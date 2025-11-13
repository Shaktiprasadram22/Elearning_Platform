-- Create doubt_sessions table directly
CREATE TABLE IF NOT EXISTS doubt_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    instructor_id INTEGER,
    course_id INTEGER NOT NULL,
    lesson_id INTEGER,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    room_name VARCHAR(100) NOT NULL UNIQUE,
    requested_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    ended_at DATETIME,
    duration_minutes INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES auth_user(id),
    FOREIGN KEY (instructor_id) REFERENCES auth_user(id),
    FOREIGN KEY (course_id) REFERENCES courses(id),
    FOREIGN KEY (lesson_id) REFERENCES lessons(id)
);
