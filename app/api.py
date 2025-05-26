from flask_restful import Api, Resource, reqparse
from flask import jsonify
from app import app, mail
from flask_mail import Message
from flask_cors import CORS

# Включите CORS для мобильных приложений
CORS(app, resources={r"/api/*": {"origins": "*"}})

api = Api(app, prefix='/api/v1')

# Парсер для входящих данных
message_parser = reqparse.RequestParser()
message_parser.add_argument('department', type=str, required=True, help='Department is required')
message_parser.add_argument('message', type=str, required=True, help='Message is required')
message_parser.add_argument('device_id', type=str, required=False)

class MessageResource(Resource):
    def post(self):
        args = message_parser.parse_args()
        
        try:
            # Логика отправки email (как в предыдущем примере)
            email = app.config['DEPARTMENTS'].get(args['department'])
            if not email:
                return {'error': 'Department not found'}, 404
            
            msg = Message(
                subject=f"Анонимное сообщение от мобильного приложения ({args.get('device_id', 'unknown')}",
                recipients=[email],
                body=f"Кафедра: {args['department']}\n\nСообщение:\n{args['message']}",
                sender=app.config['MAIL_DEFAULT_SENDER']
            )
            mail.send(msg)
            
            # Логирование в базу данных (опционально)
            # save_to_db(args['message'], args['department'], args.get('device_id'))
            
            return {'status': 'message sent'}, 200
        
        except Exception as e:
            return {'error': str(e)}, 500

# Регистрация ресурсов
api.add_resource(MessageResource, '/messages')