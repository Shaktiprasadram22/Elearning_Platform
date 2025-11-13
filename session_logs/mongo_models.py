from pymongo import MongoClient
from datetime import datetime
from django.conf import settings
import os

# Load environment variables (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# MongoDB connection
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'elearning_platform_db')
MONGO_USERNAME = os.getenv('MONGO_USERNAME', '')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', '')
MONGO_URI = os.getenv('MONGO_URI', None)

# Build connection string
if MONGO_URI:
    # Use MongoDB Atlas URI if provided
    connection_string = MONGO_URI
else:
    # Build local connection string
    if MONGO_USERNAME and MONGO_PASSWORD:
        connection_string = f'mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/'
    else:
        connection_string = f'mongodb://{MONGO_HOST}:{MONGO_PORT}/'

client = MongoClient(connection_string)
db = client[MONGO_DB_NAME]
session_logs_collection = db['session_logs']


class SessionLog:
    """
    MongoDB model for storing video session logs
    Stores student-instructor doubt session data including chat transcripts
    """
    
    @staticmethod
    def create_log(student_id, instructor_id, course_id, start_time, end_time=None, chat_transcript=None):
        """
        Create a new session log in MongoDB
        
        Args:
            student_id: ID of the student
            instructor_id: ID of the instructor
            course_id: ID of the course
            start_time: Session start datetime
            end_time: Session end datetime (optional)
            chat_transcript: List of chat messages (optional)
        
        Returns:
            str: Inserted document ID
        """
        log_data = {
            'student_id': student_id,
            'instructor_id': instructor_id,
            'course_id': course_id,
            'start_time': start_time,
            'end_time': end_time,
            'chat_transcript': chat_transcript or [],
            'created_at': datetime.now()
        }
        
        result = session_logs_collection.insert_one(log_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_log_by_id(log_id):
        """
        Get a specific session log by ID
        
        Args:
            log_id: MongoDB ObjectId as string
        
        Returns:
            dict: Session log document
        """
        from bson.objectid import ObjectId
        return session_logs_collection.find_one({'_id': ObjectId(log_id)})
    
    @staticmethod
    def get_logs_by_student(student_id):
        """
        Get all session logs for a student
        
        Args:
            student_id: ID of the student
        
        Returns:
            list: List of session log documents
        """
        return list(session_logs_collection.find({'student_id': student_id}).sort('created_at', -1))
    
    @staticmethod
    def get_logs_by_instructor(instructor_id):
        """
        Get all session logs for an instructor
        
        Args:
            instructor_id: ID of the instructor
        
        Returns:
            list: List of session log documents
        """
        return list(session_logs_collection.find({'instructor_id': instructor_id}).sort('created_at', -1))
    
    @staticmethod
    def get_logs_by_course(course_id):
        """
        Get all session logs for a specific course
        
        Args:
            course_id: ID of the course
        
        Returns:
            list: List of session log documents
        """
        return list(session_logs_collection.find({'course_id': course_id}).sort('created_at', -1))
    
    @staticmethod
    def update_log(log_id, end_time, chat_transcript):
        """
        Update session log with end time and final chat transcript
        
        Args:
            log_id: MongoDB ObjectId as string
            end_time: Session end datetime
            chat_transcript: Complete list of chat messages
        """
        from bson.objectid import ObjectId
        session_logs_collection.update_one(
            {'_id': ObjectId(log_id)},
            {'$set': {
                'end_time': end_time,
                'chat_transcript': chat_transcript
            }}
        )
    
    @staticmethod
    def get_all_logs():
        """
        Get all session logs (admin use)
        
        Returns:
            list: List of all session log documents
        """
        return list(session_logs_collection.find().sort('created_at', -1))
    
    @staticmethod
    def delete_log(log_id):
        """
        Delete a session log
        
        Args:
            log_id: MongoDB ObjectId as string
        """
        from bson.objectid import ObjectId
        session_logs_collection.delete_one({'_id': ObjectId(log_id)})
    
    @staticmethod
    def get_stats_by_student(student_id):
        """
        Get statistics for a student
        
        Args:
            student_id: ID of the student
        
        Returns:
            dict: Statistics including total sessions, total duration, etc.
        """
        logs = SessionLog.get_logs_by_student(student_id)
        total_sessions = len(logs)
        total_minutes = 0
        
        for log in logs:
            if log.get('end_time') and log.get('start_time'):
                duration = (log['end_time'] - log['start_time']).total_seconds() / 60
                total_minutes += duration
        
        return {
            'total_sessions': total_sessions,
            'total_minutes': int(total_minutes)
        }
