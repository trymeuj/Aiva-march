// Generate a random session ID
const sessionId = Math.random().toString(36).substring(2, 15);

// DOM elements
const chatContainer = document.getElementById('chat-container');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const statusIndicator = document.getElementById('status-indicator');
const connectionText = document.getElementById('connection-text');

// WebSocket connection
let socket;
let isConnected = false;

// Connect to WebSocket
function connectWebSocket() {
    // Determine WebSocket URL based on current location
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/${sessionId}`;
    
    socket = new WebSocket(wsUrl);
    
    socket.onopen = () => {
        console.log('Connected to server');
        isConnected = true;
        statusIndicator.classList.remove('disconnected');
        statusIndicator.classList.add('connected');
        connectionText.textContent = 'Connected';
        messageInput.disabled = false;
        sendButton.disabled = false;
    };
    
    socket.onmessage = (event) => {
        try {
            const response = JSON.parse(event.data);
            addMessage('assistant', response.text, response.context);
        } catch (error) {
            console.error('Error parsing response:', error);
            addMessage('assistant', 'Sorry, there was an error processing the response.');
        }
    };
    
    socket.onclose = () => {
        console.log('Disconnected from server');
        isConnected = false;
        statusIndicator.classList.remove('connected');
        statusIndicator.classList.add('disconnected');
        connectionText.textContent = 'Disconnected';
        messageInput.disabled = true;
        sendButton.disabled = true;
        
        // Try to reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
    };
    
    socket.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}

// Add message to chat
function addMessage(role, content, context) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', role);
    
    // Create message content element
    const contentElement = document.createElement('div');
    contentElement.classList.add('message-content');
    contentElement.textContent = content;
    messageElement.appendChild(contentElement);
    
    // If we have execution plan context, display it
    if (context && context.execution_plan) {
        const planElement = document.createElement('div');
        planElement.classList.add('execution-plan');
        
        const planTitle = document.createElement('h4');
        planTitle.textContent = 'Execution Plan';
        planElement.appendChild(planTitle);
        
        const planContent = document.createElement('pre');
        planContent.textContent = JSON.stringify(context.execution_plan, null, 2);
        planElement.appendChild(planContent);
        
        messageElement.appendChild(planElement);
    }
    
    chatContainer.appendChild(messageElement);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Send message
function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || !isConnected) return;
    
    // Add user message to chat
    addMessage('user', message);
    
    // Send to server
    socket.send(JSON.stringify({ text: message }));
    
    // Clear input
    messageInput.value = '';
}

// Event listeners
sendButton.addEventListener('click', sendMessage);

messageInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

// Add welcome message
window.addEventListener('DOMContentLoaded', () => {
    addMessage('assistant', 'Hello! I\'m your AI API Assistant. How can I help you today?');
});

// Initial connection
connectWebSocket();