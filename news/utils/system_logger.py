"""
System Logger Utility
Handles creation of system logs for tracking user activities
"""

from flask import session
from config import db
from models import SystemLog
from datetime import datetime


def log_system_activity(action, target_type, target_id, details=None, user_id=None):
    """
    Log a system activity
    
    Args:
        action (str): Action performed (e.g., 'article_created', 'user_registered', 'article_approved')
        target_type (str): Type of target (e.g., 'article', 'user', 'comment')
        target_id (int): ID of the target object
        details (str, optional): Additional details about the action
        user_id (int, optional): User ID performing the action (defaults to current session user)
    
    Returns:
        SystemLog: Created log entry or None if failed
    """
    try:
        # Get user ID from session if not provided
        if user_id is None:
            user_id = session.get('user_id')
        
        if not user_id:
            return None  # Can't log without a user
        
        # Create system log entry
        log_entry = SystemLog(
            action=action,
            performed_by=user_id,
            target_type=target_type,
            target_id=target_id,
            details=details,
            timestamp=datetime.utcnow()
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
        return log_entry
        
    except Exception as e:
        db.session.rollback()
        print(f"Failed to create system log: {str(e)}")
        return None


def log_user_registration(user_id, username):
    """Log user registration activity"""
    return log_system_activity(
        action='user_registered',
        target_type='user',
        target_id=user_id,
        details=f'New user registered: {username}',
        user_id=user_id
    )


def log_article_created(article_id, title, author_id):
    """Log article creation activity"""
    return log_system_activity(
        action='article_created',
        target_type='article',
        target_id=article_id,
        details=f'Article created: "{title}"',
        user_id=author_id
    )


def log_article_submitted(article_id, title, author_id):
    """Log article submission for approval"""
    return log_system_activity(
        action='article_submitted',
        target_type='article',
        target_id=article_id,
        details=f'Article submitted for approval: "{title}"',
        user_id=author_id
    )


def log_article_approved(article_id, title, approved_by):
    """Log article approval activity"""
    return log_system_activity(
        action='article_approved',
        target_type='article',
        target_id=article_id,
        details=f'Article approved: "{title}"',
        user_id=approved_by
    )


def log_article_rejected(article_id, title, rejected_by):
    """Log article rejection activity"""
    return log_system_activity(
        action='article_rejected',
        target_type='article',
        target_id=article_id,
        details=f'Article rejected: "{title}"',
        user_id=rejected_by
    )


def log_user_login(user_id, username):
    """Log user login activity"""
    return log_system_activity(
        action='user_login',
        target_type='user',
        target_id=user_id,
        details=f'User logged in: {username}',
        user_id=user_id
    )


def log_comment_added(comment_id, article_id, author_id):
    """Log comment addition activity"""
    return log_system_activity(
        action='comment_added',
        target_type='comment',
        target_id=comment_id,
        details=f'Comment added to article #{article_id}',
        user_id=author_id
    )


def log_admin_action(action, target_type, target_id, details, admin_id):
    """Log admin/superadmin actions"""
    return log_system_activity(
        action=f'admin_{action}',
        target_type=target_type,
        target_id=target_id,
        details=details,
        user_id=admin_id
    )
