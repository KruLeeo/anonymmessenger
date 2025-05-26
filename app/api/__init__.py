from flask_restful import Api
from .resources import MessageResource

api = Api()

def init_api(app):
    api.add_resource(MessageResource, '/api/v1/messages')
    api.init_app(app)