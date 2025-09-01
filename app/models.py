# models.py
from app import db
from flask_login import UserMixin

# app/models.py
# app/models.py
from app import db
from flask_login import UserMixin
from datetime import datetime # <-- Mungkin perlu diimpor jika belum adaclass Module(db.Model):
id = db.Column(db.Integer, primary_key=True)
title = db.Column(db.String(200), nullable=False)
order = db.Column(db.Integer, nullable=False)
career_path = db.Column(db.String(100), nullable=False)
lessons = db.relationship('Lesson', backref='module', lazy='dynamic', cascade="all, delete-orphan")

# app/models.py

# ... (tambahkan di bawah class ChatMessage) ...

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    career_path = db.Column(db.String(100), nullable=False)
    lessons = db.relationship('Lesson', backref='module', lazy='dynamic', cascade="all, delete-orphan")

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(500)) # Link ke artikel/video
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    # --- TAMBAHKAN DUA BARIS INI ---
    lesson_type = db.Column(db.String(50), default='article') # 'article', 'video', 'quiz'
    estimated_time = db.Column(db.Integer) # Dalam menit

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class User(UserMixin, db.Model):
    # INI YANG PALING PENTING, PASTIKAN ADA
    id = db.Column(db.Integer, primary_key=True)

    # Kolom-kolom yang sudah ada sebelumnya
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    profile_pic = db.Column(db.String(200))

    # Relasi ke submission
    submissions = db.relationship('ProjectSubmission', backref='author', lazy=True)
    chat_messages = db.relationship('ChatMessage', backref='author', lazy='dynamic')
    semester = db.Column(db.Integer, nullable=True)

    has_completed_onboarding = db.Column(db.Boolean, default=False, nullable=False)
    career_path = db.Column(db.String(100), nullable=True)
    chat_sessions = db.relationship('ChatSession', backref='author', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.name}>'

    
    # MODEL BARU: Untuk menyimpan daftar proyek yang tersedia
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(50), nullable=False) # Contoh: 'Pemula', 'Menengah'
    career_path = db.Column(db.String(100), nullable=False) # 'frontend', 'backend', dll.

    def __repr__(self):
        return f'<Project {self.title}>'

# MODIFIKASI MODEL ProjectSubmission
class ProjectSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Kolom 'path_name' kita ganti dengan foreign key ke model Project
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project', backref='submissions') # relasi
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_link = db.Column(db.String(200), nullable=False)
    interview_score = db.Column(db.Integer)
    interview_feedback = db.Column(db.Text)

    def __repr__(self):
        return f'<Submission for Project {self.project_id} by User {self.user_id}>'

# Tambahkan class baru ini di akhir file
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(10), nullable=False) # 'user' atau 'assistant'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    def __repr__(self):
        return f'<ChatMessage {self.id}>'
    
# TAMBAHKAN MODEL BARU INI
# app/models.py
class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # --- (baris title, timestamp, messages tetap sama) ---
    title = db.Column(db.String(150), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    messages = db.relationship('ChatMessage', backref='session', lazy='dynamic', cascade="all, delete-orphan")

