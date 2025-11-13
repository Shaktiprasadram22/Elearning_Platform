// WebRTC Configuration with STUN servers
const configuration = {
  iceServers: [
    { urls: "stun:stun.l.google.com:19302" },
    { urls: "stun:stun1.l.google.com:19302" },
    { urls: "stun:stun2.l.google.com:19302" },
  ],
};

// Global variables
let localStream = null;
let remoteStream = null;
let peerConnection = null;
let websocket = null;
let chatLog = [];

// DOM elements
const localVideo = document.getElementById("localVideo");
const remoteVideo = document.getElementById("remoteVideo");
const startButton = document.getElementById("startButton");
const endButton = document.getElementById("endButton");
const chatInput = document.getElementById("chatInput");
const sendButton = document.getElementById("sendButton");
const chatMessages = document.getElementById("chatMessages");

// Get room and user info from template
const roomName = document.getElementById("room-name").value;
const userId = document.getElementById("user-id").value;
const userRole = document.getElementById("user-role").value;
const username = document.getElementById("username").value;

// Initialize WebSocket connection
function initWebSocket() {
  const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${wsProtocol}//${window.location.host}/ws/session/${roomName}/`;

  websocket = new WebSocket(wsUrl);

  websocket.onopen = () => {
    console.log("WebSocket connected");
    addSystemMessage("✅ Connected to session");
  };

  websocket.onmessage = async (event) => {
    const data = JSON.parse(event.data);
    await handleWebSocketMessage(data);
  };

  websocket.onerror = (error) => {
    console.error("WebSocket error:", error);
    addSystemMessage("❌ Connection error occurred");
  };

  websocket.onclose = () => {
    console.log("WebSocket closed");
    addSystemMessage("⚠️ Disconnected from session");
  };
}

// Handle incoming WebSocket messages
async function handleWebSocketMessage(data) {
  console.log("Received message:", data.type);

  switch (data.type) {
    case "user_joined":
      addSystemMessage(`👤 ${data.username} joined the session`);
      break;

    case "user_left":
      addSystemMessage(`👋 ${data.username} left the session`);
      break;

    case "offer":
      if (data.sender_id != userId) {
        await handleOffer(data.offer);
      }
      break;

    case "answer":
      if (data.sender_id != userId) {
        await handleAnswer(data.answer);
      }
      break;

    case "ice_candidate":
      if (data.sender_id != userId) {
        await handleIceCandidate(data.candidate);
      }
      break;

    case "chat_message":
      displayChatMessage(data.sender, data.message, data.timestamp);
      break;

    case "session_accept":
      addSystemMessage(`✅ ${data.instructor_name} accepted the session`);
      break;

    case "session_end":
      addSystemMessage("🔚 Session ended");
      endCall();
      break;
  }
}

// Start video call
async function startCall() {
  try {
    // Get local media stream (video + audio)
    localStream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
      },
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
    });

    localVideo.srcObject = localStream;

    // Create peer connection
    createPeerConnection();

    // Add local stream tracks to peer connection
    localStream.getTracks().forEach((track) => {
      peerConnection.addTrack(track, localStream);
    });

    // Create and send offer
    const offer = await peerConnection.createOffer({
      offerToReceiveVideo: true,
      offerToReceiveAudio: true,
    });
    await peerConnection.setLocalDescription(offer);

    websocket.send(
      JSON.stringify({
        type: "offer",
        offer: offer,
      })
    );

    startButton.disabled = true;
    endButton.disabled = false;
    addSystemMessage("📞 Call started, waiting for peer...");
  } catch (error) {
    console.error("Error starting call:", error);
    alert(
      "❌ Failed to start call. Please check camera/microphone permissions."
    );
  }
}

// Create RTCPeerConnection
function createPeerConnection() {
  peerConnection = new RTCPeerConnection(configuration);

  // Handle ICE candidates
  peerConnection.onicecandidate = (event) => {
    if (event.candidate) {
      websocket.send(
        JSON.stringify({
          type: "ice_candidate",
          candidate: event.candidate,
        })
      );
    }
  };

  // Handle remote stream
  peerConnection.ontrack = (event) => {
    console.log("Received remote track");
    if (!remoteStream) {
      remoteStream = new MediaStream();
      remoteVideo.srcObject = remoteStream;
    }
    remoteStream.addTrack(event.track);
  };

  // Handle connection state changes
  peerConnection.onconnectionstatechange = () => {
    console.log("Connection state:", peerConnection.connectionState);

    if (peerConnection.connectionState === "connected") {
      addSystemMessage("✅ Peer connected successfully");
    } else if (peerConnection.connectionState === "disconnected") {
      addSystemMessage("⚠️ Peer disconnected");
    } else if (peerConnection.connectionState === "failed") {
      addSystemMessage("❌ Connection failed");
      endCall();
    }
  };

  // Handle ICE connection state
  peerConnection.oniceconnectionstatechange = () => {
    console.log("ICE connection state:", peerConnection.iceConnectionState);
  };
}

// Handle incoming offer
async function handleOffer(offer) {
  try {
    if (!peerConnection) {
      // Get local media stream first
      localStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });
      localVideo.srcObject = localStream;

      createPeerConnection();

      localStream.getTracks().forEach((track) => {
        peerConnection.addTrack(track, localStream);
      });

      startButton.disabled = true;
      endButton.disabled = false;
    }

    await peerConnection.setRemoteDescription(new RTCSessionDescription(offer));

    const answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);

    websocket.send(
      JSON.stringify({
        type: "answer",
        answer: answer,
      })
    );

    addSystemMessage("📞 Answering call...");
  } catch (error) {
    console.error("Error handling offer:", error);
  }
}

// Handle incoming answer
async function handleAnswer(answer) {
  try {
    await peerConnection.setRemoteDescription(
      new RTCSessionDescription(answer)
    );
    addSystemMessage("✅ Call connected!");
  } catch (error) {
    console.error("Error handling answer:", error);
  }
}

// Handle incoming ICE candidate
async function handleIceCandidate(candidate) {
  try {
    if (peerConnection) {
      await peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
    }
  } catch (error) {
    console.error("Error adding ICE candidate:", error);
  }
}

// End call
function endCall() {
  // Stop local stream
  if (localStream) {
    localStream.getTracks().forEach((track) => {
      track.stop();
    });
    localStream = null;
  }

  // Close peer connection
  if (peerConnection) {
    peerConnection.close();
    peerConnection = null;
  }

  // Clear video elements
  localVideo.srcObject = null;
  remoteVideo.srcObject = null;
  remoteStream = null;

  // Send session end message with chat log
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    websocket.send(
      JSON.stringify({
        type: "session_end",
        chat_log: chatLog,
      })
    );
  }

  startButton.disabled = false;
  endButton.disabled = true;
  addSystemMessage("🔚 Call ended");
}

// Send chat message
function sendChatMessage() {
  const message = chatInput.value.trim();
  if (message && websocket && websocket.readyState === WebSocket.OPEN) {
    const timestamp = new Date().toISOString();
    websocket.send(
      JSON.stringify({
        type: "chat_message",
        message: message,
        timestamp: timestamp,
      })
    );
    chatInput.value = "";
  }
}

// Display chat message
function displayChatMessage(sender, message, timestamp) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("chat-message");

  const senderSpan = document.createElement("strong");
  senderSpan.textContent = sender + ": ";

  const messageSpan = document.createElement("span");
  messageSpan.textContent = message;

  const timeSpan = document.createElement("small");
  timeSpan.className = "text-muted d-block";
  timeSpan.textContent = new Date(timestamp).toLocaleTimeString();

  messageDiv.appendChild(senderSpan);
  messageDiv.appendChild(messageSpan);
  messageDiv.appendChild(timeSpan);

  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  // Add to chat log
  chatLog.push({
    sender: sender,
    message: message,
    timestamp: timestamp,
  });
}

// Add system message
function addSystemMessage(message) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("system-message");
  messageDiv.textContent = message;
  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Event listeners
startButton.addEventListener("click", startCall);
endButton.addEventListener("click", endCall);
sendButton.addEventListener("click", sendChatMessage);

chatInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    sendChatMessage();
  }
});

// Initialize WebSocket on page load
window.addEventListener("load", () => {
  initWebSocket();
  addSystemMessage("🎉 Welcome to the live session room!");
});

// Cleanup on page unload
window.addEventListener("beforeunload", () => {
  endCall();
  if (websocket) {
    websocket.close();
  }
});

// Prevent accidental page close during active call
window.addEventListener("beforeunload", (e) => {
  if (peerConnection && peerConnection.connectionState === "connected") {
    e.preventDefault();
    e.returnValue = "";
  }
});
