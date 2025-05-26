from datetime import datetime
from flask import render_template, request, flash, current_app
from flask_restful import Resource, reqparse
from flask_mail import Message
from app import app, mail, api  # Импортируем api из app

# Парсер для API-запросов
message_parser = reqparse.RequestParser()
message_parser.add_argument('department', type=str, required=True)
message_parser.add_argument('message', type=str, required=True)
message_parser.add_argument('device_id', type=str, required=False)

def send_email(to, subject, template, **kwargs):
    kwargs['current_year'] = datetime.now().year
    
    msg = Message(
        subject=subject,
        recipients=[to],
        sender=app.config['MAIL_DEFAULT_SENDER'],
        html=render_template(template, **kwargs)
    )
    mail.send(msg)

class MessageResource(Resource):
    def post(self):
        args = message_parser.parse_args()
        
        try:
            email = current_app.config['DEPARTMENTS'].get(args['department'])
            if not email:
                return {'error': 'Department not found'}, 404
            
            send_email(
                to=email,
                subject=f"📱 Анонимное сообщение (мобильное приложение)",
                template="email_template.html",
                department=args['department'],
                message=args['message'],
                device_info=args.get('device_id', 'Не указано')
            )
            
            return {'status': 'success', 'message': 'Сообщение отправлено'}, 200
        
        except Exception as e:
            current_app.logger.error(f"API Error: {str(e)}")
            return {'error': str(e)}, 500

# Регистрация API-ресурса должна происходить только один раз
if not hasattr(app, '_api_registered'):  # Проверяем, не зарегистрирован ли уже ресурс
    api.add_resource(MessageResource, '/api/v1/messages')
    app._api_registered = True  # Помечаем как зарегистрированное

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        department = request.form.get('department')
        message = request.form.get('message')
        
        if not department or not message:
            flash('❌ Заполните все поля', 'error')
        else:
            email = app.config['DEPARTMENTS'].get(department)
            if email:
                try:
                    send_email(
                        to=email,
                        subject=f"✉️ Анонимное сообщение для {department}",
                        template="email_template.html",
                        department=department,
                        message=message,
                        device_info="Веб-форма"
                    )
                    flash('✅ Сообщение отправлено!', 'success')
                except Exception as e:
                    flash(f'❌ Ошибка: {str(e)}', 'error')
            else:
                flash('❌ Кафедра не найдена', 'error')
    
    return render_template('index.html', departments=app.config['DEPARTMENTS'].keys())