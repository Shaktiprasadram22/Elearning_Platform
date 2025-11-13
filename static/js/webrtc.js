/**
 * WebRTC Manager
 * Handles P2P video/audio communication using WebRTC
 */
class WebRTCManager {
    constructor(roomName, userId, userName) {
        this.roomName = roomName;
        this.userId = userId;
        this.userName = userName;
        
        this.peerConnection = null;
        this.localStream = null;
        this.remoteStream = null;
        this.dataChannel = null;
        
        this.signalingSocket = null;
        this.iceServers = [
            { urls: 'stun:stun.l.google.com:19302' },
            { urls: 'stun:stun1.l.google.com:19302' },
            { urls: 'stun:stun2.l.google.com:19302' },
            { urls: 'stun:stun3.l.google.com:19302' },
            { urls: 'stun:stun4.l.google.com:19302' }
        ];
        
        this.videoEnabled = true;
        this.audioEnabled = true;
    }

    async initialize() {
        try {
            // Get local stream
            this.localStream = await navigator.mediaDevices.getUserMedia({
                video: { width: { ideal: 1280 }, height: { ideal: 720 } },
                audio: true
            });

            // Display local video
            const localVideo = document.getElementById('localVideo');
            if (localVideo) {
                localVideo.srcObject = this.localStream;
            }

            // Initialize signaling
            this.initializeSignaling();

            // Create peer connection
            this.createPeerConnection();

            // Add event listeners
            this.setupControlButtons();
        } catch (error) {
            console.error('Error initializing WebRTC:', error);
            this.showNotification('Failed to access camera/microphone', 'error');
        }
    }

    initializeSignaling() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const signalingUrl = `${protocol}//${window.location.host}/ws/session/${this.roomName}/`;

        this.signalingSocket = new WebSocket(signalingUrl);

        this.signalingSocket.onopen = () => {
            console.log('Signaling connection established');
        };

        this.signalingSocket.onmessage = async (event) => {
            const data = JSON.parse(event.data);
            await this.handleSignalingMessage(data);
        };

        this.signalingSocket.onerror = (error) => {
            console.error('Signaling error:', error);
            this.showNotification('Connection error', 'error');
        };

        this.signalingSocket.onclose = () => {
            console.log('Signaling connection closed');
        };
    }

    createPeerConnection() {
        const peerConnectionConfig = {
            iceServers: this.iceServers
        };

        this.peerConnection = new RTCPeerConnection(peerConnectionConfig);

        // Add local stream tracks
        this.localStream.getTracks().forEach(track => {
            this.peerConnection.addTrack(track, this.localStream);
        });

        // Handle remote stream
        this.peerConnection.ontrack = (event) => {
            console.log('Remote track received:', event.track.kind);
            if (!this.remoteStream) {
                this.remoteStream = new MediaStream();
                const remoteVideo = document.getElementById('remoteVideo');
                if (remoteVideo) {
                    remoteVideo.srcObject = this.remoteStream;
                }
            }
            this.remoteStream.addTrack(event.track);
        };

        // Handle ICE candidates
        this.peerConnection.onicecandidate = (event) => {
            if (event.candidate) {
                this.sendSignalingMessage({
                    type: 'ice_candidate',
                    candidate: event.candidate
                });
            }
        };

        // Handle connection state changes
        this.peerConnection.onconnectionstatechange = () => {
            console.log('Connection state:', this.peerConnection.connectionState);
            if (this.peerConnection.connectionState === 'failed') {
                this.showNotification('Connection failed, attempting to reconnect...', 'error');
            }
        };

        // Handle ICE connection state
        this.peerConnection.oniceconnectionstatechange = () => {
            console.log('ICE connection state:', this.peerConnection.iceConnectionState);
        };
    }

    async handleSignalingMessage(data) {
        try {
            if (data.type === 'offer') {
                await this.handleOffer(data.offer);
            } else if (data.type === 'answer') {
                await this.handleAnswer(data.answer);
            } else if (data.type === 'ice_candidate') {
                await this.handleIceCandidate(data.candidate);
            } else if (data.type === 'user_joined') {
                console.log('User joined:', data.username);
                // Create offer if we're the first one
                if (this.peerConnection.signalingState === 'stable') {
                    await this.createAndSendOffer();
                }
            }
        } catch (error) {
            console.error('Error handling signaling message:', error);
        }
    }

    async createAndSendOffer() {
        try {
            const offer = await this.peerConnection.createOffer();
            await this.peerConnection.setLocalDescription(offer);
            this.sendSignalingMessage({
                type: 'offer',
                offer: offer
            });
        } catch (error) {
            console.error('Error creating offer:', error);
        }
    }

    async handleOffer(offer) {
        try {
            if (this.peerConnection.signalingState !== 'stable') {
                return;
            }

            await this.peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
            const answer = await this.peerConnection.createAnswer();
            await this.peerConnection.setLocalDescription(answer);
            this.sendSignalingMessage({
                type: 'answer',
                answer: answer
            });
        } catch (error) {
            console.error('Error handling offer:', error);
        }
    }

    async handleAnswer(answer) {
        try {
            if (this.peerConnection.signalingState !== 'have-local-offer') {
                return;
            }
            await this.peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
        } catch (error) {
            console.error('Error handling answer:', error);
        }
    }

    async handleIceCandidate(candidate) {
        try {
            if (candidate) {
                await this.peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
            }
        } catch (error) {
            console.error('Error adding ICE candidate:', error);
        }
    }

    sendSignalingMessage(message) {
        if (this.signalingSocket && this.signalingSocket.readyState === WebSocket.OPEN) {
            this.signalingSocket.send(JSON.stringify(message));
        }
    }

    setupControlButtons() {
        const toggleVideoBtn = document.getElementById('toggleVideo');
        const toggleAudioBtn = document.getElementById('toggleAudio');

        if (toggleVideoBtn) {
            toggleVideoBtn.addEventListener('click', () => this.toggleVideo());
        }

        if (toggleAudioBtn) {
            toggleAudioBtn.addEventListener('click', () => this.toggleAudio());
        }
    }

    toggleVideo() {
        this.videoEnabled = !this.videoEnabled;
        this.localStream.getVideoTracks().forEach(track => {
            track.enabled = this.videoEnabled;
        });

        const btn = document.getElementById('toggleVideo');
        if (btn) {
            btn.style.opacity = this.videoEnabled ? '1' : '0.5';
            btn.textContent = this.videoEnabled ? '📹 Video' : '📹 Video (Off)';
        }
    }

    toggleAudio() {
        this.audioEnabled = !this.audioEnabled;
        this.localStream.getAudioTracks().forEach(track => {
            track.enabled = this.audioEnabled;
        });

        const btn = document.getElementById('toggleAudio');
        if (btn) {
            btn.style.opacity = this.audioEnabled ? '1' : '0.5';
            btn.textContent = this.audioEnabled ? '🎤 Audio' : '🎤 Audio (Off)';
        }
    }

    close() {
        if (this.peerConnection) {
            this.peerConnection.close();
        }

        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
        }

        if (this.signalingSocket) {
            this.signalingSocket.close();
        }
    }

    showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }
}
