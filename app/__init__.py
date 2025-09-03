# app/__init__.py

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, redirect, url_for, request # <-- Tambahkan url_for & request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user # <-- Tambahkan current_user
from authlib.integrations.flask_client import OAuth
from byteplussdkarkruntime import Ark
from flask_migrate import Migrate

# --- TAMBAHKAN IMPORT UNTUK FLASK-ADMIN ---
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
# -----------------------------------------

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'routes.login'
oauth = OAuth()
ark_client = None


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- MULAI KONFIGURASI FLASK-ADMIN ---

    # (OPSIONAL TAPI DIANJURKAN) Impor Model di sini agar lebih rapi
    from app.models import User, Roadmap, Module, Lesson, Project, ProjectSubmission

    # 1. Buat class View yang aman
    class SecureModelView(ModelView):
        def is_accessible(self):
            # Cek apakah user sudah login DAN memiliki peran admin
            # (Lihat cara menambahkan is_admin di bawah)
            return current_user.is_authenticated and current_user.is_admin

        def inaccessible_callback(self, name, **kwargs):
            # Jika user tidak punya akses, redirect ke halaman login
            return redirect(url_for('routes.login'))

    # 2. Inisialisasi Admin Panel
    admin = Admin(app, name='Farsight Admin', template_mode='bootstrap4')

    # 3. Tambahkan setiap model ke Admin Panel
    admin.add_view(SecureModelView(User, db.session))
    admin.add_view(SecureModelView(Roadmap, db.session))
    admin.add_view(SecureModelView(Module, db.session))
    admin.add_view(SecureModelView(Lesson, db.session))
    admin.add_view(SecureModelView(Project, db.session))
    admin.add_view(SecureModelView(ProjectSubmission, db.session, name="Submissions"))

    # --- SELESAI KONFIGURASI FLASK-ADMIN ---
    
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

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    oauth.init_app(app)

    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)
    
    # Konfigurasi Logger
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

from app import models

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))
