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

# Inisialisasi Ekstensi di luar factory
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'routes.login' # Arahkan ke route login Anda
oauth = OAuth()
ark_client = None

# Fungsi User Loader untuk Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

# --- Konfigurasi Custom untuk Flask-Admin ---
class SecureModelView(ModelView):
    """
    ModelView dasar yang memeriksa apakah pengguna sudah login dan merupakan admin.
    """
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # Arahkan ke halaman login jika akses ditolak
        return redirect(url_for('routes.login', next=request.url))

class UserView(SecureModelView):
    """Kustomisasi tampilan untuk model User."""
    # Kolom yang ingin ditampilkan di daftar
    column_list = ('id', 'name', 'email', 'semester', 'career_path', 'is_admin')
    # Kolom yang bisa digunakan untuk mencari
    column_searchable_list = ('name', 'email')
    # Kolom yang bisa difilter
    column_filters = ('is_admin', 'semester', 'career_path')
    # Membuat kolom email bisa di-klik
    column_formatters = {
        'email': lambda view, context, model, name: Markup(f'<a href="mailto:{model.email}">{model.email}</a>')
    }

class TaskView(SecureModelView):
    """Kustomisasi tampilan untuk model Task."""
    column_list = ('id', 'title', 'author', 'due_date', 'priority', 'status')
    column_searchable_list = ('title', 'author.name')
    column_filters = ('priority', 'status', 'due_date')

class EventView(SecureModelView):
    """Kustomisasi tampilan untuk model Event."""
    column_list = ('id', 'title', 'author', 'start_time', 'end_time')
    column_searchable_list = ('title', 'author.name')
    column_filters = ('start_time',)


def create_app(config_class=Config):
    """
    App Factory untuk membuat instance aplikasi Flask.
    """
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
    from app.models import User, Roadmap, Module, Lesson, Project, ProjectSubmission, Task, Event
    admin = Admin(app, name='Farsight Admin', template_mode='bootstrap4', url='/admin')

    # Tambahkan view untuk setiap model dengan kustomisasi
    admin.add_view(UserView(User, db.session))
    admin.add_view(TaskView(Task, db.session))
    admin.add_view(EventView(Event, db.session))
    admin.add_view(SecureModelView(Roadmap, db.session))
    admin.add_view(SecureModelView(Module, db.session))
    admin.add_view(SecureModelView(Lesson, db.session))
    admin.add_view(SecureModelView(Project, db.session))
    admin.add_view(SecureModelView(ProjectSubmission, db.session, name="Submissions"))

    # 4. Daftarkan Blueprints & Perintah CLI
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)
    
    from app import commands
    app.cli.add_command(commands.ensure_admin)

    # 5. Konfigurasi Logging (untuk produksi)
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