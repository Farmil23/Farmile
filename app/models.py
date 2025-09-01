# models.py
from app import db
from flask_login import UserMixin

# app/models.py
# app/models.py
from app import db
from flask_login import UserMixin
from datetime import datetime # <-- Mungkin perlu diimpor jika belum ada

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

    semester = db.Column(db.Integer, nullable=True)

    has_completed_onboarding = db.Column(db.Boolean, default=False, nullable=False)
    career_path = db.Column(db.String(100), nullable=True)

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

