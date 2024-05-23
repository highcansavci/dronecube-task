from pathlib import Path

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mailman import Mail
import secrets

from minio import Minio

BASE_DIR = Path(__file__).parent


class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(BASE_DIR.joinpath('db.sqlite'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = secrets.token_urlsafe(16)
    RESET_PASS_TOKEN_MAX_AGE = 10000
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'drone.cube.reset@gmail.com'
    MAIL_PASSWORD = 'oqikhksxfryfjmfq'
    UPLOAD_FOLDER = "uploads"
    MINIO_ENDPOINT = 'localhost:9000'
    MINIO_ACCESS_KEY = 'minioadmin'
    MINIO_SECRET_KEY = 'minioadmin'
    MINIO_BUCKET = 'dronecube'
    minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
    UTC = 3
    IMAGE_WIDTH = 512
    IMAGE_HEIGHT = 512
    IMAGE_CHANNEL = 3
    NUM_IMAGES = 5
    db = SQLAlchemy()
    mail = Mail()
    login_manager = LoginManager()
