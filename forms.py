from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, NumberRange
from flask_wtf.file import FileField, FileAllowed


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Зарегистрироваться')


class TransactionForm(FlaskForm):
    amount = FloatField('Сумма', validators=[DataRequired(), NumberRange(min=0.01)])
    type = SelectField('Тип', choices=[('income', 'Доход'), ('expense', 'Расход')], 
                       validators=[DataRequired()])
    category = StringField('Категория', validators=[DataRequired(), Length(min=2, max=50)])
    description = TextAreaField('Описание', validators=[Length(max=200)])
    receipt = FileField('Чек (изображение или PDF)', 
                        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'pdf'], 
                        'Только изображения и PDF!')])
    submit = SubmitField('Добавить запись')