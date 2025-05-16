const socket = io(); // Подключение WebSocket

let playerId = null;
let gameState = null;
let myTurn = false;
let username = prompt("Введите ваше имя:");
let color = '#' + Math.floor(Math.random() * 16777215).toString(16);
let roomId = null;


const socket = io(); // Подключение WebSocket

let username = prompt("Введите ваше имя: ");
let color = '#' + Math.floor(Math.random() * 16777215).toString(16);
document.getElementById("create-room-button").addEventListener("click", () => {
  console.log("Нажата кнопка создать комнату");
  socket.emit("create_room", { username, color });
});

document.addEventListener("DOMContentLoaded", () => {


    const statusEl = document.getElementById("status");
    const questionBox = document.getElementById("question-box");
    const questionText = document.getElementById("question");
    const answerButtons = document.getElementById("answers");

    // 1. Подключение
    socket.on("connect", () => {
        console.log("Подключено к серверу.");
    });

    // 2. Присвоение игрока
    socket.on("player_data", (data) => {
        myId = data.id;
        console.log("Мой ID:", myId);
    });

    // 3. Получение состояния игры
    socket.on("game_state", (state) => {
        currentState = state;
        updateMap(state.claimedStates, state.players);
        myTurn = state.currentTurn === myId;

        if (myTurn) {
            statusEl.textContent = "Ваш ход! Кликните на штат для атаки.";
        } else {
            const current = state.players[state.currentTurn];
            statusEl.textContent = `Ходит игрок ${current?.name || "..."}`;
        }
    });

    // 4. Атака началась — показать вопрос
    socket.on("attack_started", (data) => {
        showQuestion(data);
    });

    // 5. Атака завершена
    socket.on("attack_result", (result) => {
        alert(`Атака завершена! ${result.message}`);
        questionBox.style.display = "none";
    });

    // 6. Клик по карте
    document.querySelectorAll("path").forEach(path => {
        path.addEventListener("click", () => {
            if (!myTurn) return;
            const stateName = path.getAttribute("data-name") || path.id;
            socket.emit("start_attack", { state: stateName });
        });
    });

    // 7. Показ вопроса
    function showQuestion(data) {
        questionText.textContent = data.question;
        answerButtons.innerHTML = "";
        questionBox.style.display = "block";

        data.options.forEach(option => {
            const btn = document.createElement("button");
            btn.textContent = option;
            btn.addEventListener("click", () => {
                socket.emit("answer", { answer: option });
                questionBox.style.display = "none";
            });
            answerButtons.appendChild(btn);
        });
    }

    // 8. Обновить карту
    function updateMap(claimedStates, players) {
        document.querySelectorAll("path").forEach(path => {
            const stateName = path.getAttribute("data-name") || path.id;
            const ownerId = claimedStates[stateName];
            if (ownerId && players[ownerId]) {
                const color = players[ownerId].color;
                path.style.fill = color;
            } else {
                path.style.fill = "#ccc";
            }
        });
    }
});

// Подключение к WebSocket серверу
const socket = io();
socket.on("connect", () => {
    console.log("Connected to server");
});
socket.on("player_data", (data) => {
    playerId = data.playerId;
    myColor = data.color;
    console.log("Мой ID:", playerId, "Мой цвет:", myColor);
});
socket.on("game_state", (state) => {
    gameState = state;
    myTurn = state.currentTurn === playerId;
    updateMap(); // функция обновления карты
});
socket.on("game_state", (state) => {
    console.log("Обновлённое состояние:", state);
    // Тут обновим карту, текущего игрока, захваченные штаты и т.д.
});



// Данные игрока
let username = prompt("Введите ваше имя:");
let color = '#' + Math.floor(Math.random()*16777215).toString(16);  // случайный цвет
let roomId = null;

// Кнопка "Создать комнату"
document.getElementById("create-room-button").addEventListener("click", () => {
  socket.emit("create_room", { username, color });
});


// Кнопка "Играть" (позже будем использовать для присоединения)
document.getElementById("play-button").addEventListener("click", () => {
  const inputRoom = prompt("Введите код комнаты:");
  if (inputRoom) {
    socket.emit("join_room", { room_id: inputRoom, username, color });
  }
});

// Получение подтверждения создания комнаты
socket.on("room_created", (data) => {
  console.log("Комната создана:", data.room_id);
  alert(`Комната создана! Код: ${data.room_id}`);
  roomId = data.room_id;

  // Показать карту, скрыть старт
  document.getElementById("start-section").style.display = "none";
  document.getElementById("game-container").style.display = "block";
});



// Когда другой игрок присоединился
socket.on("player_joined", (data) => {
  console.log("Игроки в комнате:", data.players);
});
