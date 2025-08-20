const API = "http://127.0.0.1:8000";
const gridElement = document.getElementById("grid");
const outputElement = document.getElementById("output");
const reportDialog = document.getElementById("reportDialog");
const logList = document.getElementById("logList");
let boardSize = 5;

function drawGrid(robot, size = boardSize) {
  gridElement.innerHTML = "";
  boardSize = size;
  gridElement.style.gridTemplateColumns = `repeat(${size}, 60px)`;
  gridElement.style.gridTemplateRows = `repeat(${size}, 60px)`;

  for (let row = size - 1; row >= 0; row--) {
    for (let col = 0; col < size; col++) {
      let cell = document.createElement("div");
      cell.className = "cell";

      if (robot && robot.x === col && robot.y === row) {
        cell.innerHTML = `<span class="robot">${robot.direction}</span>`;
      }

      gridElement.appendChild(cell);
    }
  }
}

// Place robot at (0,0) when page loads
async function initRobot() {
  let res = await fetch(`${API}/place`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ x: 0, y: 0 })
  });
  let data = await res.json();
  outputElement.innerText = "Robot placed at (0,0)";
  drawGrid(data.position, data.board.n);
}

async function upRobot() {
  let res = await fetch(`${API}/up`, { method: "POST" });
  let data = await res.json();
  outputElement.innerText = JSON.stringify(data.position);
  drawGrid(data.position, data.board.n);
}

async function downRobot() {
  let res = await fetch(`${API}/down`, { method: "POST" });
  let data = await res.json();
  outputElement.innerText = JSON.stringify(data.position);
  drawGrid(data.position, data.board.n);
}

async function leftRobot() {
  let res = await fetch(`${API}/left`, { method: "POST" });
  let data = await res.json();
  outputElement.innerText = JSON.stringify(data.position);
  drawGrid(data.position, data.board.n);
}

async function rightRobot() {
  let res = await fetch(`${API}/right`, { method: "POST" });
  let data = await res.json();
  outputElement.innerText = JSON.stringify(data.position);
  drawGrid(data.position, data.board.n);
}

async function reportRobot() {
  let res = await fetch(`${API}/report`);
  let data = await res.json();
  outputElement.innerText = JSON.stringify(data.position);

  logList.innerHTML = "";
  data.logs.forEach(log => {
    let li = document.createElement("li");
    li.innerText = log;
    logList.appendChild(li);
  });

  reportDialog.showModal();
}

function closeDialog() {
  reportDialog.close();
}

async function resizeBoard() {
  let size = parseInt(document.getElementById("boardSize").value);
  if (isNaN(size) || size < 5) size = 5;
  let res = await fetch(`${API}/resize/${size}`, { method: "POST" });
  let data = await res.json();
  outputElement.innerText = `Board resized to ${size}x${size}`;
  drawGrid(data.position, data.board.n);
}

// Run on page load
initRobot();