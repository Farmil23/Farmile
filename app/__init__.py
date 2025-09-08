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
from markupsafe import Markup
from apscheduler.schedulers.background import BackgroundScheduler

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
    """Kustomisasi tampilan untuk model Lesson."""
    column_list = ('order', 'title', 'module', 'lesson_type', 'estimated_time')
    column_searchable_list = ('title', 'description')
    column_filters = ('lesson_type', 'module.title')
    form_columns = ('module', 'title', 'description', 'order', 'lesson_type', 'url', 'estimated_time')
    form_ajax_refs = {
        'module': {
            'fields': ['title'], # Menggunakan 'title' sesuai model Module Anda
            'page_size': 10
        }
    }

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 1. Inisialisasi Ekstensi
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    oauth.init_app(app)

    # 2. Konfigurasi Klien Eksternal (OAuth & AI)
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
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

    # 3. Konfigurasi Flask-Admin
    from app.models import User, Roadmap, Module, Lesson, Project, ProjectSubmission, Task, Event, Notification
    admin = Admin(app, name='Farsight Admin', template_mode='bootstrap4', url='/admin')

    # Tambahkan view untuk setiap model dengan kustomisasi
    admin.add_view(UserView(User, db.session))
    admin.add_view(TaskView(Task, db.session))
    admin.add_view(EventView(Event, db.session))
    admin.add_view(LessonView(Lesson, db.session)) # <-- Menggunakan view yang sudah benar
    admin.add_view(SecureModelView(Roadmap, db.session))
    admin.add_view(SecureModelView(Module, db.session))
    admin.add_view(SecureModelView(Project, db.session))
    admin.add_view(SecureModelView(ProjectSubmission, db.session, name="Submissions"))
    admin.add_view(SecureModelView(Notification, db.session))

    # 4. Inisialisasi Scheduler Notifikasi
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

    # 5. Daftarkan Blueprints & Perintah CLI
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)
    
    from app import commands
    app.cli.add_command(commands.ensure_admin)

    # 6. Konfigurasi Logging
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