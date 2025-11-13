/**
 * Chat Manager
 * Handles real-time text chat using WebSockets
 */
class ChatManager {
    constructor(roomName, userId, userName) {
        this.roomName = roomName;
        this.userId = userId;
        this.userName = userName;
        
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendChat');
        
        this.messages = [];
        this.signalingSocket = null;
    }

    initialize() {
        if (this.sendButton) {
            this.sendButton.addEventListener('click', () => this.sendMessage());
        }

        if (this.chatInput) {
            this.chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendMessage();
                }
            });
        }

        // Get signaling socket from WebRTC manager
        if (window.webrtc && window.webrtc.signalingSocket) {
            this.signalingSocket = window.webrtc.signalingSocket;
        }
    }

    sendMessage() {
        if (!this.chatInput || !this.chatInput.value.trim()) {
            return;
        }

        const message = this.chatInput.value.trim();
        const timestamp = new Date().toLocaleTimeString();

        // Add to local chat
        this.addMessage(this.userName, message, timestamp, true);

        // Send to other user
        if (this.signalingSocket && this.signalingSocket.readyState === WebSocket.OPEN) {
            this.signalingSocket.send(JSON.stringify({
                type: 'chat_message',
                message: message,
                timestamp: timestamp
            }));
        }

        // Clear input
        this.chatInput.value = '';
        this.chatInput.focus();
    }

    addMessage(sender, message, timestamp, isOwn = false) {
        if (!this.chatMessages) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${isOwn ? 'own' : ''}`;

        const senderSpan = document.createElement('div');
        senderSpan.className = 'chat-message-sender';
        senderSpan.textContent = sender;

        const textSpan = document.createElement('div');
        textSpan.className = 'chat-message-text';
        textSpan.textContent = message;

        const timeSpan = document.createElement('div');
        timeSpan.className = 'chat-message-time';
        timeSpan.textContent = timestamp;

        messageDiv.appendChild(senderSpan);
        messageDiv.appendChild(textSpan);
        messageDiv.appendChild(timeSpan);

        this.chatMessages.appendChild(messageDiv);

        // Auto-scroll to bottom
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;

        // Store message
        this.messages.push({
            sender: sender,
            message: message,
            timestamp: timestamp,
            isOwn: isOwn
        });
    }

    handleRemoteMessage(data) {
        const timestamp = data.timestamp || new Date().toLocaleTimeString();
        this.addMessage(data.sender, data.message, timestamp, false);
    }

    getTranscript() {
        return this.messages.map(msg => 
            `[${msg.timestamp}] ${msg.sender}: ${msg.message}`
        ).join('\n');
    }

    clearChat() {
        if (this.chatMessages) {
            this.chatMessages.innerHTML = '';
        }
        this.messages = [];
    }
}
