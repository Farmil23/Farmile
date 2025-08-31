# models.py
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    profile_pic = db.Column(db.String(200))
    submissions = db.relationship('ProjectSubmission', backref='author', lazy=True)

    def __repr__(self):
        return f'<User {self.name}>'

class ProjectSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path_name = db.Column(db.String(100), nullable=False)
    project_link = db.Column(db.String(200), nullable=False)
    interview_score = db.Column(db.Integer)
    interview_feedback = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Submission {self.path_name} by User {self.user_id}>'