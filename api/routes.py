from flask_restful import Resource, Api
from models import Transaction, User, db
from flask import jsonify, request
from datetime import datetime


class TransactionListAPI(Resource):
    def get(self, user_id):
        """Получить все транзакции пользователя"""
        user = User.query.get_or_404(user_id)
        transactions = Transaction.query.filter_by(user_id=user_id)\
            .order_by(Transaction.date_posted.desc()).all()
        
        return {
            'user_id': user_id,
            'username': user.username,
            'transactions': [
                {
                    'id': t.id,
                    'amount': t.amount,
                    'type': t.type,
                    'category': t.category,
                    'description': t.description,
                    'date_posted': t.date_posted.isoformat(),
                    'has_receipt': bool(t.receipt_path)
                }
                for t in transactions
            ]
        }


class TransactionStatsAPI(Resource):
    def get(self, user_id):
        """Получить статистику по транзакциям пользователя"""
        user = User.query.get_or_404(user_id)
        transactions = Transaction.query.filter_by(user_id=user_id).all()
        
        total_income = sum(t.amount for t in transactions if t.type == 'income')
        total_expense = sum(t.amount for t in transactions if t.type == 'expense')
        
        # Группировка по категориям
        categories = {}
        for t in transactions:
            if t.category not in categories:
                categories[t.category] = 0
            categories[t.category] += t.amount
        
        return {
            'user_id': user_id,
            'username': user.username,
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': total_income - total_expense,
            'categories': categories,
            'transaction_count': len(transactions)
        }


class TransactionCRUDAPI(Resource):
    def get(self, transaction_id):
        """Получить конкретную транзакцию"""
        transaction = Transaction.query.get_or_404(transaction_id)
        
        return {
            'id': transaction.id,
            'amount': transaction.amount,
            'type': transaction.type,
            'category': transaction.category,
            'description': transaction.description,
            'date_posted': transaction.date_posted.isoformat(),
            'receipt_path': transaction.receipt_path,
            'user_id': transaction.user_id
        }
    
    
    def put(self, transaction_id):
        """Обновить транзакцию"""
        transaction = Transaction.query.get_or_404(transaction_id)
        data = request.get_json()
        
        if 'amount' in data:
            transaction.amount = data['amount']
        if 'category' in data:
            transaction.category = data['category']
        if 'description' in data:
            transaction.description = data.get('description', '')
        
        db.session.commit()
        
        return {'message': 'Транзакция обновлена', 'id': transaction.id}
    
    
    def delete(self, transaction_id):
        """Удалить транзакцию"""
        transaction = Transaction.query.get_or_404(transaction_id)
        db.session.delete(transaction)
        db.session.commit()
        
        return {'message': 'Транзакция удалена', 'id': transaction_id}