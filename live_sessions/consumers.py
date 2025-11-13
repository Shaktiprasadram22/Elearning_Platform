import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import DoubtSession
from django.utils import timezone


class SignalingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for WebRTC signaling
    Handles offer, answer, ICE candidates, and session management
    """
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'session_{self.room_name}'
        self.user = self.scope['user']
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Notify others in room that user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'username': self.user.username,
                'user_id': self.user.id
            }
        )
    
    async def disconnect(self, close_code):
        # Notify others that user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'username': self.user.username,
                'user_id': self.user.id
            }
        )
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        data = json.loads(text_data)
        message_type = data.get('type')
        
        # Route different message types
        if message_type == 'offer':
            await self.handle_offer(data)
        elif message_type == 'answer':
            await self.handle_answer(data)
        elif message_type == 'ice_candidate':
            await self.handle_ice_candidate(data)
        elif message_type == 'chat_message':
            await self.handle_chat_message(data)
        elif message_type == 'session_request':
            await self.handle_session_request(data)
        elif message_type == 'session_accept':
            await self.handle_session_accept(data)
        elif message_type == 'session_end':
            await self.handle_session_end(data)
        elif message_type == 'whiteboard_draw':
            await self.handle_whiteboard_draw(data)
        elif message_type == 'whiteboard_clear':
            await self.handle_whiteboard_clear(data)
        elif message_type == 'screen_share_start':
            await self.handle_screen_share_start(data)
        elif message_type == 'screen_share_stop':
            await self.handle_screen_share_stop(data)
    
    async def handle_offer(self, data):
        """Handle WebRTC offer"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_offer',
                'offer': data['offer'],
                'sender': self.user.username,
                'sender_id': self.user.id
            }
        )
    
    async def handle_answer(self, data):
        """Handle WebRTC answer"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_answer',
                'answer': data['answer'],
                'sender': self.user.username,
                'sender_id': self.user.id
            }
        )
    
    async def handle_ice_candidate(self, data):
        """Handle ICE candidate"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_ice_candidate',
                'candidate': data['candidate'],
                'sender': self.user.username,
                'sender_id': self.user.id
            }
        )
    
    async def handle_chat_message(self, data):
        """Handle text chat message"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': data['message'],
                'sender': self.user.username,
                'sender_id': self.user.id,
                'timestamp': data.get('timestamp')
            }
        )
    
    async def handle_session_request(self, data):
        """Handle session request from student"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'session_request',
                'student_name': self.user.username,
                'student_id': self.user.id,
                'course_id': data.get('course_id')
            }
        )
    
    async def handle_session_accept(self, data):
        """Handle session acceptance from instructor"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'session_accept',
                'instructor_name': self.user.username,
                'instructor_id': self.user.id
            }
        )
    
    async def handle_session_end(self, data):
        """Handle session end"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'session_end',
                'ended_by': self.user.username,
                'chat_log': data.get('chat_log', [])
            }
        )
    
    async def handle_whiteboard_draw(self, data):
        """Handle whiteboard drawing"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'whiteboard_draw',
                'x': data.get('x'),
                'y': data.get('y'),
                'x0': data.get('x0'),
                'y0': data.get('y0'),
                'color': data.get('color', '#000000'),
                'size': data.get('size', 2),
                'sender': self.user.username,
                'sender_id': self.user.id
            }
        )
    
    async def handle_whiteboard_clear(self, data):
        """Handle whiteboard clear"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'whiteboard_clear',
                'sender': self.user.username,
                'sender_id': self.user.id
            }
        )
    
    async def handle_screen_share_start(self, data):
        """Handle screen share start"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'screen_share_start',
                'sender': self.user.username,
                'sender_id': self.user.id
            }
        )
    
    async def handle_screen_share_stop(self, data):
        """Handle screen share stop"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'screen_share_stop',
                'sender': self.user.username,
                'sender_id': self.user.id
            }
        )
    
    # Event handlers (called by channel_layer.group_send)
    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'username': event['username'],
            'user_id': event['user_id']
        }))
    
    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'username': event['username'],
            'user_id': event['user_id']
        }))
    
    async def webrtc_offer(self, event):
        await self.send(text_data=json.dumps({
            'type': 'offer',
            'offer': event['offer'],
            'sender': event['sender'],
            'sender_id': event['sender_id']
        }))
    
    async def webrtc_answer(self, event):
        await self.send(text_data=json.dumps({
            'type': 'answer',
            'answer': event['answer'],
            'sender': event['sender'],
            'sender_id': event['sender_id']
        }))
    
    async def webrtc_ice_candidate(self, event):
        await self.send(text_data=json.dumps({
            'type': 'ice_candidate',
            'candidate': event['candidate'],
            'sender': event['sender'],
            'sender_id': event['sender_id']
        }))
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender': event['sender'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp']
        }))
    
    async def session_request(self, event):
        await self.send(text_data=json.dumps({
            'type': 'session_request',
            'student_name': event['student_name'],
            'student_id': event['student_id'],
            'course_id': event.get('course_id')
        }))
    
    async def session_accept(self, event):
        await self.send(text_data=json.dumps({
            'type': 'session_accept',
            'instructor_name': event['instructor_name'],
            'instructor_id': event['instructor_id']
        }))
    
    async def session_end(self, event):
        await self.send(text_data=json.dumps({
            'type': 'session_end',
            'ended_by': event['ended_by'],
            'chat_log': event.get('chat_log', [])
        }))
    
    async def whiteboard_draw(self, event):
        await self.send(text_data=json.dumps({
            'type': 'whiteboard_draw',
            'x': event['x'],
            'y': event['y'],
            'x0': event['x0'],
            'y0': event['y0'],
            'color': event['color'],
            'size': event['size'],
            'sender': event['sender'],
            'sender_id': event['sender_id']
        }))
    
    async def whiteboard_clear(self, event):
        await self.send(text_data=json.dumps({
            'type': 'whiteboard_clear',
            'sender': event['sender'],
            'sender_id': event['sender_id']
        }))
    
    async def screen_share_start(self, event):
        await self.send(text_data=json.dumps({
            'type': 'screen_share_start',
            'sender': event['sender'],
            'sender_id': event['sender_id']
        }))
    
    async def screen_share_stop(self, event):
        await self.send(text_data=json.dumps({
            'type': 'screen_share_stop',
            'sender': event['sender'],
            'sender_id': event['sender_id']
        }))


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications
    Used for instructor notifications when students request sessions
    """
    
    async def connect(self):
        self.user = self.scope['user']
        self.user_group = f'user_{self.user.id}'
        
        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        # Handle any incoming messages if needed
    
    async def session_notification(self, event):
        """Send session notification to instructor"""
        await self.send(text_data=json.dumps({
            'type': 'session_notification',
            'message': event['message'],
            'student_name': event['student_name'],
            'student_id': event['student_id'],
            'course_id': event.get('course_id'),
            'room_name': event.get('room_name')
        }))
