from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = "user"
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    profile_pic = db.Column(db.String(200))
    semester = db.Column(db.Integer, nullable=True)
    has_completed_onboarding = db.Column(db.Boolean, default=False, nullable=False)
    career_path = db.Column(db.String(100), nullable=True)

    user_progress = db.relationship('UserProgress', back_populates='user', lazy='dynamic', cascade="all, delete-orphan")
    submissions = db.relationship("ProjectSubmission", backref="author", lazy="dynamic", cascade="all, delete-orphan")
    chat_sessions = db.relationship("ChatSession", backref="author", lazy="dynamic", cascade="all, delete-orphan")
    chat_messages = db.relationship("ChatMessage", backref="author", lazy="dynamic", cascade="all, delete-orphan")
    modules = db.relationship("Module", backref="user", lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.name}>"

class UserProgress(db.Model):
    __tablename__ = 'user_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    completed_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    user = db.relationship('User', back_populates='user_progress')
    lesson = db.relationship('Lesson', back_populates='user_progress')

    def __repr__(self):
        return f"<UserProgress user:{self.user_id} lesson:{self.lesson_id}>"

class Roadmap(db.Model):
    __tablename__ = "roadmap"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    level = db.Column(db.String(50), nullable=False)
    modules = db.relationship("Module", back_populates="roadmap", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Roadmap {self.title}>"

class Module(db.Model):
    __tablename__ = "module"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    roadmap_id = db.Column(db.Integer, db.ForeignKey("roadmap.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, nullable=False)
    career_path = db.Column(db.String(100), nullable=True)

    roadmap = db.relationship("Roadmap", back_populates="modules")
    user_progress = db.relationship("UserProgress", backref="module", lazy="dynamic", cascade="all, delete-orphan")
    # Di dalam class Module(db.Model):
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
    url = db.Column(db.String(500))
    lesson_type = db.Column(db.String(50), default="article")
    estimated_time = db.Column(db.Integer)
    description = db.Column(db.Text, nullable=True)
    video_url = db.Column(db.String(500), nullable=True)
    user_progress = db.relationship('UserProgress', back_populates='lesson', lazy='dynamic', cascade="all, delete-orphan")

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

    chat_session = db.relationship("ChatSession", back_populates="project", uselist=False)
    submissions = db.relationship("ProjectSubmission", backref="project", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project {self.title}>"

class ProjectSubmission(db.Model):
    __tablename__ = "project_submission"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    project_link = db.Column(db.String(200), nullable=False)
    interview_score = db.Column(db.Integer)
    interview_feedback = db.Column(db.Text)
    interview_messages = db.relationship("InterviewMessage", back_populates="submission", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Submission {self.id} for Project {self.project_id}>"

class ChatSession(db.Model):
    __tablename__ = "chat_session"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    messages = db.relationship("ChatMessage", backref="session", lazy="dynamic", cascade="all, delete-orphan")
    project = db.relationship('Project', back_populates='chat_session')

    def __repr__(self):
        return f"<ChatSession {self.title}>"

class ChatMessage(db.Model):
    __tablename__ = "chat_message"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey("chat_session.id"), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f"<ChatMessage {self.id}>"

class InterviewMessage(db.Model):
    __tablename__ = "interview_message"
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey("project_submission.id"), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    submission = db.relationship("ProjectSubmission", back_populates="interview_messages")

    def __repr__(self):
        return f"<InterviewMessage {self.id}>"

# Model LearningResource dihapus karena sepertinya tidak terpakai dan bisa disederhanakan
# Model CodingSession dan CodeFile telah dihapus
    
class LearningResource(db.Model):
    __tablename__ = "learning_resource"

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey("module.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<LearningResource {self.title}>"