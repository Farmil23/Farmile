# app/__init__.py

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

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'routes.login'
oauth = OAuth()
ark_client = None


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from flask import redirect, url_for, request

    # --- MULAI KONFIGURASI FLASK-ADMIN ---
    
    class SecureModelView(ModelView):
        def is_accessible(self):
            return current_user.is_authenticated and current_user.is_admin

        def inaccessible_callback(self, name, **kwargs):
            return redirect(url_for('routes.login'))
    
    class LessonView(SecureModelView):
        column_list = ('id', 'title', 'order', 'module', 'module_id')
        column_labels = {
            'module': 'Modul',
            'module_id': 'ID Modul'
        }
        
    class ModuleView(SecureModelView):
        column_list = ('id', 'title', 'description', 'order', 'career_path')
        column_exclude_list = ['lessons', 'projects']
        
        def _list_formatter_lessons(view, context, model, name):
            count = len(model.lessons) 
            return Markup(f'<a href="{url_for("lesson.index_view", search=model.title)}">{count} pelajaran</a>')
        
        column_formatters = {
            'lessons': _list_formatter_lessons
        }

    admin = Admin(app, name='Farsight Admin', template_mode='bootstrap4')

    from app.models import User, Roadmap, Module, Lesson, Project, ProjectSubmission

    admin.add_view(SecureModelView(User, db.session))
    admin.add_view(SecureModelView(Roadmap, db.session))
    
    admin.add_view(ModuleView(Module, db.session, name='Modules'))
    admin.add_view(LessonView(Lesson, db.session))
    
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

    with app.app_context():
        admin_user = User.query.filter_by(email='farmiljobs@gmail.com').first()
        if admin_user and not admin_user.is_admin:
            admin_user.is_admin = True
            db.session.commit()
            app.logger.info("User 'farmiljobs@gmail.com' berhasil diatur sebagai admin.")

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)
    
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