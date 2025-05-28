from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_mail import Mail, Message
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object('config.Config')
mail = Mail(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})
api = Api(app, prefix='/api/v1')

message_parser = reqparse.RequestParser()
message_parser.add_argument('department', type=str, required=True, help='Department is required')
message_parser.add_argument('message', type=str, required=True, help='Message is required')
message_parser.add_argument('device_id', type=str, required=False)

class MessageResource(Resource):
    def post(self):
        args = message_parser.parse_args()
        try:
            email = app.config['DEPARTMENTS'].get(args['department'])
            if not email:
                return {'error': 'Department not found'}, 404
            msg = Message(
                subject=f"Анонимное сообщение от мобильного приложения ({args.get('device_id', 'unknown')})",
                recipients=[email],
                body=f"Кафедра: {args['department']}\n\nСообщение:\n{args['message']}",
                sender=app.config['MAIL_DEFAULT_SENDER']
            )
            mail.send(msg)
            return {'status': 'message sent'}, 200
        except Exception as e:
            return {'error': str(e)}, 500

api.add_resource(MessageResource, '/messages')

if __name__ == "__main__":
    app.run(debug=True)
