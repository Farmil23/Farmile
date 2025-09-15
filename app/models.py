from app import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import or_
import json


connections = db.Table('connections',
    db.Column('user_a_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('user_b_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


# --- GANTI SELURUH CLASS ConnectionRequest DENGAN INI ---
class ConnectionRequest(db.Model):
    __tablename__ = 'connection_request'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # Definisikan relasi dengan back_populates
    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='sent_requests')
    receiver = db.relationship('User', foreign_keys=[receiver_id], back_populates='received_requests')



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
    
    # ---> TAMBAHKAN BARIS INI TEPAT DI SINI <---
    username = db.Column(db.String(80), unique=True, nullable=True)
    
    # --- TAMBAHKAN DUA RELASI BARU INI DI DALAM CLASS USER ---
    sent_requests = db.relationship('ConnectionRequest', foreign_keys=[ConnectionRequest.sender_id], back_populates='sender', lazy='dynamic', cascade="all, delete-orphan")
    received_requests = db.relationship('ConnectionRequest', foreign_keys=[ConnectionRequest.receiver_id], back_populates='receiver', lazy='dynamic', cascade="all, delete-orphan")
    
    
    # Relasi ke fitur baru Personal Hub
    tasks = db.relationship('Task', back_populates='author', lazy='dynamic', cascade="all, delete-orphan")
    events = db.relationship('Event', back_populates='author', lazy='dynamic', cascade="all, delete-orphan")
    notes = db.relationship('Note', backref='author', lazy='dynamic', cascade="all, delete-orphan")
    
    # --- Tambahkan relasi ini di dalam class User ---
    connected = db.relationship(
        'User', secondary=connections,
        primaryjoin=(connections.c.user_a_id == id),
        secondaryjoin=(connections.c.user_b_id == id),
        backref=db.backref('connections', lazy='dynamic'), lazy='dynamic')

    # --- Tambahkan fungsi helper ini di dalam class User ---
    def add_connection(self, user):
        if not self.is_connected(user):
            self.connected.append(user)
            user.connected.append(self)

    def remove_connection(self, user):
        if self.is_connected(user):
            self.connected.remove(user)
            user.connected.remove(self)

    def is_connected(self, user):
        return self.connected.filter(
            connections.c.user_b_id == user.id).count() > 0

    def sent_connection_request(self, user):
        return ConnectionRequest.query.filter_by(sender_id=self.id, receiver_id=user.id).count() > 0

    def received_connection_request(self, user):
        return ConnectionRequest.query.filter_by(sender_id=user.id, receiver_id=self.id).count() > 0

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

    level = db.Column(db.String(50), default='beginner', nullable=False) # <-- TAMBAHKAN BARIS INI
    
    def __repr__(self):
        return f"<Module {self.title}>"

# Di dalam file models.py

class Lesson(db.Model):
    __tablename__ = "lesson"
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey("module.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    # --- TAMBAHKAN KOLOM INI ---
    description = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, nullable=False)
    lesson_type = db.Column(db.String(50), default="article")
    url = db.Column(db.String(500))
    estimated_time = db.Column(db.Integer)
    
    quiz = db.Column(db.Text, nullable=True) # <-- TAMBAHKAN BARIS INI
    
    
    content = db.Column(db.Text, nullable=True) # <-- BARIS INI DITAMBAHKAN
    
    
    user_progress = db.relationship('UserProgress', backref='lesson', lazy='dynamic', cascade="all, delete-orphan")
    notes = db.relationship('Note', backref='lesson', lazy='dynamic')

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
    
class UserProject(db.Model):
    __tablename__ = 'user_project'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    
    status = db.Column(db.String(50), default='in_progress', nullable=False) # Contoh: 'in_progress', 'submitted'
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    
     # --- TAMBAHKAN KOLOM BARU INI ---
    reflection = db.Column(db.Text, nullable=True) # Untuk menyimpan cerita pengguna
    
    # Membuat relasi agar kita bisa memanggil user_project.user dan user_project.project
    user = db.relationship('User', backref=db.backref('active_projects', cascade="all, delete-orphan"))
    project = db.relationship('Project', backref=db.backref('takers', cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<UserProject User {self.user_id} - Project {self.project_id}>'
    
    
    
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

    reminder_minutes = db.Column(db.Integer, default=30) # Default 30 menit
    
    
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
    
    
    reminder_minutes = db.Column(db.Integer, default=10) # Default 10 menit
    
    
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
    
    # --- TAMBAHKAN DUA BARIS INI ---
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=True)
    lesson = db.relationship('Lesson', backref=db.backref('chat_sessions', cascade="all, delete-orphan"))
    # --- AKHIR PERUBAHAN ---

class ChatMessage(db.Model):
    # ... (Model ini tidak perlu diubah)
    __tablename__ = "chat_message"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey("chat_session.id"), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat() + 'Z'
        }

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
    
    
    

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(300), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    link = db.Column(db.String(255))  # URL tujuan saat notifikasi diklik
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'is_read': self.is_read,
            'link': self.link,
            'timestamp': self.created_at.isoformat() + 'Z'
        }

    def __repr__(self):
        return f'<Notification {self.message[:50]}>'
    
    
    
    
    
# Tambahkan ini di bagian bawah file app/models.py

class UserResume(db.Model):
    __tablename__ = 'user_resume'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    resume_content = db.Column(db.Text, nullable=False)  # Menyimpan teks hasil ekstraksi
    ai_feedback = db.Column(db.Text, nullable=True)     # Menyimpan feedback dari AI
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    
    
    # --- TAMBAHKAN KOLOM BARU INI ---
    generated_cv_json = db.Column(db.Text, nullable=True) # Menyimpan JSON CV final
    # --------------------------------
    
    

    author = db.relationship('User', backref=db.backref('resumes', cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<UserResume {self.original_filename}>'
    
# Tambahkan ini di bagian bawah file app/models.py

class JobApplication(db.Model):
    __tablename__ = 'job_application'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    position = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(50), default='applied', nullable=False) # e.g., 'wishlist', 'applied', 'interview', 'offer', 'rejected'
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    job_link = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    # Untuk menghubungkan dengan CV yang digunakan
    resume_id = db.Column(db.Integer, db.ForeignKey('user_resume.id'), nullable=True) 

    author = db.relationship('User', backref=db.backref('job_applications', cascade="all, delete-orphan"))
    resume_used = db.relationship('UserResume')

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'position': self.position,
            'status': self.status,
            'application_date': self.application_date.isoformat(),
            'job_link': self.job_link,
            'notes': self.notes,
            'resume_filename': self.resume_used.original_filename if self.resume_used else None
        }

    def __repr__(self):
        return f'<JobApplication {self.position} at {self.company_name}>'
    
    
# Tambahkan ini di bagian bawah file app/models.py

class JobCoachMessage(db.Model):
    __tablename__ = 'job_coach_message'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('job_application.id'), nullable=False)
    role = db.Column(db.String(10), nullable=False) # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    application = db.relationship('JobApplication', backref=db.backref('coach_messages', cascade="all, delete-orphan"))

    def to_dict(self):
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }

    def __repr__(self):
        return f'<JobCoachMessage for App {self.application_id}>'
    
    
# Tambahkan di bagian paling bawah file app/models.py

class JobMatchAnalysis(db.Model):
    __tablename__ = 'job_match_analysis'
    id = db.Column(db.Integer, primary_key=True)
    user_resume_id = db.Column(db.Integer, db.ForeignKey('user_resume.id'), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    match_result = db.Column(db.Text, nullable=False) # Hasil analisis dari AI
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    resume = db.relationship('UserResume', backref=db.backref('analyses', lazy='dynamic', cascade="all, delete-orphan"))

    def to_dict(self):
        return {
            'id': self.id,
            'job_description': self.job_description,
            'match_result': self.match_result,
            'created_at': self.created_at.isoformat()
        }
        
        
        
        
        
        
        
        
        
        
        
        
# Di dalam app/models.py

# --- Tambahkan dua class baru ini di bagian paling bawah file ---

class Conversation(db.Model):
    """Model ini merepresentasikan satu ruang chat antara dua pengguna."""
    __tablename__ = 'conversation'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) # Waktu pesan terakhir untuk sorting
    
    # Relasi ke partisipan (pengguna) dalam percakapan
    participants = db.relationship('User', secondary='conversation_participants',
                                 backref=db.backref('conversations', lazy='dynamic'))
    messages = db.relationship('DirectMessage', backref='conversation', lazy='dynamic', cascade="all, delete-orphan")

# Tabel asosiasi untuk melacak siapa saja yang ada di dalam sebuah percakapan
conversation_participants = db.Table('conversation_participants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('conversation_id', db.Integer, db.ForeignKey('conversation.id'), primary_key=True)
)

study_group_members = db.Table('study_group_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('study_group.id'), primary_key=True)
)

class DirectMessage(db.Model):
    """Model ini merepresentasikan satu pesan individual."""
    __tablename__ = 'direct_message'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    sender = db.relationship('User')

    def to_dict(self):
        return {
            "id": self.id,
            "sender": {
                "id": self.sender.id,
                "name": self.sender.name,
                "profile_pic": self.sender.profile_pic
            },
            "content": self.content,
            "timestamp": self.timestamp.isoformat() + "Z"
        }
        
    # --- Tambahkan class baru ini di bawah class DirectMessage ---
class StudyGroup(db.Model):
    __tablename__ = 'study_group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_private = db.Column(db.Boolean, default=False, nullable=False) # <-- TAMBAHKAN INI
    
    creator = db.relationship('User', backref='created_groups')
    members = db.relationship('User', secondary=study_group_members, lazy='dynamic',
                              backref=db.backref('study_groups', lazy='dynamic'))

    def __repr__(self):
        return f'<StudyGroup {self.name}>'
    
    
# Di dalam app/models.py, tambahkan Class baru ini di bagian bawah file

class QuizHistory(db.Model):
    __tablename__ = 'quiz_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    attempt_number = db.Column(db.Integer, nullable=False)
    # Menyimpan jawaban pengguna dalam format JSON untuk review detail
    answers_data = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('quiz_history', cascade="all, delete-orphan"))
    lesson = db.relationship('Lesson', backref=db.backref('quiz_history', cascade="all, delete-orphan"))

    def to_dict(self):
        return {
            'id': self.id,
            'score': self.score,
            'attempt_number': self.attempt_number,
            'answers_data': json.loads(self.answers_data) if self.answers_data else None,
            'timestamp': self.timestamp.isoformat()
        }