"""
SuperAdmin Controller
Handles routing for superadmin-related pages
"""

from flask import Blueprint, request
from config import db
from pages.superadmin_page import (
    SuperAdminDashboardPage,
    ApprovalManagementPage,
    SystemManagementPage
)
from utils.decorators import role_required

# Create Blueprint
superadmin_controller = Blueprint('superadmin', __name__, url_prefix='/superadmin')


@superadmin_controller.route('/dashboard')
@role_required(['superadmin'])
def dashboard():
    """Handle superadmin dashboard"""
    dashboard_page = SuperAdminDashboardPage()
    return dashboard_page.render_dashboard()


@superadmin_controller.route('/approval-requests')
@role_required(['superadmin'])
def approval_requests():
    """Handle approval requests management"""
    approval_page = ApprovalManagementPage()
    return approval_page.render_approval_requests()


@superadmin_controller.route('/admins')
@role_required(['superadmin'])
def admins():
    """Handle admin management page"""
    from flask import render_template
    from models import User, Role
    # Get only admin users (excluding superadmins)
    admins = User.query.filter(User.role.has(Role.name == 'admin')).all()
    # Get only superadmin users
    superadmins = User.query.filter(User.role.has(Role.name == 'superadmin')).all()
    return render_template('superadmin/admins.html', admins=admins, superadmins=superadmins)


@superadmin_controller.route('/system-management')
@role_required(['superadmin'])
def system_management():
    """Handle system management page"""
    dashboard_page = SuperAdminDashboardPage()
    return dashboard_page.render_dashboard()


@superadmin_controller.route('/user-action/<int:user_id>/<action>')
@role_required(['superadmin'])
def user_action(user_id, action):
    """Handle user management actions"""
    system_page = SystemManagementPage()
    success, redirect_url, error = system_page.process_user_action(user_id, action)
    return system_page.redirect_to(redirect_url)


@superadmin_controller.route('/users')
@role_required(['superadmin'])
def users():
    """Handle users management page"""
    from flask import render_template
    from models import User, Role
    users = User.query.filter(User.role.has(Role.name == 'user')).all()
    return render_template('superadmin/users.html', users=users)


@superadmin_controller.route('/publishers')
@role_required(['superadmin'])
def publishers():
    """Handle publishers management page"""
    from flask import render_template
    from models import User, Role
    publishers = User.query.filter(User.role.has(Role.name == 'publisher')).all()
    return render_template('superadmin/publishers.html', publishers=publishers)


@superadmin_controller.route('/approvals')
@role_required(['superadmin'])
def approvals():
    """Handle approvals page (alias for approval-requests)"""
    from flask import render_template
    from models import ApprovalRequest
    approval_requests = ApprovalRequest.query.filter_by(status='pending').all()
    return render_template('superadmin/approvals.html', approval_requests=approval_requests)


@superadmin_controller.route('/articles')
@role_required(['superadmin'])
def articles():
    """Handle articles management page"""
    from flask import render_template
    from models import Article
    articles = Article.query.all()
    return render_template('superadmin/articles.html', articles=articles)


@superadmin_controller.route('/logs')
@role_required(['superadmin'])
def logs():
    """Handle logs page"""
    from flask import render_template
    from models import SystemLog
    # Get recent system logs, ordered by most recent first
    recent_logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).limit(100).all()
    return render_template('superadmin/logs.html', logs=recent_logs)


@superadmin_controller.route('/create-admin', methods=['GET', 'POST'])
@role_required(['superadmin'])
def create_admin():
    """Handle admin creation page"""
    from pages.admin_page import AdminUserCreationPage
    create_user_page = AdminUserCreationPage()
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        success, redirect_url, error = create_user_page.process_create_admin_user(
            username, email, password, confirm_password, 'admin'
        )
        
        if success:
            return create_user_page.redirect_to('superadmin.admins')
        
        return create_user_page.render_create_user_form()
    
    return create_user_page.render_create_user_form()


@superadmin_controller.route('/create-superadmin', methods=['GET', 'POST'])
@role_required(['superadmin'])
def create_superadmin():
    """Handle superadmin creation page"""
    from pages.admin_page import AdminUserCreationPage
    create_user_page = AdminUserCreationPage()
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        success, redirect_url, error = create_user_page.process_create_admin_user(
            username, email, password, confirm_password, 'superadmin'
        )
        
        if success:
            return create_user_page.redirect_to('superadmin.admins')
        
        return create_user_page.render_create_user_form()
    
    return create_user_page.render_create_user_form()


@superadmin_controller.route('/view-article/<int:id>')
@role_required(['superadmin'])
def view_article(id):
    """Handle viewing article details"""
    from flask import render_template
    from models import Article
    article = Article.query.get_or_404(id)
    return render_template('superadmin/article_details.html', article=article)


@superadmin_controller.route('/delete-article/<int:id>', methods=['POST', 'GET'])
@role_required(['superadmin'])
def delete_article(id):
    """Handle deleting articles"""
    from flask import session, flash, redirect, url_for
    from services.article_service import ArticleService
    from utils.system_logger import log_admin_action
    
    user_id = session.get('user_id')
    
    # Delete the article using the service
    success, error = ArticleService.delete_article(id, user_id)
    
    if success:
        # Log the admin action
        log_admin_action(
            action='article_deleted',
            target_type='article',
            target_id=id,
            details=f'Article {id} deleted by superadmin',
            admin_id=user_id
        )
        flash('Article deleted successfully!', 'success')
    else:
        flash(f'Failed to delete article: {error}', 'error')
    
    return redirect(url_for('superadmin.articles'))


@superadmin_controller.route('/process-approval/<int:request_id>', methods=['POST'])
@role_required(['superadmin'])
def process_approval(request_id):
    """Handle processing approval requests"""
    from flask import request, session, redirect, url_for, flash
    from approval import process_approval_request
    
    status = request.form.get('status')  # 'approved' or 'rejected'
    user_id = session.get('user_id')
    
    if not status or status not in ['approved', 'rejected']:
        flash('Invalid approval status', 'error')
        return redirect(url_for('superadmin.approvals'))
    
    success, error = process_approval_request(request_id, user_id, status)
    
    if success:
        flash(f'Approval request {status} successfully!', 'success')
    else:
        flash(f'Failed to process approval request: {error}', 'error')
    
    return redirect(url_for('superadmin.approvals'))


@superadmin_controller.route('/toggle-user-status/<int:id>')
@role_required(['superadmin'])
def toggle_user_status(id):
    """Handle toggling user active/inactive status"""
    from flask import redirect, url_for, flash
    from models import User
    from utils.system_logger import log_admin_action
    
    user = User.query.get_or_404(id)
    
    try:
        # Toggle user status
        user.is_active = not user.is_active
        status_text = 'activated' if user.is_active else 'deactivated'
        
        db.session.commit()
        
        # Log the admin action
        from flask import session
        admin_id = session.get('user_id')
        log_admin_action(
            action=f'user_{status_text}',
            target_type='user',
            target_id=user.id,
            details=f'User {user.username} {status_text}',
            admin_id=admin_id
        )
        
        flash(f'User {user.username} has been {status_text} successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to update user status: {str(e)}', 'error')
    
    return redirect(url_for('superadmin.admins'))
