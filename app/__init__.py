# File: app/__init__.py

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, redirect, url_for, request, jsonify
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from authlib.integrations.flask_client import OAuth
# --- PERBAIKAN 1: Ganti import yang lama dengan yang ini ---
from byteplus.ark.runtime import Ark
# ---------------------------------------------------------
from flask_migrate import Migrate
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from apscheduler.schedulers.background import BackgroundScheduler
from markupsafe import Markup, escape
from datetime import datetime, timedelta
import pytz
from sqlalchemy import func, cast, String
import json

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'routes.login'

@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith('/api/'):
        return jsonify(error="Authentication required. Please log in again."), 401
    return redirect(url_for('routes.login'))

oauth = OAuth()
ark_client = None

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('routes.login', next=request.url))

class UserView(SecureModelView):
    column_list = ('id', 'name', 'email', 'semester', 'career_path', 'is_admin')
    column_searchable_list = ('name', 'email')
    column_filters = ('is_admin', 'semester', 'career_path')
    column_formatters = {'email': lambda view, context, model, name: Markup(f'<a href="mailto:{model.email}">{model.email}</a>')}

class TaskView(SecureModelView):
    column_list = ('id', 'title', 'author', 'due_date', 'priority', 'status')
    column_searchable_list = ('title', 'author.name')
    column_filters = ('priority', 'status', 'due_date')

class EventView(SecureModelView):
    column_list = ('id', 'title', 'author', 'start_time', 'end_time')
    column_searchable_list = ('title', 'author.name')
    column_filters = ('start_time',)

class LessonView(SecureModelView):
    column_list = ('order', 'title', 'module', 'lesson_type', 'estimated_time')
    column_searchable_list = ('title', 'description')
    column_filters = ('lesson_type', 'module.title')
    form_columns = ('module', 'title', 'description', 'order', 'lesson_type', 'url', 'estimated_time', 'content', 'quiz')
    form_ajax_refs = {'module': {'fields': ['title'], 'page_size': 10}}

class ProjectView(SecureModelView):
    column_list = ('title', 'module', 'difficulty', 'is_challenge')
    column_searchable_list = ('title', 'description', 'tech_stack')
    column_filters = ('difficulty', 'is_challenge', 'module.title')
    form_columns = ('module', 'title', 'description', 'difficulty', 'is_challenge', 'project_goals', 'tech_stack', 'evaluation_criteria', 'resources')
    form_ajax_refs = {'module': {'fields': ['title'], 'page_size': 10}}

class ModuleView(SecureModelView):
    column_list = ('title', 'roadmap', 'career_path', 'order', 'level')
    column_searchable_list = ('title',)
    column_filters = ('career_path', 'level', 'roadmap.title')
    form_columns = ('roadmap', 'user', 'title', 'order', 'career_path', 'level')
    form_ajax_refs = {'roadmap': {'fields': ['title'], 'page_size': 10}, 'user': {'fields': ['name', 'email'], 'page_size': 10}}

class SubmissionView(SecureModelView):
    column_list = ('id', 'project', 'author', 'interview_score', 'project_link')
    column_searchable_list = ('project.title', 'author.name')
    column_filters = ('interview_score',)
    form_columns = ('project', 'author', 'project_link', 'interview_score', 'interview_feedback')
    form_ajax_refs = {'project': {'fields': ['title'], 'page_size': 10}, 'author': {'fields': ['name', 'email'], 'page_size': 10}}

class UserProjectView(SecureModelView):
    column_list = ('id', 'user', 'project', 'status', 'started_at')
    column_searchable_list = ('user.name', 'project.title')
    column_filters = ('status',)
    form_columns = ('user', 'project', 'status', 'started_at', 'reflection')
    form_ajax_refs = {'user': {'fields': ['name', 'email'], 'page_size': 10}, 'project': {'fields': ['title'], 'page_size': 10}}

class CertificateView(SecureModelView):
    column_list = ('id', 'user', 'roadmap', 'career_path', 'issued_at')
    column_searchable_list = ('user.name', 'user.email', 'career_path')
    column_filters = ('career_path', 'issued_at')
    form_columns = ('user', 'roadmap', 'career_path', 'total_hours', 'projects_completed_json')
    form_ajax_refs = {
        'user': {'fields': ['name', 'email'], 'page_size': 10},
        'roadmap': {'fields': ['title'], 'page_size': 10}
    }

class JobApplicationView(SecureModelView):
    can_create = True
    can_edit = True
    can_delete = True
    
    column_list = ('id', 'author', 'company_name', 'position', 'status', 'application_date', 'resume_used')
    column_searchable_list = ('author.name', 'company_name', 'position')
    column_filters = ('status', 'application_date', 'author.name')
    
    form_columns = ('author', 'company_name', 'position', 'status', 'application_date', 'work_model', 'job_link', 'notes', 'resume_used')
    
    form_ajax_refs = {
        'author': {
            'fields': ['name', 'email'],
            'page_size': 10
        },
        'resume_used': {
            'fields': ['original_filename'],
            'page_size': 10
        }
    }

class AnalyticsView(BaseView):
    @expose('/')
    def index(self):
        from .models import User, UserActivityLog, Lesson, Project, ProjectSubmission, UserResume, JobApplication, JobCoachMessage, AnalyticsSnapshot
        
        feature_usage_query = db.session.query(UserActivityLog.action, func.count(UserActivityLog.action)).group_by(UserActivityLog.action).all()
        feature_usage_chart_data = {"labels": [row[0] for row in feature_usage_query], "data": [row[1] for row in feature_usage_query]}
        
        top_users = db.session.query(User.name, func.count(UserActivityLog.id).label('total_activities')).join(UserActivityLog).group_by(User.name).order_by(db.desc('total_activities')).limit(5).all()
        top_lessons = db.session.query(Lesson.title, func.count(UserActivityLog.id).label('view_count')).join(UserActivityLog, func.json_extract(UserActivityLog.details, '$.lesson_id') == cast(Lesson.id, String)).filter(UserActivityLog.action == 'viewed_lesson').group_by(Lesson.title).order_by(db.desc('view_count')).limit(5).all()
        top_projects = db.session.query(Project.title, func.count(ProjectSubmission.id).label('submission_count')).join(ProjectSubmission).group_by(Project.title).order_by(db.desc('submission_count')).limit(5).all()
        
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        daily_activity_query = db.session.query(func.date(UserActivityLog.timestamp), func.count(UserActivityLog.id)).filter(UserActivityLog.timestamp >= seven_days_ago).group_by(func.date(UserActivityLog.timestamp)).order_by(func.date(UserActivityLog.timestamp)).all()
        
        daily_activity_chart_data = {
            "labels": [datetime.strptime(date_str, '%Y-%m-%d').strftime('%d %b') for date_str, count in daily_activity_query],
            "data": [count for date_str, count in daily_activity_query]
        }

        total_resumes_analyzed = db.session.query(func.count(UserResume.id)).scalar()
        total_jobs_tracked = db.session.query(func.count(JobApplication.id)).scalar()
        total_coach_sessions = db.session.query(func.count(func.distinct(JobCoachMessage.application_id))).scalar()
        
        job_status_distribution_query = db.session.query(JobApplication.status, func.count(JobApplication.status)).group_by(JobApplication.status).all()
        job_status_chart_data = {"labels": [row[0] for row in job_status_distribution_query], "data": [row[1] for row in job_status_distribution_query]}
        
        saved_snapshots = AnalyticsSnapshot.query.order_by(AnalyticsSnapshot.created_at.desc()).all()

        return self.render('admin/analytics_index.html', 
                           feature_usage_chart_data=feature_usage_chart_data,
                           daily_activity_chart_data=daily_activity_chart_data,
                           top_users=top_users,
                           top_lessons=top_lessons,
                           top_projects=top_projects,
                           total_resumes_analyzed=total_resumes_analyzed,
                           total_jobs_tracked=total_jobs_tracked,
                           total_coach_sessions=total_coach_sessions,
                           job_status_chart_data=job_status_chart_data,
                           saved_snapshots=saved_snapshots)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('routes.login', next=request.url))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    oauth.init_app(app)

    def fromisoformat_filter(s):
        if s: return datetime.fromisoformat(s.replace('Z', '+00:00'))
        return s
    def localdatetime_filter(dt, fmt="%d %B %Y, %H:%M"):
        if dt is None: return ""
        if dt.tzinfo is None: dt = pytz.utc.localize(dt)
        local_zone = pytz.timezone('Asia/Jakarta')
        return dt.astimezone(local_zone).strftime(fmt)
    def nl2br_filter(s):
        if s: return Markup(escape(s).replace('\\n', '<br>\\n'))
        return s
    app.jinja_env.filters['fromisoformat'] = fromisoformat_filter
    app.jinja_env.filters['localdatetime'] = localdatetime_filter
    app.jinja_env.filters['nl2br'] = nl2br_filter

    oauth.register(name='google', client_id=app.config.get('GOOGLE_CLIENT_ID'), client_secret=app.config.get('GOOGLE_CLIENT_SECRET'), server_metadata_url='https://accounts.google.com/.well-known/openid-configuration', client_kwargs={'scope': 'openid email profile'})
    
    # --- PERBAIKAN 2: Ganti seluruh blok inisialisasi Ark Client ---
    global ark_client
    try:
        api_key = app.config.get('ARK_API_KEY')
        if not api_key: raise ValueError("ARK_API_KEY not found in config.")
        
        # Inisialisasi yang benar
        ark_client = Ark(
            api_key=api_key,
            base_url="https://ark.ap-southeast.bytepluses.com/api/v3"
        )
        
        app.ark_client = ark_client
        app.logger.info("BytePlus Ark client initialized successfully!")
    except Exception as e:
        app.logger.error(f"Failed to initialize BytePlus Ark client: {e}")
        ark_client = None
    # -------------------------------------------------------------

    from app.models import (User, Roadmap, Module, Lesson, Project, ProjectSubmission, Task, Event, Notification, UserProject, UserActivityLog, UserResume, JobApplication, JobCoachMessage, AnalyticsSnapshot, Certificate, UserProgress)
    
    @app.context_processor
    def inject_progress():
        if current_user.is_authenticated and current_user.career_path:
            all_modules_in_path = Module.query.filter_by(career_path=current_user.career_path).all()
            all_lesson_ids_in_path = {lesson.id for module in all_modules_in_path for lesson in module.lessons}
            all_project_ids_in_path = {project.id for module in all_modules_in_path for project in module.projects}
            total_items = len(all_lesson_ids_in_path) + len(all_project_ids_in_path)

            completed_lessons_in_path = UserProgress.query.join(Lesson).join(Module).filter(
                UserProgress.user_id == current_user.id,
                Module.career_path == current_user.career_path
            ).count()

            submitted_projects_in_path = ProjectSubmission.query.join(Project).join(Module).filter(
                ProjectSubmission.user_id == current_user.id,
                Module.career_path == current_user.career_path
            ).count()
            
            completed_items = completed_lessons_in_path + submitted_projects_in_path

            progress_percentage = 0
            if total_items > 0:
                progress_percentage = min(100, int((completed_items / total_items) * 100))
            
            return dict(progress=progress_percentage)
        
        return dict(progress=0)

    admin = Admin(app, name='Farmile Admin', template_mode='bootstrap4', url='/admin')

    admin.add_view(UserView(User, db.session))
    admin.add_view(TaskView(Task, db.session))
    admin.add_view(EventView(Event, db.session))
    admin.add_view(LessonView(Lesson, db.session))
    admin.add_view(ProjectView(Project, db.session))
    admin.add_view(ModuleView(Module, db.session))
    admin.add_view(SubmissionView(ProjectSubmission, db.session, name="Submissions"))
    admin.add_view(UserProjectView(UserProject, db.session))
    admin.add_view(SecureModelView(Roadmap, db.session))
    admin.add_view(SecureModelView(Notification, db.session))
    
    admin.add_view(JobApplicationView(JobApplication, db.session, name="Job Applications"))
    
    admin.add_view(CertificateView(Certificate, db.session))
    admin.add_view(AnalyticsView(name='Analytics', endpoint='analytics'))
    
    try:
        from app.scheduler_jobs import check_reminders
        scheduler = BackgroundScheduler(daemon=True)
        scheduler.add_job(check_reminders, 'interval', seconds=60, args=[app])
        scheduler.start()
        app.logger.info("Notification scheduler started successfully.")
    except Exception as e:
        app.logger.error(f"Failed to start scheduler: {e}")

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)
    from app import commands
    app.cli.add_command(commands.ensure_admin)

    if not app.debug and not app.testing:
        if not os.path.exists('logs'): os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Farmile app startup')

    return app