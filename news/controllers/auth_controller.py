"""
Authentication Controller
Handles routing for authentication-related pages
"""

from flask import Blueprint, request
from pages.auth_page import LoginPage, RegistrationPage, LogoutPage
from utils.decorators import role_required, login_required

# Create Blueprint
auth_controller = Blueprint('auth', __name__)


@auth_controller.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login page and form submission"""
    login_page = LoginPage()
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        success, redirect_url, error = login_page.process_login(username, password)
        
        if success:
            return login_page.redirect_to(redirect_url)
        
        # If login failed, render form again with error
        return login_page.render_login_form()
    
    # GET request - render login form
    return login_page.render_login_form()


@auth_controller.route('/register', methods=['GET', 'POST'])
def register():
    """Handle registration page and form submission"""
    registration_page = RegistrationPage()
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role_name = request.form.get('role', 'user')
        
        success, redirect_url, error = registration_page.process_registration(
            username, email, password, confirm_password, role_name
        )
        
        if success:
            return registration_page.redirect_to(redirect_url)
        
        # If registration failed, render form again with error
        return registration_page.render_registration_form()
    
    # GET request - render registration form
    return registration_page.render_registration_form()


@auth_controller.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_page = LogoutPage()
    redirect_url = logout_page.process_logout()
    return logout_page.redirect_to(redirect_url)
