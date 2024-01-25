var socket = io.connect('http://' + document.domain + ':' + location.port);
const displayMsg = document.getElementById("allMessages");

// Load messages from sessionStorage when the page loads
/*window.onload = function () {
    loadMessages();
};*/
let chatRoomID;
socket.on('sendChatID', function (data) {
    const chatRoomID = data.chat_room_id;

    // Now you can use the chat room ID in your client-side logic
    console.log('Received Chat Room ID:', chatRoomID);
    //loadMessages();
});

socket.on('message', function (data) {
    if (data.room === chatRoomID) {
    createMessage(data.name, data.message, data.time);
    // Save the message to sessionStorage
    //saveMessageToSessionStorage(data.name, data.message, data.time);}
    } 
});

function sendMessage() {
    var messageInput = document.getElementById("message");
    var message = messageInput.value;
    if (message.trim() !== "") {
        socket.emit('message', { message: message});
        messageInput.value = "";

        // Assuming you want to display the sent message immediately
        createMessage("You", message, getCurrentTime());

        // Save the sent message to sessionStorage
       // saveMessageToSessionStorage("You", message, getCurrentTime());
    }
}

function createMessage(name, msg, time) {
    const content =
        `<div class="text">
            <span>
                <strong>${name}</strong>: ${msg}
            </span>
            <span>${time}</span>
        </div>`
    displayMsg.innerHTML += content;
}

function getCurrentTime() {
    var now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
/*
function saveMessageToSessionStorage(name, msg, time) {
    // Retrieve existing messages from sessionStorage
    var storedMessages = JSON.parse(sessionStorage.getItem('chatMessages')) || [];

    // Add the new message
    storedMessages.push({ name: name, message: msg, time: time });

    // Save the updated messages back to sessionStorage
    sessionStorage.setItem('chatMessages', JSON.stringify(storedMessages));
}

function loadMessages() {
    // Retrieve messages from sessionStorage
    var storedMessages = JSON.parse(sessionStorage.getItem('chatMessages')) || [];

    // Display the messages on the page
    storedMessages.forEach(function (message) {
        createMessage(message.name, message.message, message.time);
    });
}*/