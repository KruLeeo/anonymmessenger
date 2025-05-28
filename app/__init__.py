from flask import Flask
from flask_mail import Mail
from flask_restful import Api

app = Flask(__name__)
app.config.from_object('config.Config')
mail = Mail(app)
api = Api(app, prefix='/api/v1')

from app import routes
