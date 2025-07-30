"""
Utility decorators for the Flask News Portal
"""

from functools import wraps
from flask import session, flash, redirect, url_for
from services.auth_service import AuthService


def role_required(allowed_roles):
    """
    Decorator for role-based access control
    
    Args:
        allowed_roles (list): List of allowed role names
        
    Returns:
        Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is logged in
            if 'user_id' not in session:
                flash('Please log in to access this page', 'error')
                return redirect(url_for('auth.login'))
            
            user_id = session['user_id']
            has_permission, error = AuthService.check_user_role(user_id, allowed_roles)
            
            if not has_permission:
                flash(error or 'You do not have permission to access this page', 'error')
                if error == "User account is not active or approved":
                    session.clear()
                    return redirect(url_for('auth.login'))
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def login_required(f):
    """
    Decorator to require user login
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
