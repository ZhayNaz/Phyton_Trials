#!/usr/bin/env python3
"""
process_logs.py

Streams large log files, extracts calls to /old/endpointXX/ and /new/endpointXX/,
parses username, datetime, ip, endpoint (parameters stripped), and call parameters.
Saves results into SQLite database and produces a CSV report:
 username, date, endpoint, number_of_calls

Usage:
  python process_logs.py /path/to/log1 /path/to/log2 --db processed_calls.db --report report.csv

Notes & heuristics (because log format isn't provided):
 - Endpoints are detected by regex looking for '/old/endpoint\d{2}' or '/new/endpoint\d{2}'.
 - Endpoint stripping:
     * Path is split into segments. Segments that are ALL-UPPERCASE (A-Z, length 1-6) are treated as an unnamed 'ticker' parameter and removed from endpoint.
     * A segment 'top' is considered part of endpoint (per example), so kept.
     * Everything up to the first uppercase-only segment (treated as ticker) is considered part of endpoint.
     * Trailing slash normalized: endpoint always ends with '/'
 - Query parameters after '?' are parsed into key=value pairs. Parameters without '=' become keys with empty value.
 - Username is searched by looking for tokens like user=, username=, "user": "..." or email-like substring. Fallback to 'unknown'.
 - Datetime: several common timestamp patterns attempted (ISO 8601, Apache-style, RFC-ish). Stored in DB as ISO-8601 text.
 - IP: first IPv4-like found in line is used.
 - Multi-line calls: If the same (username, ip, endpoint) pair appears with timestamps within a short window (default 30s), multiple lines are merged into a single call, aggregating parameters. This is a heuristic to handle calls split across lines.
 - Performance: file streaming, batch DB inserts, indexes on call table for report.

Author: ChatGPT
"""

import argparse
import os
import re
import sqlite3
import sys
import csv
import time
from datetime import datetime, timedelta
from collections import defaultdict, deque

# ---------------------------
# Configurable heuristics
# ---------------------------
MERGE_WINDOW_SECONDS = 30  # lines within this window for same (user, ip, endpoint) are merged into same call
DB_BATCH_SIZE = 1000       # insert per batch
# ---------------------------

# Regexes
RE_ENDPOINT = re.compile(r'/(?:old|new)/endpoint\d{1,3}(?:/[^?\s"]*)*')  # find candidate path
RE_IPV4 = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
RE_USER_KV = re.compile(r'(?:user(?:name)?|usr|u)=["\']?([A-Za-z0-9_.@+-]+)["\']?', re.IGNORECASE)
RE_USER_JSON = re.compile(r'["\']user(?:name)?["\']\s*:\s*["\']([^"\']+)["\']', re.IGNORECASE)
RE_EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
# Several timestamp patterns
RE_ISO = re.compile(r'\b(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+\-]\d{2}:?\d{2})?)\b')
RE_DATETIME_SPACE = re.compile(r'\b(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\b')
RE_APACHE = re.compile(r'\b(\d{2}/[A-Za-z]{3}/\d{4}:\d{2}:\d{2}:\d{2})')  # 10/Oct/2000:13:55:36
RE_SIMPLE = re.compile(r'\b(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})\b')

# helpers
def find_first_ip(line):
    m = RE_IPV4.search(line)
    return m.group(0) if m else None

def find_username(line):
    m = RE_USER_KV.search(line)
    if m:
        return m.group(1)
    m = RE_USER_JSON.search(line)
    if m:
        return m.group(1)
    m = RE_EMAIL.search(line)
    if m:
        return m.group(0)
    return None

def parse_timestamp(line):
    # Try patterns in order. Return ISO8601 string (UTC naive) or None
    m = RE_ISO.search(line)
    if m:
        try:
            # normalize so we keep it as-is (ISO)
            return m.group(1)
        except Exception:
            pass
    m = RE_DATETIME_SPACE.search(line)
    if m:
        return m.group(1)
    m = RE_APACHE.search(line)
    if m:
        # convert '10/Oct/2000:13:55:36' -> '2000-10-10 13:55:36'
        try:
            dt = datetime.strptime(m.group(1), '%d/%b/%Y:%H:%M:%S')
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            pass
    m = RE_SIMPLE.search(line)
    if m:
        return m.group(1)
    return None

def parse_query_params(qs):
    # qs: string after '?', may contain & separated key=val pairs or lone tokens
    params = {}
    if not qs:
        return params
    # strip fragments
    qs = qs.split('#', 1)[0]
    for pair in qs.split('&'):
        if not pair:
            continue
        if '=' in pair:
            k, v = pair.split('=', 1)
            params[k.strip()] = v.strip()
        else:
            params[pair.strip()] = ''
    return params

def normalize_endpoint_and_params(raw_path):
    """
    Given a raw path (e.g. '/new/endpoint05/ARKK/top?date=current'),
    return (endpoint, params_dict)

    Heuristics per task description:
     - endpoint should end with a slash, e.g. '/new/endpoint05/top/'
     - 'ARKK' (all-uppercase token) is treated as an unnamed ticker param -> parameter name 'ticker'
     - query string parsed to parameters
    """
    # split path and query
    if '?' in raw_path:
        path_part, query_part = raw_path.split('?', 1)
    else:
        path_part, query_part = raw_path, ''
    # ensure leading slash
    if not path_part.startswith('/'):
        path_part = '/' + path_part
    # split into segments (without empty segments)
    segs = [s for s in path_part.split('/') if s != '']
    # find the index of 'old' or 'new' followed by endpoint###
    endpoint_idx = None
    for i in range(len(segs)-1):
        if segs[i] in ('old', 'new') and segs[i+1].startswith('endpoint'):
            endpoint_idx = i
            break
    if endpoint_idx is None:
        # fallback: try to find first seg starting with endpoint
        for i, s in enumerate(segs):
            if s.startswith('endpoint'):
                endpoint_idx = max(0, i-1)
                break
    if endpoint_idx is None:
        # give up — return path_part as endpoint (strip params)
        endpoint = path_part
        if not endpoint.endswith('/'):
            endpoint += '/'
        params = parse_query_params(query_part)
        return endpoint, params

    # Build endpoint segments until encountering an ALL-UPPERCASE token (ticker) which we treat as a param
    endpoint_segments = []
    ticker_value = None
    i = endpoint_idx
    while i < len(segs):
        seg = segs[i]
        # if uppercase-only (A-Z) and length reasonable, treat as ticker param and stop
        if seg.isalpha() and seg.isupper() and 1 <= len(seg) <= 6:
            ticker_value = seg
            i += 1
            break
        # else keep as endpoint part
        endpoint_segments.append(seg)
        i += 1
    # Join back
    endpoint = '/' + '/'.join(endpoint_segments) + '/'
    # parse query params
    params = parse_query_params(query_part)
    if ticker_value:
        # only add ticker if not already specified in params
        if 'ticker' not in params:
            params['ticker'] = ticker_value
    return endpoint, params

# ---------------------------
# DB functions
# ---------------------------
CREATE_CALL_TABLE = """
CREATE TABLE IF NOT EXISTS call (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    date_of_call TEXT,   -- stored as ISO8601 or 'YYYY-MM-DD HH:MM:SS'
    ip_address TEXT,
    endpoint TEXT
);
"""

CREATE_CALL_PARAMS_TABLE = """
CREATE TABLE IF NOT EXISTS call_parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    call_id INTEGER,
    parameter_name TEXT,
    parameter_value TEXT,
    FOREIGN KEY(call_id) REFERENCES call(ID)
);
"""

CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_call_user_date_endpoint ON call(username, date_of_call, endpoint);",
    "CREATE INDEX IF NOT EXISTS idx_call_date ON call(date_of_call);"
]

def init_db(conn):
    cur = conn.cursor()
    cur.execute(CREATE_CALL_TABLE)
    cur.execute(CREATE_CALL_PARAMS_TABLE)
    for s in CREATE_INDEXES:
        cur.execute(s)
    conn.commit()

# ---------------------------
# Processing logic
# ---------------------------
class CallBufferItem:
    def __init__(self, username, ip, endpoint, timestamp_text):
        self.username = username
        self.ip = ip
        self.endpoint = endpoint
        self.params = {}  # aggregated parameters
        self.first_seen = timestamp_text
        self.last_seen = timestamp_text

    def merge(self, other_ts_text, other_params):
        # update last_seen, merge params (existing keys keep first-seen value)
        self.last_seen = other_ts_text or self.last_seen
        for k, v in other_params.items():
            if k not in self.params:
                self.params[k] = v

def process_files(paths, db_path, report_csv_path):
    # Open DB
    conn = sqlite3.connect(db_path)
    init_db(conn)
    cur = conn.cursor()

    # Buffer for merging multi-line calls.
    # key -> CallBufferItem
    open_calls = {}

    # For batching DB inserts
    calls_to_insert = []
    params_to_insert = []

    def flush_call_buffer_if_old(cutoff_dt):
        # flush entries whose last_seen < cutoff_dt (ISO string compare is okay if format consistent)
        nonlocal open_calls, calls_to_insert, params_to_insert
        to_delete = []
        for key, item in list(open_calls.items()):
            # last_seen stored as text; try parse to datetime or compare using fallback
            try:
                last_dt = parse_iso_to_dt(item.last_seen)
            except Exception:
                # if cannot parse, flush anyway if it's older than cutoff by comparing strings
                last_dt = None
            if last_dt is not None:
                if last_dt < cutoff_dt:
                    # flush
                    calls_to_insert.append((item.username or 'unknown', item.first_seen, item.ip or '', item.endpoint))
                    # index is temporary, we'll assign call_id after insertion
                    idx = len(calls_to_insert) - 1
                    for pname, pval in item.params.items():
                        params_to_insert.append((idx, pname, pval))
                    to_delete.append(key)
            else:
                # if we can't compare, don't flush
                pass
        for k in to_delete:
            open_calls.pop(k, None)

    # Walk files list and yield lines
    def iter_lines_from_paths(paths):
        for p in paths:
            if os.path.isdir(p):
                for fname in sorted(os.listdir(p)):
                    fpath = os.path.join(p, fname)
                    if os.path.isfile(fpath):
                        yield from iter_lines_from_file(fpath)
            elif os.path.isfile(p):
                yield from iter_lines_from_file(p)
            else:
                print(f"Warning: {p} is not a file or directory, skipping.", file=sys.stderr)

    def iter_lines_from_file(path):
        with open(path, 'r', errors='ignore') as fh:
            for line in fh:
                yield line

    def insert_batches():
        nonlocal calls_to_insert, params_to_insert
        if not calls_to_insert:
            return
        # Insert calls (we'll get inserted rowids to map params)
        cur.executemany("INSERT INTO call (username, date_of_call, ip_address, endpoint) VALUES (?, ?, ?, ?);", calls_to_insert)
        conn.commit()
        # get last N rowids
        last_rowid = cur.lastrowid
        first_rowid = last_rowid - len(calls_to_insert) + 1
        # map idx to real call_id
        callid_map = {}
        for idx in range(len(calls_to_insert)):
            callid_map[idx] = first_rowid + idx
        # prepare params insertion using real call ids
        params_values = []
        for idx, name, val in params_to_insert:
            real_call_id = callid_map.get(idx)
            if real_call_id:
                params_values.append((real_call_id, name, val))
        if params_values:
            cur.executemany("INSERT INTO call_parameters (call_id, parameter_name, parameter_value) VALUES (?, ?, ?);", params_values)
        conn.commit()
        calls_to_insert = []
        params_to_insert = []

    # process streaming
    processed_lines = 0
    last_flush_time = datetime.utcnow()
    for line in iter_lines_from_paths(paths):
        processed_lines += 1
        # quick find endpoints
        m = RE_ENDPOINT.search(line)
        if not m:
            # still maybe this line contains username/ip/timestamp for merging — try extracting and merge
            # but skip unless it has an endpoint elsewhere
            continue
        raw_path = m.group(0)
        endpoint, params = normalize_endpoint_and_params(raw_path)
        username = find_username(line) or 'unknown'
        ip = find_first_ip(line) or ''
        timestamp_text = parse_timestamp(line) or datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        # Attach query params parsed from path and params collected
        merged_params = dict(params)  # shallow copy

        # Create key for merging
        key = (username, ip, endpoint)

        # merge behavior
        existing = open_calls.get(key)
        if existing:
            # check time difference
            try:
                last_dt = parse_iso_to_dt(existing.last_seen)
                curr_dt = parse_iso_to_dt(timestamp_text)
                if curr_dt is None:
                    # if cannot parse current ts, just update last_seen
                    existing.merge(timestamp_text, merged_params)
                else:
                    if (curr_dt - last_dt).total_seconds() <= MERGE_WINDOW_SECONDS:
                        existing.merge(timestamp_text, merged_params)
                    else:
                        # flush existing into DB and replace
                        # append to calls_to_insert and params_to_insert
                        calls_to_insert.append((existing.username or 'unknown', existing.first_seen, existing.ip or '', existing.endpoint))
                        idx = len(calls_to_insert) - 1
                        for pname, pval in existing.params.items():
                            params_to_insert.append((idx, pname, pval))
                        # replace with new item
                        open_calls[key] = CallBufferItem(username, ip, endpoint, timestamp_text)
                        open_calls[key].params.update(merged_params)
            except Exception:
                # fallback: just merge
                existing.merge(timestamp_text, merged_params)
        else:
            item = CallBufferItem(username, ip, endpoint, timestamp_text)
            item.params.update(merged_params)
            open_calls[key] = item

        # Periodically flush buffer items older than MERGE_WINDOW_SECONDS
        if processed_lines % 1000 == 0:
            cutoff = datetime.utcnow() - timedelta(seconds=MERGE_WINDOW_SECONDS)
            flush_call_buffer_if_old(cutoff)

        # Periodically insert batches to DB
        if len(calls_to_insert) >= DB_BATCH_SIZE:
            insert_batches()

    # After loop, flush all remaining open_calls
    for key, item in open_calls.items():
        calls_to_insert.append((item.username or 'unknown', item.first_seen, item.ip or '', item.endpoint))
        idx = len(calls_to_insert) - 1
        for pname, pval in item.params.items():
            params_to_insert.append((idx, pname, pval))
    open_calls.clear()
    # final insert
    insert_batches()

    # Generate report: username, date, endpoint, number_of_calls (date derived from date_of_call)
    # We'll try to extract date portion (YYYY-MM-DD) from date_of_call strings
    # Using SQL substr to get first 10 characters is sufficient for ISO-like forms
    with open(report_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['username', 'date', 'endpoint', 'number_of_calls'])
        q = """
        SELECT username, substr(date_of_call,1,10) as date, endpoint, COUNT(*) as cnt
        FROM call
        GROUP BY username, date, endpoint
        ORDER BY username, date, endpoint;
        """
        for row in cur.execute(q):
            writer.writerow(row)

    conn.close()
    print(f"Done. Processed approx {processed_lines} lines. Report saved to {report_csv_path} and DB to {db_path}.")

# utility to parse ISO-like into datetime object (best-effort)
def parse_iso_to_dt(text):
    if not text:
        return None
    # Try several patterns
    for fmt in ('%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%S.%f%z',
                '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S',
                '%Y/%m/%d %H:%M:%S'):
        try:
            # Handle naive timezoneless strings
            if fmt.endswith('%z') and (text.endswith('Z') or ('+' in text or '-' in text[10:])):
                # normalize Z -> +0000
                t = text.replace('Z', '+0000')
                # remove colon in offset if exists like +02:00 -> +0200
                t = re.sub(r'([+\-]\d{2}):(\d{2})$', r'\1\2', t)
                return datetime.strptime(t, fmt)
            else:
                return datetime.strptime(text, fmt)
        except Exception:
            continue
    # Try apache style
    try:
        if RE_APACHE.search(text):
            m = RE_APACHE.search(text).group(1)
            dt = datetime.strptime(m, '%d/%b/%Y:%H:%M:%S')
            return dt
    except Exception:
        pass
    return None

# ---------------------------
# Unit tests for parsing helpers
# ---------------------------
import unittest

class TestParsingLogic(unittest.TestCase):
    def test_normalize_simple(self):
        e, p = normalize_endpoint_and_params('/new/endpoint10/')
        self.assertEqual(e, '/new/endpoint10/')
        self.assertEqual(p, {})

    def test_normalize_with_query(self):
        e, p = normalize_endpoint_and_params('/new/endpoint09/CFO?date=current')
        self.assertEqual(e, '/new/endpoint09/')
        self.assertEqual(p.get('ticker'), 'CFO')
        self.assertEqual(p.get('date'), 'current')

    def test_normalize_top_included(self):
        e, p = normalize_endpoint_and_params('/new/endpoint05/ARKK/top?date=current')
        self.assertEqual(e, '/new/endpoint05/top/')
        self.assertEqual(p.get('ticker'), 'ARKK')
        self.assertEqual(p.get('date'), 'current')

    def test_username_email(self):
        s = '... user=someone@example.com ...'
        self.assertEqual(find_username(s), 'someone@example.com')

    def test_username_kv(self):
        s = 'foo user=joe.bar ip=1.2.3.4'
        self.assertEqual(find_username(s), 'joe.bar')

    def test_ip(self):
        s = 'client 10.20.30.40 connected'
        self.assertEqual(find_first_ip(s), '10.20.30.40')

    def test_parse_query_params(self):
        qs = 'a=1&b=two&flag'
        p = parse_query_params(qs)
        self.assertEqual(p['a'], '1')
        self.assertEqual(p['b'], 'two')
        self.assertEqual(p['flag'], '')

# ---------------------------
# CLI
# ---------------------------
def main():
    parser = argparse.ArgumentParser(description="Process large log files to extract calls to /old|/new endpointXX")
    parser.add_argument('paths', nargs='*', help='files or directories to process')
    parser.add_argument('--db', default='processed_calls.db', help='sqlite db path')
    parser.add_argument('--report', default='calls_report.csv', help='output CSV report path')
    parser.add_argument('--run-tests', action='store_true', help='run unit tests and exit')
    args = parser.parse_args()
    if args.run_tests:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestParsingLogic)
        runner = unittest.TextTestRunner()
        res = runner.run(suite)
        sys.exit(0 if res.wasSuccessful() else 2)
    if not args.paths:
        print("Please provide at least one file or directory to process.", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    start = time.time()
    process_files(args.paths, args.db, args.report)
    end = time.time()
    print(f"Total time: {end-start:.2f} seconds")

if __name__ == '__main__':
    main()
