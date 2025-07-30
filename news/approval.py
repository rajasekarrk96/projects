from flask import flash
from config import db
from models import ApprovalRequest, User, Article, Comment
from datetime import datetime

# Central logic for creating and processing approval requests

def create_approval_request(user_id, target_type, target_id, action_type):
    """
    Create a new approval request
    
    Parameters:
    - user_id: ID of the user making the request
    - target_type: Type of target (article, comment, user)
    - target_id: ID of the target object
    - action_type: Type of action (create, update, delete, deactivate)
    
    Returns:
    - The created approval request object
    """
    # Validate user exists
    user = User.query.get(user_id)
    if not user:
        return None, "User not found"
    
    # Validate target exists based on target_type
    if target_type == 'article':
        target = Article.query.get(target_id)
        if not target:
            return None, "Article not found"
        target_table = 'articles'
    elif target_type == 'comment':
        target = Comment.query.get(target_id)
        if not target:
            return None, "Comment not found"
        target_table = 'comments'
    elif target_type == 'user':
        target = User.query.get(target_id)
        if not target:
            return None, "User not found"
        target_table = 'users'
    else:
        return None, "Invalid target type"
    
    # Create approval request
    approval_request = ApprovalRequest(
        requester_id=user_id,
        target_table=target_table,
        target_id=target_id,
        action_type=action_type,
        status='pending'
    )
    
    db.session.add(approval_request)
    db.session.commit()
    
    return approval_request, None

def process_approval_request(request_id, approved_by, status):
    """
    Process an approval request
    
    Parameters:
    - request_id: ID of the approval request
    - approved_by: ID of the admin/superadmin processing the request
    - status: New status (approved/rejected)
    
    Returns:
    - True if successful, False otherwise
    - Error message if any
    """
    # Validate approval request exists
    approval_request = ApprovalRequest.query.get(request_id)
    if not approval_request:
        return False, "Approval request not found"
    
    # Validate admin exists
    admin = User.query.get(approved_by)
    if not admin:
        return False, "Admin not found"
    
    # Update approval request status
    approval_request.status = status
    
    # Process the request based on target_table and action_type
    if status == 'approved':
        if approval_request.target_table == 'articles':
            article = Article.query.get(approval_request.target_id)
            if not article:
                return False, "Article not found"
            
            if approval_request.action_type == 'create' or approval_request.action_type == 'update':
                article.status = 'published'
                article.approved_by = approved_by
            elif approval_request.action_type == 'delete':
                db.session.delete(article)
        
        elif approval_request.target_table == 'users':
            user = User.query.get(approval_request.target_id)
            if not user:
                return False, "User not found"
            
            if approval_request.action_type == 'create':
                user.is_approved = True
            elif approval_request.action_type == 'deactivate':
                user.is_active = False
    
    db.session.commit()
    return True, None

def get_pending_approval_requests():
    """
    Get all pending approval requests
    
    Returns:
    - List of pending approval requests
    """
    return ApprovalRequest.query.filter_by(status='pending').all()

def get_approval_requests_by_status(status):
    """
    Get approval requests by status
    
    Parameters:
    - status: Status to filter by (pending/approved/rejected)
    
    Returns:
    - List of approval requests with the given status
    """
    return ApprovalRequest.query.filter_by(status=status).all()