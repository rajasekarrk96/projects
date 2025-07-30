"""
Admin Controller
Handles routing for admin-related pages
"""

from flask import Blueprint, request
from pages.admin_page import (
    AdminDashboardPage,
    UserManagementPage,
    ArticleApprovalPage,
    UserActionsPage,
    AdminUserCreationPage
)
from utils.decorators import role_required

# Create Blueprint
admin_controller = Blueprint('admin', __name__, url_prefix='/admin')


@admin_controller.route('/dashboard')
@role_required(['admin'])
def dashboard():
    """Handle admin dashboard"""
    dashboard_page = AdminDashboardPage()
    return dashboard_page.render_dashboard()


@admin_controller.route('/users')
@role_required(['admin'])
def view_users():
    """Handle users management page"""
    user_management_page = UserManagementPage()
    return user_management_page.render_users_list()


@admin_controller.route('/publishers')
@role_required(['admin'])
def view_publishers():
    """Handle publishers management page"""
    user_management_page = UserManagementPage()
    return user_management_page.render_publishers_list()


@admin_controller.route('/pending-articles')
@role_required(['admin'])
def pending_articles():
    """Handle pending articles page"""
    approval_page = ArticleApprovalPage()
    return approval_page.render_pending_articles()


@admin_controller.route('/view-article/<int:id>')
@role_required(['admin'])
def view_article(id):
    """Handle viewing article details"""
    article_approval_page = ArticleApprovalPage()
    return article_approval_page.render_article_details(id)


@admin_controller.route('/approve-article/<int:id>')
@role_required(['admin'])
def approve_article(id):
    """Handle article approval"""
    approval_page = ArticleApprovalPage()
    success, redirect_url, error = approval_page.process_approve_article(id)
    return approval_page.redirect_to(redirect_url)


@admin_controller.route('/reject-article/<int:id>')
@role_required(['admin'])
def reject_article(id):
    """Handle article rejection"""
    approval_page = ArticleApprovalPage()
    success, redirect_url, error = approval_page.process_reject_article(id)
    return approval_page.redirect_to(redirect_url)


@admin_controller.route('/delete-article/<int:id>')
@role_required(['admin'])
def delete_article(id):
    """Handle article deletion"""
    approval_page = ArticleApprovalPage()
    success, redirect_url, error = approval_page.process_delete_article(id)
    return approval_page.redirect_to(redirect_url)


@admin_controller.route('/approval-requests')
@role_required(['admin'])
def approval_requests():
    """Handle approval requests page"""
    approval_page = ArticleApprovalPage()
    return approval_page.render_pending_articles()


@admin_controller.route('/pending-comments')
@role_required(['admin'])
def pending_comments():
    """Handle pending comments page"""
    approval_page = ArticleApprovalPage()
    return approval_page.render_pending_articles()


@admin_controller.route('/process-approval/<int:request_id>', methods=['POST'])
@role_required(['admin'])
def process_approval(request_id):
    """Handle processing approval requests"""
    approval_page = ArticleApprovalPage()
    # For now, redirect back to approval requests
    return approval_page.redirect_to('admin.approval_requests')


@admin_controller.route('/flag-user/<int:id>')
@role_required(['admin'])
def flag_user(id):
    """Handle flagging users for deactivation"""
    user_management_page = UserManagementPage()
    # For now, redirect back to users list
    return user_management_page.redirect_to('admin.dashboard')


@admin_controller.route('/create-admin-user', methods=['GET', 'POST'])
@role_required(['admin'])
def create_admin_user():
    """Handle admin user creation"""
    create_user_page = AdminUserCreationPage()
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        
        success, redirect_url, error = create_user_page.process_create_admin_user(
            username, email, password, confirm_password, role
        )
        
        if success:
            return create_user_page.redirect_to('admin.dashboard')
        
        return create_user_page.render_create_user_form()
    
    return create_user_page.render_create_user_form()
