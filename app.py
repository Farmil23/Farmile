# app.py
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, redirect, url_for, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from authlib.integrations.flask_client import OAuth

# --- Inisialisasi Aplikasi & Konfigurasi ---
app = Flask(__name__)
app.config.from_object(Config)

# --- KONFIGURASI LOGGER ---
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Farsight app startup')

# --- Inisialisasi Ekstensi ---
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Halaman yang dituju jika user mencoba akses halaman terproteksi tanpa login
oauth = OAuth(app)

# --- Definisi Model Database ---
from models import User

# --- User Loader untuk Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Konfigurasi Authlib untuk Google ---
oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# --- Rute Utama ---
@app.route('/')
def index():
    return render_template('index.html', title='Selamat Datang')

# --- Rute untuk Autentikasi ---
@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/auth')
def auth():
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')
    
    user = User.query.filter_by(google_id=user_info['sub']).first()
    
    if not user:
        user = User(
            google_id=user_info['sub'],
            name=user_info['name'],
            email=user_info['email'],
            profile_pic=user_info['picture']
        )
        db.session.add(user)
        db.session.commit()
    
    login_user(user)
    return redirect(url_for('profile'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- Rute untuk Halaman Pengguna ---
@app.route('/profile')
@login_required
def profile():
    # Untuk sementara, hanya menampilkan nama. Nanti akan dikembangkan di Fase 2
    return render_template('profile.html', user=current_user)

# --- Rute Tes untuk Error 500 ---
@app.route('/test500')
def test_500():
    raise RuntimeError("Ini adalah error tes internal!")

# --- ERROR HANDLERS ---
@app.errorhandler(404)
def not_found_error(error):
    app.logger.warning(f'Not Found error at {request.path}')
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(f'Internal Server Error: {error}', exc_info=True)
    return render_template('errors/500.html'), 500

# --- Jalankan Aplikasi ---
if __name__ == '__main__':
    app.run(debug=True)