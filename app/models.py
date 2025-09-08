from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    profile_pic = db.Column(db.String(200))
    semester = db.Column(db.Integer, nullable=True)
    has_completed_onboarding = db.Column(db.Boolean, default=False, nullable=False)
    career_path = db.Column(db.String(100), nullable=True)

    # Relasi ke fitur-fitur lain
    submissions = db.relationship("ProjectSubmission", backref="author", lazy="dynamic", cascade="all, delete-orphan")
    chat_sessions = db.relationship("ChatSession", backref="author", lazy="dynamic", cascade="all, delete-orphan")
    modules = db.relationship("Module", backref="user", lazy='dynamic', cascade="all, delete-orphan")
    user_progress = db.relationship('UserProgress', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    
    timezone = db.Column(db.String(50), nullable=False, server_default='Asia/Jakarta')
    
    
    # Relasi ke fitur baru Personal Hub
    tasks = db.relationship('Task', back_populates='author', lazy='dynamic', cascade="all, delete-orphan")
    events = db.relationship('Event', back_populates='author', lazy='dynamic', cascade="all, delete-orphan")
    notes = db.relationship('Note', backref='author', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.name}>"

class Roadmap(db.Model):
    __tablename__ = "roadmap"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    level = db.Column(db.String(50), nullable=False)
    modules = db.relationship("Module", backref="roadmap", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Roadmap {self.title}>"

class Module(db.Model):
    __tablename__ = "module"
    id = db.Column(db.Integer, primary_key=True)
    roadmap_id = db.Column(db.Integer, db.ForeignKey("roadmap.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    career_path = db.Column(db.String(100), nullable=True)
    
    lessons = db.relationship('Lesson', backref='module', cascade="all, delete-orphan")
    projects = db.relationship('Project', backref='module', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Module {self.title}>"

class Lesson(db.Model):
    __tablename__ = "lesson"
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey("module.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    lesson_type = db.Column(db.String(50), default="article")
    url = db.Column(db.String(500))
    estimated_time = db.Column(db.Integer)
    
    user_progress = db.relationship('UserProgress', backref='lesson', lazy='dynamic', cascade="all, delete-orphan")
    notes = db.relationship('Note', backref='lesson', lazy='dynamic') # Relasi ke catatan

    def __repr__(self):
        return f"<Lesson {self.title}>"
    
    
class Project(db.Model):
    __tablename__ = "project"
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey("module.id"), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.String(50), nullable=True)
    is_challenge = db.Column(db.Boolean, default=False, nullable=False)
    project_goals = db.Column(db.Text, nullable=True)
    tech_stack = db.Column(db.Text, nullable=True)
    evaluation_criteria = db.Column(db.Text, nullable=True)
    resources = db.Column(db.Text, nullable=True)

    # TAMBAHKAN BARIS INI
    chat_session = db.relationship("ChatSession", back_populates="project", uselist=False, cascade="all, delete-orphan")

    submissions = db.relationship("ProjectSubmission", backref="project", lazy="dynamic", cascade="all, delete-orphan")
    notes = db.relationship('Note', backref='project', lazy='dynamic')

    def __repr__(self):
        return f"<Project {self.title}>"
    
    
class ProjectSubmission(db.Model):
    # ... (Model ini tidak perlu diubah, bisa dibiarkan seperti yang Anda punya)
    __tablename__ = "project_submission"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    project_link = db.Column(db.String(200), nullable=False)
    interview_score = db.Column(db.Integer)
    interview_feedback = db.Column(db.Text)
    # Di dalam class ProjectSubmission:
    interview_messages = db.relationship(
        "InterviewMessage", 
        back_populates="submission", # <-- Gunakan back_populates
        lazy="dynamic", 
        cascade="all, delete-orphan"
    )

# --- MODEL BARU UNTUK PERSONAL HUB ---

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(20), default='medium') # 'urgent', 'high', 'medium', 'low'
    status = db.Column(db.String(20), default='todo') # 'todo', 'inprogress', 'done'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    enable_notifications = db.Column(db.Boolean, nullable=False, server_default='1') # Defaultnya notif aktif
    notification_minutes_before = db.Column(db.Integer, nullable=True) # Waktu custom dari pengguna

    
    # Opsional: Tautkan tugas ke Lesson atau Project
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    
    author = db.relationship('User', back_populates='tasks')

    def __repr__(self):
        return f"<Task {self.title}>"

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    link = db.Column(db.String(500), nullable=True) # Untuk link Zoom/GMeet
    color = db.Column(db.String(7), nullable=True, default='#3788d8') # Warna default biru FullCalendar
    
    author = db.relationship('User', back_populates='events')
    
    
    
    enable_notifications = db.Column(db.Boolean, nullable=False, server_default='1')
    notification_minutes_before = db.Column(db.Integer, nullable=True)
    
    

    def __repr__(self):
        return f"<Event {self.title}>"

class Note(db.Model):
    __tablename__ = 'note'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Tautan kontekstual
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)

    def __repr__(self):
        return f"<Note {self.id}>"

# ------------------------------------

class UserProgress(db.Model):
    # ... (Model ini tidak perlu diubah)
    __tablename__ = 'user_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    completed_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
class ChatSession(db.Model):
    # ... (Model ini tidak perlu diubah)
    __tablename__ = "chat_session"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    messages = db.relationship("ChatMessage", backref="session", lazy="dynamic", cascade="all, delete-orphan")
    project = db.relationship('Project', back_populates='chat_session')

class ChatMessage(db.Model):
    # ... (Model ini tidak perlu diubah)
    __tablename__ = "chat_message"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey("chat_session.id"), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

class InterviewMessage(db.Model):
    # ... (Model ini tidak perlu diubah)
    __tablename__ = "interview_message"
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey("project_submission.id"), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    submission = db.relationship(
    "ProjectSubmission", 
    back_populates="interview_messages" # <-- Pastikan ini menunjuk ke nama relasi di atas
)