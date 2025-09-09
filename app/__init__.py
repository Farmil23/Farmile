import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, redirect, url_for, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from authlib.integrations.flask_client import OAuth
from byteplussdkarkruntime import Ark
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from apscheduler.schedulers.background import BackgroundScheduler

# Import tambahan untuk filter Jinja2
from markupsafe import Markup, escape
from datetime import datetime
import pytz

# Inisialisasi Ekstensi di luar factory
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'routes.login'
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
    form_columns = ('module', 'title', 'description', 'order', 'lesson_type', 'url', 'estimated_time')
    form_ajax_refs = {
        'module': {
            'fields': ['title'],
            'page_size': 10
        }
    }

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inisialisasi Ekstensi
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    oauth.init_app(app)

    # Filter Jinja2 Kustom
    def fromisoformat_filter(s):
        if s:
            return datetime.fromisoformat(s.replace('Z', '+00:00'))
        return s

    def localdatetime_filter(dt, fmt="%d %B %Y, %H:%M"):
        if dt is None:
            return ""
        utc_zone = pytz.utc
        local_zone = pytz.timezone('Asia/Jakarta')
        utc_dt = dt.replace(tzinfo=utc_zone)
        local_dt = utc_dt.astimezone(local_zone)
        return local_dt.strftime(fmt)

    def nl2br_filter(s):
        if s:
            return Markup(escape(s).replace('\n', '<br>\n'))
        return s
    
    app.jinja_env.filters['fromisoformat'] = fromisoformat_filter
    app.jinja_env.filters['localdatetime'] = localdatetime_filter
    app.jinja_env.filters['nl2br'] = nl2br_filter

    # Konfigurasi Klien Eksternal (OAuth & AI)
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
        app.logger.info("BytePlus Ark client initialized successfully!")
    except Exception as e:
        app.logger.error(f"Failed to initialize BytePlus Ark client: {e}")
        ark_client = None

    # Konfigurasi Flask-Admin
    from app.models import User, Roadmap, Module, Lesson, Project, ProjectSubmission, Task, Event, Notification, UserProject
    admin = Admin(app, name='Farsight Admin', template_mode='bootstrap4', url='/admin')

    admin.add_view(UserView(User, db.session))
    admin.add_view(TaskView(Task, db.session))
    admin.add_view(EventView(Event, db.session))
    admin.add_view(LessonView(Lesson, db.session))
    admin.add_view(SecureModelView(Roadmap, db.session))
    admin.add_view(SecureModelView(Module, db.session))
    admin.add_view(SecureModelView(Project, db.session))
    admin.add_view(SecureModelView(ProjectSubmission, db.session, name="Submissions"))
    admin.add_view(SecureModelView(Notification, db.session))
    admin.add_view(SecureModelView(UserProject, db.session)) # Memastikan UserProject ada di admin

    # Inisialisasi Scheduler Notifikasi
    try:
        from app.scheduler_jobs import check_reminders
        scheduler = BackgroundScheduler(daemon=True)
        scheduler.add_job(check_reminders, 'interval', seconds=60, args=[app])
        scheduler.start()
        app.logger.info("Notification scheduler started successfully.")
    except ImportError:
        app.logger.warning("scheduler_jobs.py not found, scheduler not started.")
    except Exception as e:
        app.logger.error(f"Failed to start scheduler: {e}")

    # Daftarkan Blueprints & Perintah CLI
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)
    
    from app import commands
    app.cli.add_command(commands.ensure_admin)

    # Konfigurasi Logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Farsight app startup')

    return app