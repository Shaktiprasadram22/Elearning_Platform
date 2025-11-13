/**
 * Screen Share Manager
 * Handles screen sharing using getDisplayMedia API
 */
class ScreenShareManager {
    constructor(roomName, userId) {
        this.roomName = roomName;
        this.userId = userId;
        
        this.screenStream = null;
        this.screenTrack = null;
        this.isScreenSharing = false;
        this.screenShareContainer = document.getElementById('screenShareContainer');
        this.screenShareVideo = document.getElementById('screenShareVideo');
        
        this.signalingSocket = null;
        this.setupScreenShareButton();
    }

    setupScreenShareButton() {
        const toggleScreenShareBtn = document.getElementById('toggleScreenShare');
        if (toggleScreenShareBtn) {
            toggleScreenShareBtn.addEventListener('click', () => this.toggleScreenShare());
        }
    }

    async toggleScreenShare() {
        if (this.isScreenSharing) {
            await this.stopScreenShare();
        } else {
            await this.startScreenShare();
        }
    }

    async startScreenShare() {
        try {
            // Request screen capture
            this.screenStream = await navigator.mediaDevices.getDisplayMedia({
                video: {
                    cursor: 'always'
                },
                audio: false
            });

            this.screenTrack = this.screenStream.getVideoTracks()[0];

            // Display screen share
            if (this.screenShareVideo) {
                this.screenShareVideo.srcObject = this.screenStream;
                if (this.screenShareContainer) {
                    this.screenShareContainer.style.display = 'block';
                }
            }

            this.isScreenSharing = true;

            // Update button
            const toggleScreenShareBtn = document.getElementById('toggleScreenShare');
            if (toggleScreenShareBtn) {
                toggleScreenShareBtn.style.background = '#dc3545';
                toggleScreenShareBtn.textContent = '🖥️ Stop Sharing';
            }

            // Notify other user
            if (window.signalingSocket && window.signalingSocket.readyState === WebSocket.OPEN) {
                window.signalingSocket.send(JSON.stringify({
                    type: 'screen_share_start'
                }));
            }

            // Handle screen share stop
            this.screenTrack.onended = () => {
                this.stopScreenShare();
            };

            this.showNotification('Screen sharing started', 'success');
        } catch (error) {
            if (error.name !== 'NotAllowedError') {
                console.error('Error starting screen share:', error);
                this.showNotification('Failed to start screen sharing', 'error');
            }
        }
    }

    async stopScreenShare() {
        try {
            if (this.screenStream) {
                this.screenStream.getTracks().forEach(track => track.stop());
                this.screenStream = null;
                this.screenTrack = null;
            }

            if (this.screenShareContainer) {
                this.screenShareContainer.style.display = 'none';
            }

            this.isScreenSharing = false;

            // Update button
            const toggleScreenShareBtn = document.getElementById('toggleScreenShare');
            if (toggleScreenShareBtn) {
                toggleScreenShareBtn.style.background = '#6c757d';
                toggleScreenShareBtn.textContent = '🖥️ Share Screen';
            }

            // Notify other user
            if (window.signalingSocket && window.signalingSocket.readyState === WebSocket.OPEN) {
                window.signalingSocket.send(JSON.stringify({
                    type: 'screen_share_stop'
                }));
            }

            this.showNotification('Screen sharing stopped', 'success');
        } catch (error) {
            console.error('Error stopping screen share:', error);
        }
    }

    handleRemoteScreenShareStart() {
        console.log('Remote user started screen sharing');
        this.showNotification('Other user is sharing their screen', 'info');
    }

    handleRemoteScreenShareStop() {
        console.log('Remote user stopped screen sharing');
        this.showNotification('Other user stopped sharing screen', 'info');
    }

    showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }
}
