from datetime import timedelta


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = '57e19ea558d4967a552d03deece34a70'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    ENV="development"
    DEVELOPMENT=True
    DEBUG=True

DATABASE='database/database.db'