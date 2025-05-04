const socket = io(); // WebSocket подключение

let playerId = null;
let gameState = null;
let myColor = null;
let myTurn = false;

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
  roomId = data.room_id;
  console.log("Комната создана:", roomId);
  alert(`Комната создана! Код: ${roomId}`);
  // здесь можно отобразить выбор стартового штата
});

// Когда другой игрок присоединился
socket.on("player_joined", (data) => {
  console.log("Игроки в комнате:", data.players);
});
