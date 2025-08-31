# app/__init__.py
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth

# Inisialisasi Ekstensi
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'routes.login'
oauth = OAuth()

def create_app(config_class=Config):
    # Inisialisasi Aplikasi & Konfigurasi
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Hubungkan ekstensi dengan aplikasi
    db.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)

    # --- TAMBAHKAN BLOK INI ---
    # Daftarkan Klien OAuth (Google)
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    # --- AKHIR BLOK TAMBAHAN ---

    # Daftarkan Blueprint untuk rute
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)
    
    # Konfigurasi Logger
    # (kode logger Anda tetap di sini)
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