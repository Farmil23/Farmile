from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    profile_pic = db.Column(db.String(200))
    semester = db.Column(db.Integer, nullable=True)
    has_completed_onboarding = db.Column(db.Boolean, default=False, nullable=False)
    career_path = db.Column(db.String(100), nullable=True)
    submissions = db.relationship('ProjectSubmission', backref='author', lazy='dynamic', cascade="all, delete-orphan")
    chat_sessions = db.relationship('ChatSession', backref='author', lazy='dynamic', cascade="all, delete-orphan")
    chat_messages = db.relationship('ChatMessage', backref='author', lazy='dynamic', cascade="all, delete-orphan")
    modules = db.relationship('Module', backref='author', lazy='dynamic', cascade="all, delete-orphan")
    progress = db.relationship('UserProgress', backref='user', lazy='dynamic', cascade="all, delete-orphan")

# ... (Kode lengkap untuk semua model lain: Project, ProjectSubmission, ChatSession, ChatMessage, Module, Lesson, UserProgress)
    def __repr__(self):
        return f'<User {self.name}>'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    career_path = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Project {self.title}>'

class ProjectSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_link = db.Column(db.String(200), nullable=False)
    interview_score = db.Column(db.Integer)
    interview_feedback = db.Column(db.Text)
    project = db.relationship('Project', backref='submissions')

    def __repr__(self):
        return f'<Submission for Project {self.project_id} by User {self.user_id}>'

class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    messages = db.relationship('ChatMessage', backref='session', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<ChatSession {self.title}>'

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<ChatMessage {self.id}>'

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    career_path = db.Column(db.String(100), nullable=False)
    lessons = db.relationship('Lesson', backref='module', lazy='dynamic', cascade="all, delete-orphan")

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(500))
    lesson_type = db.Column(db.String(50), default='article')
    estimated_time = db.Column(db.Integer)

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)