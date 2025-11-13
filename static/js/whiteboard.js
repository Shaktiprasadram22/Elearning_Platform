/**
 * Whiteboard Manager
 * Handles real-time collaborative whiteboard using HTML Canvas
 */
class WhiteboardManager {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
        
        this.isDrawing = false;
        this.lastX = 0;
        this.lastY = 0;
        
        this.color = '#000000';
        this.size = 2;
        
        this.signalingSocket = null;
        this.drawingBuffer = [];
        
        if (this.canvas) {
            this.resizeCanvas();
            this.setupEventListeners();
        }
    }

    resizeCanvas() {
        if (!this.canvas) return;
        
        const container = this.canvas.parentElement;
        this.canvas.width = container.offsetWidth;
        this.canvas.height = 400;
        
        // Set white background
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }

    setupEventListeners() {
        if (!this.canvas) return;

        // Color picker
        const colorPicker = document.getElementById('colorPicker');
        if (colorPicker) {
            colorPicker.addEventListener('change', (e) => {
                this.color = e.target.value;
            });
        }

        // Size slider
        const sizePicker = document.getElementById('sizePicker');
        if (sizePicker) {
            sizePicker.addEventListener('change', (e) => {
                this.size = parseInt(e.target.value);
            });
        }

        // Clear button
        const clearBtn = document.getElementById('clearWhiteboard');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clear());
        }

        // Mouse events
        this.canvas.addEventListener('mousedown', (e) => this.startDrawing(e));
        this.canvas.addEventListener('mousemove', (e) => this.draw(e));
        this.canvas.addEventListener('mouseup', () => this.stopDrawing());
        this.canvas.addEventListener('mouseout', () => this.stopDrawing());

        // Touch events for mobile
        this.canvas.addEventListener('touchstart', (e) => this.startDrawing(e));
        this.canvas.addEventListener('touchmove', (e) => this.draw(e));
        this.canvas.addEventListener('touchend', () => this.stopDrawing());
    }

    getMousePos(e) {
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;

        let x, y;
        if (e.touches) {
            x = (e.touches[0].clientX - rect.left) * scaleX;
            y = (e.touches[0].clientY - rect.top) * scaleY;
        } else {
            x = (e.clientX - rect.left) * scaleX;
            y = (e.clientY - rect.top) * scaleY;
        }

        return { x, y };
    }

    startDrawing(e) {
        if (!this.canvas) return;
        
        this.isDrawing = true;
        const pos = this.getMousePos(e);
        this.lastX = pos.x;
        this.lastY = pos.y;
    }

    draw(e) {
        if (!this.isDrawing || !this.canvas) return;

        e.preventDefault();
        const pos = this.getMousePos(e);

        // Draw locally
        this.drawLine(this.lastX, this.lastY, pos.x, pos.y);

        // Send to other user
        if (window.signalingSocket && window.signalingSocket.readyState === WebSocket.OPEN) {
            window.signalingSocket.send(JSON.stringify({
                type: 'whiteboard_draw',
                x: pos.x,
                y: pos.y,
                x0: this.lastX,
                y0: this.lastY,
                color: this.color,
                size: this.size
            }));
        }

        this.lastX = pos.x;
        this.lastY = pos.y;
    }

    stopDrawing() {
        this.isDrawing = false;
    }

    drawLine(x0, y0, x1, y1, color = null, size = null) {
        if (!this.ctx) return;

        this.ctx.strokeStyle = color || this.color;
        this.ctx.lineWidth = size || this.size;
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';

        this.ctx.beginPath();
        this.ctx.moveTo(x0, y0);
        this.ctx.lineTo(x1, y1);
        this.ctx.stroke();
    }

    clear() {
        if (!this.ctx) return;

        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Notify other user
        if (window.signalingSocket && window.signalingSocket.readyState === WebSocket.OPEN) {
            window.signalingSocket.send(JSON.stringify({
                type: 'whiteboard_clear'
            }));
        }
    }

    handleRemoteDrawing(data) {
        this.drawLine(data.x0, data.y0, data.x, data.y, data.color, data.size);
    }

    handleRemoteClear() {
        this.clear();
    }
}
