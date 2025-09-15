import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, redirect, url_for, request, jsonify
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from authlib.integrations.flask_client import OAuth
from byteplussdkarkruntime import Ark
from flask_migrate import Migrate
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from apscheduler.schedulers.background import BackgroundScheduler
from markupsafe import Markup, escape
from datetime import datetime
import pytz
from sqlalchemy import func, cast, String

# Inisialisasi Ekstensi di luar factory
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

# ======================= KELAS-KELAS VIEW UNTUK ADMIN (VERSI BARU) =======================

class UserView(SecureModelView):
    column_list = ('id', 'name', 'email', 'semester', 'career_path', 'is_admin')
    column_searchable_list = ('name', 'email')
    column_filters = ('is_admin', 'semester', 'career_path')
    column_formatters = {
        'email': lambda view, context, model, name: Markup(f'<a href="mailto:{model.email}">{model.email}</a>')
    }

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
    form_ajax_refs = {
        'module': { 'fields': ['title'], 'page_size': 10 }
    }

class ProjectView(SecureModelView):
    column_list = ('title', 'module', 'difficulty', 'is_challenge')
    column_searchable_list = ('title', 'description', 'tech_stack')
    column_filters = ('difficulty', 'is_challenge', 'module.title')
    form_columns = (
        'module', 'title', 'description', 'difficulty', 'is_challenge', 
        'project_goals', 'tech_stack', 'evaluation_criteria', 'resources'
    )
    form_ajax_refs = {
        'module': { 'fields': ['title'], 'page_size': 10 }
    }

class ModuleView(SecureModelView):
    column_list = ('title', 'roadmap', 'career_path', 'order', 'level')
    column_searchable_list = ('title',)
    column_filters = ('career_path', 'level', 'roadmap.title')
    form_columns = ('roadmap', 'user', 'title', 'order', 'career_path', 'level')
    form_ajax_refs = {
        'roadmap': { 'fields': ['title'], 'page_size': 10 },
        'user': { 'fields': ['name', 'email'], 'page_size': 10 }
    }

class SubmissionView(SecureModelView):
    column_list = ('id', 'project', 'author', 'interview_score', 'project_link')
    column_searchable_list = ('project.title', 'author.name')
    column_filters = ('interview_score',)
    form_columns = ('project', 'author', 'project_link', 'interview_score', 'interview_feedback')
    form_ajax_refs = {
        'project': { 'fields': ['title'], 'page_size': 10 },
        'author': { 'fields': ['name', 'email'], 'page_size': 10 }
    }

class UserProjectView(SecureModelView):
    column_list = ('id', 'user', 'project', 'status', 'started_at')
    column_searchable_list = ('user.name', 'project.title')
    column_filters = ('status',)
    form_columns = ('user', 'project', 'status', 'started_at', 'reflection')
    form_ajax_refs = {
        'user': { 'fields': ['name', 'email'], 'page_size': 10 },
        'project': { 'fields': ['title'], 'page_size': 10 }
    }

class AnalyticsView(BaseView):
    @expose('/')
    def index(self):
        from .models import User, UserActivityLog, Lesson
        feature_usage = db.session.query(
            UserActivityLog.action, 
            func.count(UserActivityLog.action)
        ).group_by(UserActivityLog.action).all()
        top_users = db.session.query(
            User.name, 
            func.count(UserActivityLog.id).label('total_activities')
        ).join(UserActivityLog).group_by(User.name).order_by(db.desc('total_activities')).limit(10).all()

        # ---> PERBAIKAN UTAMA ADA DI SINI <---
        # Mengganti .astext dengan func.json_extract yang didukung SQLite
        top_lessons = db.session.query(
            Lesson.title,
            func.count(UserActivityLog.id).label('view_count')
        ).join(UserActivityLog, func.json_extract(UserActivityLog.details, '$.lesson_id') == cast(Lesson.id, String)) \
         .filter(UserActivityLog.action == 'viewed_lesson') \
         .group_by(Lesson.title).order_by(db.desc('view_count')).limit(10).all()
        # ---> AKHIR DARI PERBAIKAN <---

        return self.render('admin/analytics_index.html', 
                           feature_usage=feature_usage,
                           top_users=top_users,
                           top_lessons=top_lessons)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('routes.login', next=request.url))

# ======================= AKHIR DARI KELAS VIEW =======================

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

    oauth.register(
        name='google',
        client_id=app.config.get('GOOGLE_CLIENT_ID'),
        client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
    
    global ark_client
    try:
        api_key = app.config.get('ARK_API_KEY')
        if not api_key: raise ValueError("ARK_API_KEY not found in config.")
        os.environ['ARK_API_KEY'] = api_key
        ark_client = Ark(base_url="https://ark.ap-southeast.bytepluses.com/api/v3")
        app.ark_client = ark_client
        app.logger.info("BytePlus Ark client initialized successfully!")
    except Exception as e:
        app.logger.error(f"Failed to initialize BytePlus Ark client: {e}")
        ark_client = None

    from app.models import (User, Roadmap, Module, Lesson, Project, ProjectSubmission, 
                            Task, Event, Notification, UserProject, UserActivityLog)
    
    admin = Admin(app, name='Farsight Admin', template_mode='bootstrap4', url='/admin')

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
        app.logger.info('Farsight app startup')

    return app