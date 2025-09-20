# config.py
import os
from dotenv import load_dotenv

# Muat variabel dari file .env
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google OAuth Credentials
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

     # Ganti variabel BytePlus yang lama
    ARK_API_KEY = os.environ.get('ARK_API_KEY')
    MODEL_ENDPOINT_ID = os.environ.get('MODEL_ENDPOINT_ID')