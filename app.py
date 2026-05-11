from flask import Flask, render_template, url_for, flash, redirect, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from config import Config
from models import db, User, Transaction
from forms import LoginForm, RegisterForm, TransactionForm
from utils import save_receipt, get_currency_rates, calculate_totals
from api.routes import TransactionListAPI, TransactionStatsAPI, TransactionCRUDAPI
from flask_restful import Api

# Создание приложения
app = Flask(__name__)
app.config.from_object(Config)

# Инициализация расширений
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
login_manager.login_message_category = 'info'

# Инициализация API
api = Api(app)
api.add_resource(TransactionListAPI, '/api/transactions/user/<int:user_id>')
api.add_resource(TransactionStatsAPI, '/api/transactions/stats/<int:user_id>')
api.add_resource(TransactionCRUDAPI, '/api/transactions/<int:transaction_id>')

# Создание папки для загрузок если её нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Маршруты ---

@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        transactions = Transaction.query.filter_by(user_id=current_user.id)\
            .order_by(Transaction.date_posted.desc()).limit(10).all()
        totals = calculate_totals(Transaction.query.filter_by(user_id=current_user.id).all())
        currency_rates = get_currency_rates()
    else:
        transactions = []
        totals = {'total_income': 0, 'total_expense': 0, 'balance': 0}
        currency_rates = {'USD': 0, 'EUR': 0, 'RUB': 1}
    
    return render_template('index.html', 
                           transactions=transactions, 
                           totals=totals,
                           currency_rates=currency_rates)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Проверка существования пользователя
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Пользователь с таким email уже существует.', 'danger')
            return render_template('register.html', form=form)
        
        # Создание нового пользователя
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Регистрация успешна! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash(f'Добро пожаловать, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Неверный email или пароль.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    form = TransactionForm()
    if form.validate_on_submit():
        receipt_filename = None
        
        # Обработка загруженного чека
        if form.receipt.data:
            receipt_filename = save_receipt(form.receipt.data)
        
        # Создание транзакции
        transaction = Transaction(
            amount=form.amount.data,
            type=form.type.data,
            category=form.category.data,
            description=form.description.data,
            receipt_path=receipt_filename,
            user_id=current_user.id
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash('Транзакция успешно добавлена!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_transaction.html', form=form)

@app.route('/transaction/<int:transaction_id>')
@login_required
def transaction_detail(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    
    # Проверка что транзакция принадлежит текущему пользователю
    if transaction.user_id != current_user.id:
        flash('У вас нет доступа к этой транзакции.', 'danger')
        return redirect(url_for('index'))
    
    return render_template('transaction_detail.html', transaction=transaction)


@app.route('/transaction/<int:transaction_id>/delete', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    
    # Проверка что транзакция принадлежит текущему пользователю
    if transaction.user_id != current_user.id:
        flash('У вас нет доступа к этой транзакции.', 'danger')
        return redirect(url_for('index'))
    
    db.session.delete(transaction)
    db.session.commit()
    
    flash('Транзакция успешно удалена!', 'success')
    return redirect(url_for('index'))

# --- Обработчики ошибок ---

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# --- Инициализация БД ---

@app.cli.command('init-db')
def init_db():
    """Создает все таблицы в базе данных"""
    db.create_all()
    print('База данных инициализирована.')

# --- Запуск ---

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))