# Testing Guide - Doubt Solving Feature

## Pre-Test Setup

### 1. Start MongoDB
```bash
# Windows
mongod

# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongod
```

### 2. Start Django Development Server
```bash
# Using Daphne (recommended for WebSocket)
daphne -b 0.0.0.0 -p 8000 elearning_platform.asgi:application

# Or using Django dev server
python manage.py runserver
```

### 3. Populate Mock Data
```bash
python manage.py populate_mock_data
```

## Test Scenarios

### Scenario 1: Student Requests Doubt Session

**Steps:**
1. Open browser 1: http://localhost:8000/accounts/login/
2. Login as `student1` / `password123`
3. Navigate to Courses
4. Click on any course (e.g., "Python Programming Fundamentals")
5. Click on a lesson (e.g., "Introduction to Python")
6. Click "Start Doubt Session" button

**Expected Results:**
- ✅ Session request created
- ✅ Redirected to session room
- ✅ Local video/audio enabled
- ✅ Waiting for instructor message shown

### Scenario 2: Instructor Accepts Session

**Steps:**
1. Open browser 2: http://localhost:8000/accounts/login/
2. Login as `instructor1` / `password123`
3. Navigate to `/live-sessions/instructor-dashboard/`
4. See pending request from student1
5. Click "Accept" button

**Expected Results:**
- ✅ Session status changes to "Active"
- ✅ Instructor redirected to session room
- ✅ Both users see each other's video
- ✅ Session started_at timestamp recorded

### Scenario 3: Video & Audio Communication

**Steps:**
1. Both users in session room
2. Speak and verify audio transmission
3. Check video streams on both sides
4. Click "Toggle Video" button
5. Click "Toggle Audio" button

**Expected Results:**
- ✅ Audio transmitted in real-time
- ✅ Video streams visible
- ✅ Toggle buttons disable/enable streams
- ✅ Button UI updates to show status

### Scenario 4: Live Chat

**Steps:**
1. Both users in session room
2. Student types message in chat input
3. Student clicks "Send" or presses Enter
4. Verify message appears in both chats

**Expected Results:**
- ✅ Message appears instantly on both sides
- ✅ Sender name displayed
- ✅ Timestamp shown
- ✅ Own messages styled differently
- ✅ Chat scrolls to latest message

### Scenario 5: Whiteboard Drawing

**Steps:**
1. Both users in session room
2. Click "Whiteboard" button
3. Student draws on whiteboard
4. Change color using color picker
5. Adjust brush size with slider
6. Click "Clear" button

**Expected Results:**
- ✅ Whiteboard appears below video
- ✅ Drawing syncs to instructor in real-time
- ✅ Color changes apply to new strokes
- ✅ Size slider adjusts brush thickness
- ✅ Clear button erases all drawings on both sides

### Scenario 6: Screen Sharing

**Steps:**
1. Both users in session room
2. Instructor clicks "Share Screen" button
3. Select screen/window to share
4. Verify screen appears in session
5. Click "Stop Sharing" button

**Expected Results:**
- ✅ Screen share container appears
- ✅ Screen content visible to student
- ✅ Button changes to "Stop Sharing"
- ✅ Screen share stops when button clicked
- ✅ Container hidden after stop

### Scenario 7: Session Ending

**Steps:**
1. Both users in active session
2. One user clicks "End Session" button
3. Confirm session end

**Expected Results:**
- ✅ Session status changes to "Completed"
- ✅ Duration calculated and saved
- ✅ User redirected to dashboard
- ✅ Session appears in completed list

### Scenario 8: Student Dashboard

**Steps:**
1. Login as student
2. Navigate to `/live-sessions/student-dashboard/`
3. Check tabs: Pending, Active, Completed

**Expected Results:**
- ✅ Pending sessions show "Waiting for instructor"
- ✅ Active sessions show "Join Session" button
- ✅ Completed sessions show duration and date
- ✅ Stats cards show correct counts
- ✅ Tab switching works

### Scenario 9: Instructor Dashboard

**Steps:**
1. Login as instructor
2. Navigate to `/live-sessions/instructor-dashboard/`
3. Check tabs: Pending Requests, Active Sessions, Completed

**Expected Results:**
- ✅ Pending requests show "Accept" and "Reject" buttons
- ✅ Active sessions show "Join Session" button
- ✅ Completed sessions show duration
- ✅ Stats cards show correct counts
- ✅ Dashboard auto-refreshes every 30 seconds

### Scenario 10: Reject Session

**Steps:**
1. Instructor dashboard with pending request
2. Click "Reject" button
3. Confirm rejection

**Expected Results:**
- ✅ Session status changes to "Rejected"
- ✅ Pending request disappears from list
- ✅ Student sees rejection notification

### Scenario 11: Multiple Concurrent Sessions

**Steps:**
1. Have multiple students request sessions
2. Instructor accepts one session
3. Verify other requests still pending
4. Accept another session in new browser tab

**Expected Results:**
- ✅ Each session has unique room_name
- ✅ Sessions don't interfere with each other
- ✅ Instructor can manage multiple sessions

### Scenario 12: MongoDB Session Logging

**Steps:**
1. Complete a doubt session
2. Open MongoDB client
3. Query `session_logs` collection

```javascript
db.session_logs.findOne({student_id: 1})
```

**Expected Results:**
- ✅ Session log created with all details
- ✅ student_id, instructor_id, course_id recorded
- ✅ start_time and end_time stored
- ✅ Chat transcript saved (if implemented)

## Browser Compatibility

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| WebRTC Video | ✅ | ✅ | ✅ | ✅ |
| WebRTC Audio | ✅ | ✅ | ✅ | ✅ |
| WebSocket | ✅ | ✅ | ✅ | ✅ |
| Canvas Drawing | ✅ | ✅ | ✅ | ✅ |
| getDisplayMedia | ✅ | ✅ | ⚠️ | ✅ |

⚠️ Safari requires user permission and specific settings

## Performance Testing

### Network Conditions
- Test with throttled network (DevTools)
- Verify graceful degradation
- Check reconnection handling

### Load Testing
- Multiple concurrent sessions
- Monitor CPU/Memory usage
- Check WebSocket message throughput

### Latency Testing
- Measure video/audio delay
- Check chat message latency
- Verify whiteboard sync delay

## Debugging Tips

### Enable WebSocket Debugging
```javascript
// In browser console
const ws = new WebSocket('ws://localhost:8000/ws/session/test/');
ws.onmessage = (e) => console.log('Received:', JSON.parse(e.data));
ws.send(JSON.stringify({type: 'test'}));
```

### Check Django Logs
```bash
# Terminal running Django
# Look for WebSocket connection messages
# Check for errors in consumer
```

### Monitor MongoDB
```bash
# MongoDB shell
use elearning_platform_db
db.session_logs.find().pretty()
```

### Browser DevTools
1. **Network Tab**: Monitor WebSocket connections
2. **Console**: Check JavaScript errors
3. **Performance**: Profile video/audio performance
4. **Application**: Check WebRTC stats

## Known Limitations

1. **InMemoryChannelLayer**: Single server only
   - Use Redis for multi-server deployment

2. **Screen Sharing**: HTTPS required in production
   - Works on localhost in development

3. **Browser Support**: Some older browsers don't support WebRTC
   - Requires modern browser (Chrome 50+, Firefox 55+, Safari 11+, Edge 79+)

4. **Network**: Requires stable internet connection
   - Works best with STUN servers configured
   - Consider TURN servers for production

## Troubleshooting

### WebSocket Connection Fails
- Check Daphne is running
- Verify WebSocket URL is correct
- Check browser console for errors
- Ensure firewall allows WebSocket

### No Video/Audio
- Check browser permissions
- Verify camera/microphone connected
- Test with https://webrtc.github.io/samples/
- Check browser console for getUserMedia errors

### Whiteboard Not Syncing
- Verify WebSocket connection active
- Check browser console for errors
- Ensure canvas element exists
- Test with simple drawing first

### Screen Share Not Working
- Verify browser supports getDisplayMedia
- Check HTTPS (or localhost)
- Grant screen sharing permission
- Test with https://www.webrtc-experiment.com/

### MongoDB Not Storing Data
- Verify MongoDB is running
- Check connection string
- Verify database name
- Check collection permissions

## Test Checklist

- [ ] Student can request session
- [ ] Instructor receives notification
- [ ] Instructor can accept session
- [ ] Video/audio works both ways
- [ ] Chat messages sync
- [ ] Whiteboard drawing syncs
- [ ] Screen sharing works
- [ ] Session ends properly
- [ ] Duration calculated correctly
- [ ] Data logged to MongoDB
- [ ] Dashboards show correct data
- [ ] Multiple sessions work
- [ ] Rejection works
- [ ] Auto-refresh works
- [ ] Responsive on mobile

## Performance Benchmarks

**Target Metrics:**
- Video latency: < 500ms
- Chat latency: < 100ms
- Whiteboard sync: < 50ms
- Page load: < 2s
- WebSocket connection: < 1s

## Regression Testing

After any code changes:
1. Run all scenarios above
2. Check browser console for errors
3. Monitor network traffic
4. Verify MongoDB logs
5. Test on multiple browsers
6. Test on mobile devices
