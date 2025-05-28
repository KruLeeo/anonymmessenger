from flask import render_template, request, flash
from flask_restful import Resource, reqparse
from flask_mail import Message
from flask_cors import CORS
import os
from app import app, mail, api
import re
from functools import lru_cache
from datetime import datetime

CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.before_first_request
def check_files():
    if not os.path.exists('forbidden_words.txt'):
        with open('forbidden_words.txt', 'w', encoding='utf-8') as f:
            f.write("# Пример файла с запрещёнными словами\n")
            f.write("плохоеслово1\n")
            f.write("оскорбление\n")
        app.logger.info("Created default forbidden_words.txt file")

@lru_cache(maxsize=1)
def load_forbidden_words():
    try:
        path = os.path.abspath('forbidden_words.txt')
        app.logger.info(f"Loading forbidden words from: {path}")
        
        with open('forbidden_words.txt', 'r', encoding='utf-8') as f:
            words = {line.strip().lower() for line in f 
                    if line.strip() and not line.startswith('#')}
            
            if not words:
                app.logger.warning("Forbidden words file is empty")
            return words
            
    except FileNotFoundError:
        app.logger.error(f"Critical: Forbidden words file not found at: {path}")
        return set()
    except Exception as e:
        app.logger.error(f"Error loading forbidden words: {str(e)}")
        return set()

def contains_forbidden_words(text):
    if not text:
        return False
    
    forbidden_words = load_forbidden_words()
    if not forbidden_words:
        return False
    
    # Нормализация текста - удаляем всё, кроме букв и цифр
    text_normalized = re.sub(r'[^\w\s]', '', text.lower())
    words_in_text = set(re.split(r'\s+', text_normalized))
    
    # Проверяем точное совпадение слов
    return not words_in_text.isdisjoint(forbidden_words)

def send_email(to, subject, template, **kwargs):
    kwargs['current_year'] = datetime.now().year
    
    msg = Message(
        subject=subject,
        recipients=[to],
        sender=app.config['MAIL_DEFAULT_SENDER'],
        html=render_template(template, **kwargs)
    )
    mail.send(msg)

message_parser = reqparse.RequestParser()
message_parser.add_argument('department', type=str, required=True)
message_parser.add_argument('message', type=str, required=True)
message_parser.add_argument('device_id', type=str, required=False)

class MessageResource(Resource):
    def post(self):
        args = message_parser.parse_args()
        
        if contains_forbidden_words(args['message']):
            return {'error': 'Не ругайся'}, 400
            
        try:
            email = app.config['DEPARTMENTS'].get(args['department'])
            if not email:
                return {'error': 'Department not found'}, 404
                
            send_email(
                to=email,
                subject=f"✉️ Анонимное сообщение для {args['department']}",
                template="email_template.html",
                department=args['department'],
                message=args['message'],
                device_info=f"Мобильное приложение ({args.get('device_id', 'unknown')})"
            )
            return {'status': 'message sent'}, 200
            
        except Exception as e:
            app.logger.error(f"Message sending error: {str(e)}")
            return {'error': str(e)}, 500

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        department = request.form.get('department')
        message = request.form.get('message')
        
        if not department or not message:
            flash('❌ Заполните все поля', 'error')
        elif contains_forbidden_words(message):
            flash('❌ Не ругайся', 'error')
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

if not hasattr(app, '_api_registered'):
    api.add_resource(MessageResource, '/messages')
    app._api_registered = True