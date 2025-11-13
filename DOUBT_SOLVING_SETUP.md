# 1-to-1 Doubt Solving Feature Setup Guide

## Overview
Complete 1-to-1 doubt solving feature with WebRTC video/audio, live chat, whiteboard, and screen sharing for Django E-Learning platform.

## Features Implemented

✅ **WebRTC P2P Communication**
- Video and audio streaming
- ICE candidate handling
- Automatic reconnection

✅ **Live Chat**
- Real-time text messaging
- Message history
- Timestamp tracking

✅ **Collaborative Whiteboard**
- HTML Canvas drawing
- Real-time synchronization
- Color and brush size controls
- Clear canvas functionality

✅ **Screen Sharing**
- getDisplayMedia API integration
- Real-time screen capture
- Toggle on/off

✅ **Session Management**
- Student requests doubt session
- Instructor accepts/rejects requests
- Real-time notifications
- Session logging in MongoDB
- Duration tracking

✅ **Dashboards**
- Instructor dashboard with pending/active/completed sessions
- Student dashboard with session history
- Real-time status updates

✅ **Mock Data**
- 3 instructors with courses
- 5 students enrolled in courses
- 25 lessons with descriptions
- Pre-populated database

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup

#### SQLite (for Django models)
```bash
python manage.py makemigrations
python manage.py migrate
```

#### MongoDB (for session logging)
Make sure MongoDB is running locally:
```bash
# On Windows
mongod

# On macOS
brew services start mongodb-community

# On Linux
sudo systemctl start mongod
```

### 3. Populate Mock Data
```bash
python manage.py populate_mock_data
```

This creates:
- 3 instructors (instructor1, instructor2, instructor3)
- 5 students (student1, student2, student3, student4, student5)
- 5 courses with 5 lessons each
- Student enrollments

**Default password for all users:** `password123`

### 4. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 5. Run Development Server

#### Using Daphne (for WebSocket support)
```bash
daphne -b 0.0.0.0 -p 8000 elearning_platform.asgi:application
```

#### Or using Django's development server (limited WebSocket support)
```bash
python manage.py runserver
```

## Usage

### Student Workflow
1. Login as a student (e.g., `student1` / `password123`)
2. Browse courses and enroll
3. Watch a lesson
4. Click "Start Doubt Session" button
5. Wait for instructor to accept
6. Use video, audio, chat, whiteboard, and screen sharing

### Instructor Workflow
1. Login as an instructor (e.g., `instructor1` / `password123`)
2. Go to "Instructor Dashboard" (`/live-sessions/instructor-dashboard/`)
3. View pending doubt session requests
4. Click "Accept" to join the session
5. Use all features to help the student

### URLs

**Student Dashboard:**
```
/live-sessions/student-dashboard/
```

**Instructor Dashboard:**
```
/live-sessions/instructor-dashboard/
```

**Doubt Session Room:**
```
/live-sessions/room/<room_name>/
```

**Request Session:**
```
/live-sessions/request/<lesson_id>/
```

## Architecture

### Backend
- **Django 4.2**: Web framework
- **Django Channels 4.0.0**: WebSocket support (InMemoryChannelLayer)
- **Daphne 4.0.0**: ASGI server
- **MongoDB**: Session logging and transcript storage

### Frontend
- **Bootstrap 5**: UI framework
- **Vanilla JavaScript**: No frameworks
- **WebRTC**: P2P communication
- **HTML Canvas**: Whiteboard
- **getDisplayMedia**: Screen sharing

### Key Components

#### Models
- `DoubtSession`: Tracks student-instructor sessions
- `UserProfile`: Student/Instructor roles
- `Course`, `Lesson`, `Enrollment`: Course management

#### WebSocket Consumers
- `SignalingConsumer`: WebRTC signaling, whiteboard, chat, screen sharing
- `NotificationConsumer`: Real-time notifications

#### JavaScript Managers
- `WebRTCManager`: P2P video/audio
- `ChatManager`: Text messaging
- `WhiteboardManager`: Collaborative drawing
- `ScreenShareManager`: Screen capture

#### Views
- `request_session_view`: Student initiates session
- `session_room_view`: Main session room
- `instructor_dashboard_view`: Instructor's pending/active sessions
- `student_dashboard_view`: Student's session history
- `accept_session_view`: Instructor accepts request
- `reject_session_view`: Instructor rejects request
- `end_session_view`: End active session

## File Structure

```
elearning_platform/
├── live_sessions/
│   ├── models.py              # DoubtSession model
│   ├── views.py               # Session views
│   ├── consumers.py           # WebSocket consumers
│   ├── urls.py                # URL routing
│   ├── routing.py             # WebSocket routing
│   └── templates/
│       └── live_sessions/
│           ├── doubt_session.html           # Main session room
│           ├── instructor_dashboard.html    # Instructor dashboard
│           └── student_dashboard.html       # Student dashboard
├── static/js/
│   ├── webrtc.js              # WebRTC manager
│   ├── chat.js                # Chat manager
│   ├── whiteboard.js          # Whiteboard manager
│   └── screenshare.js         # Screen sharing manager
├── courses/
│   ├── management/commands/
│   │   └── populate_mock_data.py  # Mock data generator
│   ├── models.py              # Course, Lesson, Enrollment
│   └── views.py               # Course views
├── session_logs/
│   ├── mongo_models.py        # MongoDB session logging
│   └── services.py            # Session services
└── elearning_platform/
    ├── settings.py            # Django settings
    ├── asgi.py                # ASGI configuration
    └── urls.py                # URL routing
```

## WebSocket Message Types

### Signaling
- `offer`: WebRTC offer
- `answer`: WebRTC answer
- `ice_candidate`: ICE candidate

### Chat
- `chat_message`: Text message

### Whiteboard
- `whiteboard_draw`: Drawing stroke
- `whiteboard_clear`: Clear canvas

### Screen Sharing
- `screen_share_start`: Start sharing
- `screen_share_stop`: Stop sharing

### Session Management
- `session_request`: Student requests session
- `session_accept`: Instructor accepts
- `session_end`: Session ends

## Troubleshooting

### WebSocket Connection Issues
- Ensure Daphne is running (not Django dev server)
- Check firewall settings
- Verify ASGI configuration in settings.py

### Camera/Microphone Not Working
- Check browser permissions
- Ensure HTTPS in production (WebRTC requires secure context)
- Test with `https://localhost:8000` in development

### MongoDB Connection Issues
- Verify MongoDB is running
- Check connection string in `session_logs/mongo_models.py`
- Default: `mongodb://localhost:27017/`

### Screen Sharing Not Working
- Only works in HTTPS (or localhost)
- Browser must support getDisplayMedia API
- User must grant permission

## Performance Considerations

1. **InMemoryChannelLayer**: Suitable for development/small deployments
   - For production, use Redis Channel Layer
   - Update `CHANNEL_LAYERS` in settings.py

2. **MongoDB**: Ensure indexes on frequently queried fields
   - `student_id`, `instructor_id`, `course_id`

3. **WebRTC**: P2P connection works best with good network
   - STUN servers configured for NAT traversal
   - Consider TURN servers for production

## Security Notes

1. **Authentication**: All views require login
2. **Authorization**: Students can only request sessions for enrolled courses
3. **CSRF Protection**: All POST requests protected
4. **WebSocket Auth**: Uses Django's AuthMiddlewareStack
5. **Secrets**: Change `SECRET_KEY` in production

## Future Enhancements

- [ ] Recording sessions
- [ ] Session transcripts with AI
- [ ] Persistent chat history
- [ ] Drawing annotations on screen share
- [ ] Multiple instructor support
- [ ] Session scheduling
- [ ] Performance metrics
- [ ] Mobile app support

## Support

For issues or questions, refer to:
- Django Channels: https://channels.readthedocs.io/
- WebRTC: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API
- MongoDB: https://docs.mongodb.com/

## License

This project is part of the E-Learning Platform.
