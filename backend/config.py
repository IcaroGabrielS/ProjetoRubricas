import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = 'chave-secreta-do-app'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'contagil-client-portal.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'chave-secreta-jwt'
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 60 * 60  # 24 horas em segundos