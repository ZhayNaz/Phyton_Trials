from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
def read_index():
    return FileResponse("static/index.html")

class RobotPosition(BaseModel):
    x: int
    y: int

robot = {"x": None, "y": None, "direction": "⬆️"}
logs = []
board_size = {"n": 5} 

def add_log(action: str):
    logs.append(f"{action} -> Position: ({robot['x']}, {robot['y']})")

@app.post("/place")
def place_robot(pos: RobotPosition):
    global robot
    robot["x"], robot["y"] = pos.x, pos.y
    robot["direction"] = "⬆️"
    add_log("Placed Robot")
    return {"position": robot, "board": board_size}

@app.post("/up")
def move_up():
    global robot
    if robot["y"] < board_size["n"] - 1:
        robot["y"] += 1
    robot["direction"] = "⬆️"
    add_log("Move Up")
    return {"position": robot, "board": board_size}

@app.post("/down")
def move_down():
    global robot
    if robot["y"] > 0:
        robot["y"] -= 1
    robot["direction"] = "⬇️"
    add_log("Move Down")
    return {"position": robot, "board": board_size}

@app.post("/left")
def move_left():
    global robot
    if robot["x"] > 0:
        robot["x"] -= 1
    robot["direction"] = "⬅️"
    add_log("Move Left")
    return {"position": robot, "board": board_size}

@app.post("/right")
def move_right():
    global robot
    if robot["x"] < board_size["n"] - 1:
        robot["x"] += 1
    robot["direction"] = "➡️"
    add_log("Move Right")
    return {"position": robot, "board": board_size}

@app.get("/report")
def report_robot():
    return {"position": robot, "logs": logs, "board": board_size}

@app.post("/resize/{n}")
def resize_board(n: int):
    global board_size, robot
    if n < 5:
        n = 5
    board_size["n"] = n
    robot["x"], robot["y"] = 0, 0
    robot["direction"] = "⬆️"
    add_log(f"Resized board to {n}x{n}")
    return {"position": robot, "board": board_size}
