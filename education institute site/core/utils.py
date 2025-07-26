import random
import string
from datetime import datetime, date
from sqlalchemy import func, and_

def generate_id(prefix, length=6):
    """Generate unique ID with prefix"""
    return prefix + ''.join(random.choices(string.digits, k=length))

def get_monthly_stats(db, model, date_field, current_month=None, current_year=None):
    """Get monthly statistics for any model"""
    if current_month is None:
        current_month = datetime.now().month
    if current_year is None:
        current_year = datetime.now().year
    
    return db.session.query(
        func.extract('month', date_field).label('month'),
        func.extract('year', date_field).label('year'),
        func.count(model.id).label('count')
    ).filter(
        and_(
            func.extract('month', date_field) == current_month,
            func.extract('year', date_field) == current_year
        )
    ).scalar() or 0

def get_monthly_sum(db, model, amount_field, date_field, current_month=None, current_year=None):
    """Get monthly sum for any model"""
    if current_month is None:
        current_month = datetime.now().month
    if current_year is None:
        current_year = datetime.now().year
    
    return db.session.query(func.sum(amount_field)).filter(
        and_(
            func.extract('month', date_field) == current_month,
            func.extract('year', date_field) == current_year
        )
    ).scalar() or 0 