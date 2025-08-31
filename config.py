# config.py
import os
from dotenv import load_dotenv

# Muat variabel dari file .env
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google OAuth Credentials
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

    # BytePlus API Keys
    BYTEPLUS_ACCESS_KEY_ID = os.environ.get('BYTEPLUS_ACCESS_KEY_ID')
    BYTEPLUS_SECRET_ACCESS_KEY = os.environ.get('BYTEPLUS_SECRET_ACCESS_KEY')