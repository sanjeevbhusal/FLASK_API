import os

from dotenv import load_dotenv
load_dotenv()

uri = os.environ["DATABASE_URI"]
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)


class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # MAIL_SERVER = "smtp.mailtrap.io"
    # MAIL_PORT = 2525
    # MAIL_USE_TLS = True 
    # MAIL_USERNAME = os.environ["MAIL_USERNAME"]
    # MAIL_PASSWORD = os.environ["MAIL_PASSWORD"]
    # MAIL_DEFAULT_SENDER = os.environ["MAIL_USERNAME"]
    # MAIL_USE_SSL = False
    MAIL_SERVER='smtp.mailtrap.io'
    MAIL_PORT = 2525
    MAIL_USERNAME = '7333153070b432'
    MAIL_PASSWORD = 'ce7347484a0931'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    
class TestConfig :
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING =  True
    MAIL_SERVER = "smtp.mailtrap.io"
    MAIL_PORT = 2525
    MAIL_USE_TLS = True 
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME")
    
    
