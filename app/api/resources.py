from flask_restful import Resource, reqparse
from flask import current_app
from flask_mail import Message

message_parser = reqparse.RequestParser()
message_parser.add_argument('department', type=str, required=True)
message_parser.add_argument('message', type=str, required=True)
message_parser.add_argument('device_id', type=str, required=False)

class MessageResource(Resource):
    def post(self):
        args = message_parser.parse_args()
        
        try:
            email = current_app.config['DEPARTMENTS'].get(args['department'])
            if not email:
                return {'error': 'Department not found'}, 404
            
            msg = Message(
                subject=f"Анонимное сообщение от мобильного приложения",
                recipients=[email],
                body=f"Кафедра: {args['department']}\n\nСообщение:\n{args['message']}",
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            current_app.extensions['mail'].send(msg)
            
            return {'status': 'message sent'}, 200
        
        except Exception as e:
            return {'error': str(e)}, 500