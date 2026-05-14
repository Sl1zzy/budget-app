import os
import secrets
from PIL import Image
from flask import current_app


def save_receipt(form_picture):
    """Сохраняет загруженный файл чека и возвращает имя файла"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/uploads', picture_fn)
    
    # Оптимизация изображения если это картинка
    if f_ext.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
        output_size = (800, 800)
        i = Image.open(form_picture)
        i.thumbnail(output_size)
        i.save(picture_path)
    else:
        form_picture.save(picture_path)
    
    return picture_fn


def get_currency_rates():
    """Получает курсы валют через внешний API"""
    import requests
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/RUB', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'USD': round(data['rates']['USD'], 2),
                'EUR': round(data['rates']['EUR'], 2),
                'RUB': 1.0
            }
    except:
        pass
    
    # Резервные значения если API недоступен
    return {
        'USD': 0.011,
        'EUR': 0.010,
        'RUB': 1.0
    }


def calculate_totals(transactions):
    """Подсчитывает итоги по доходам и расходам"""
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expense = sum(t.amount for t in transactions if t.type == 'expense')
    balance = total_income - total_expense
    
    return {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance
    }