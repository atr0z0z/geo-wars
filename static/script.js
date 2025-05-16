const socket = io(); // Подключение WebSocket

let username = prompt("Введите ваше имя:");
let color = '#' + Math.floor(Math.random() * 16777215).toString(16);
let roomId = null;
let myId = null;
let myTurn = false;

// DOM элементы
const statusEl = document.getElementById("status");
const questionBox = document.getElementById("question-box");
const questionText = document.getElementById("question");
const answerButtons = document.getElementById("answers");

// Кнопка "Создать комнату"
document.getElementById("create-room-button").addEventListener("click", () => {
  console.log("Создание комнаты...");
  socket.emit("create_room", { username, color });
});

// Кнопка "Играть" (присоединиться к комнате)
document.getElementById("play-button").addEventListener("click", () => {
  const inputRoom = prompt("Введите код комнаты:");
  if (inputRoom) {
    socket.emit("join_room", { room_id: inputRoom, username, color });
  }
});

// При подключении к серверу
socket.on("connect", () => {
  console.log("Подключено к серверу.");
});

// При создании комнаты
socket.on("room_created", (data) => {
  console.log("Комната создана:", data.room_id);
  alert(`Комната создана! Код: ${data.room_id}`);
  roomId = data.room_id;

  // Показать карту, скрыть меню
  document.getElementById("start-section").style.display = "none";
  document.getElementById("game-container").style.display = "block";
});

// При подключении к комнате
socket.on("player_joined", (data) => {
  console.log("Игроки в комнате:", data.players);
  document.getElementById("start-section").style.display = "none";
  document.getElementById("game-container").style.display = "block";
});

// Получение состояния игры
socket.on("game_state", (state) => {
  myTurn = state.turn === username;
  updateMap(state.map);
  if (myTurn) {
    statusEl.textContent = "Ваш ход! Кликните на штат для атаки.";
  } else {
    statusEl.textContent = `Ходит игрок ${state.turn}`;
  }
});

// Начало атаки — показать вопрос
socket.on("attack_started", (data) => {
  showQuestion(data);
});

// Ответ принят
socket.on("attack_result", (result) => {
  alert(`Атака завершена! ${result.message}`);
  questionBox.style.display = "none";
});

// Клик по карте
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("path").forEach(path => {
    path.addEventListener("click", () => {
      if (!myTurn) return;
      const state = path.getAttribute("data-name") || path.id;
      socket.emit("start_attack", { room_id: roomId, state });
    });
  });
});

// Показываем вопрос
function showQuestion(data) {
  questionText.textContent = data.question;
  answerButtons.innerHTML = "";
  questionBox.style.display = "block";

  data.options.forEach(option => {
    const btn = document.createElement("button");
    btn.className = "answer-btn";
    btn.textContent = option;
    btn.addEventListener("click", () => {
      socket.emit("answer", { room_id: roomId, answer: option });
      questionBox.style.display = "none";
    });
    answerButtons.appendChild(btn);
  });
}

// Обновить карту по состоянию
function updateMap(mapData) {
  document.querySelectorAll("path").forEach(path => {
    const state = path.getAttribute("data-name") || path.id;
    if (mapData[state]) {
      path.style.fill = mapData[state].color;
    } else {
      path.style.fill = "#ccc";
    }
  });
}
