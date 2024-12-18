const socket = io('https://whiteboard-backend-jzw7.onrender.com'); // Replace with your actual backend URL

// Canvas and user setup
const canvas = document.getElementById("whiteboard");
const ctx = canvas.getContext("2d");

let drawing = false; // Tracks whether the user is drawing
let username = null; // Stores the username
let color = "#000000"; // Default color
let brushSize = 4; // Default brush size
let history = []; // Drawing history for undo/redo
let redoStack = []; // Redo stack for redo functionality

// Handle login button click
document.getElementById("login-btn").addEventListener("click", () => {
    console.log("Login button clicked"); // Debug log
    username = document.getElementById("username").value; // Get username from input
    console.log("Username entered:", username); // Debug log

    if (username) {
        console.log("Redirecting to the whiteboard..."); // Debug log
        // Hide the login screen and show the whiteboard
        document.getElementById("login-screen").style.display = "none";
        document.getElementById("whiteboard-container").style.display = "block";
        document.getElementById("user-display").textContent = username;
    } else {
        alert("Please enter a username!"); // Alert if username is empty
    }
});

// Handle color picker input
document.getElementById("color-picker").addEventListener("input", (e) => {
    color = e.target.value; // Update the color
    console.log("Selected color:", color); // Debug log
});

// Handle brush size slider input
document.getElementById("brush-size").addEventListener("input", (e) => {
    brushSize = e.target.value; // Update the brush size
    console.log("Brush size changed to:", brushSize); // Debug log
});

// Start drawing
canvas.addEventListener("mousedown", () => {
    drawing = true;
    console.log("Drawing started"); // Debug log
});

// Stop drawing
canvas.addEventListener("mouseup", () => {
    drawing = false;
    console.log("Drawing stopped"); // Debug log
});

// Draw on canvas and emit events
canvas.addEventListener("mousemove", (e) => {
    if (!drawing) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const data = { x, y, color, size: brushSize, user: username };
    draw(data); // Draw locally
    socket.emit("draw_event", data); // Send the drawing data to the backend
    console.log("Drawing data emitted:", data); // Debug log
});

// Listen for draw events from the backend
socket.on("draw_event", (data) => {
    console.log("Received draw event:", data); // Debug log
    draw(data); // Draw on the canvas
});

// Function to draw on the canvas
function draw({ x, y, color, size }) {
    history.push({ x, y, color, size }); // Save to history for undo
    ctx.fillStyle = color || "#000000";
    ctx.fillRect(x, y, size || 4, size || 4);
}

// Undo functionality
document.addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.key === "z") { // Undo (Ctrl + Z)
        console.log("Undo action triggered"); // Debug log
        const lastAction = history.pop();
        if (lastAction) redoStack.push(lastAction); // Save for redo
        redrawCanvas();
    } else if (e.ctrlKey && e.key === "y") { // Redo (Ctrl + Y)
        console.log("Redo action triggered"); // Debug log
        const redoAction = redoStack.pop();
        if (redoAction) history.push(redoAction);
        redrawCanvas();
    }
});

// Redraw the canvas from history
function redrawCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas
    history.forEach((action) => draw(action)); // Redraw everything
}
