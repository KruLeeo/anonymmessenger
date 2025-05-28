import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.yandex.ru')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 465))
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    DEPARTMENTS = {
        "math": "tkach.i.i.2.22@gmail.com",
        "physics": "physics@university.edu",
        "cs": "cs@university.edu"
    }
