# Public Routes Module - Handles authentication and public pages
# 
# Testing Commands:
#     curl http://localhost:5000/                    # Test home page
#     curl http://localhost:5000/login               # Test login page
#     curl http://localhost:5000/enquiry             # Test enquiry form
#     curl -X POST http://localhost:5000/login -d "email=admin@edusphere.com&password=admin123"  # Test login
# 
# Available Routes:
#     GET  /           -> Home page (index.html)
#     GET  /login      -> Login form
#     POST /login      -> Process login
#     GET  /logout     -> Logout user
#     GET  /dashboard  -> Redirect to role-based dashboard
#     GET  /enquiry    -> Enquiry form
#     POST /enquiry    -> Submit enquiry
# 
# Demo Login Credentials:
#     admin@edusphere.com / admin123
#     staff@edusphere.com / staff123
#     faculty@edusphere.com / faculty123
#     student@edusphere.com / student123

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from core.auth import AuthService
from core.services import EnquiryService, DashboardService
from datetime import datetime
from werkzeug.security import check_password_hash

# Create Blueprint
public_bp = Blueprint('public', __name__)

# Public Routes
@public_bp.route('/')
def index():
    return render_template('index.html')

@public_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = AuthService.authenticate_user(email, password)
        
        if user:
            login_user(user)
            
            # Redirect based on user role
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'staff':
                return redirect(url_for('staff.dashboard'))
            elif user.role == 'faculty':
                return redirect(url_for('faculty.dashboard'))
            elif user.role == 'student':
                return redirect(url_for('student.dashboard'))
            else:
                return redirect(url_for('public.dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@public_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('public.index'))

@public_bp.route('/dashboard')
@login_required
def dashboard():
    """Redirect to role-specific dashboard"""
    # Redirect based on user role
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif current_user.role == 'staff':
        return redirect(url_for('staff.dashboard'))
    elif current_user.role == 'faculty':
        return redirect(url_for('faculty.dashboard'))
    elif current_user.role == 'student':
        return redirect(url_for('student.dashboard'))
    else:
        # Fallback for unknown roles
        flash('Unknown user role', 'error')
        return redirect(url_for('public.index'))

@public_bp.route('/enquiry', methods=['GET', 'POST'])
def enquiry():
    """Handle enquiry form"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        course_interest = request.form.get('course_interest')
        message = request.form.get('message')
        
        # Create new enquiry using service
        success = EnquiryService.create_enquiry(
            name=name,
            email=email,
            phone=phone,
            course_interest=course_interest,
            message=message
        )
        
        if success:
            flash('Thank you for your enquiry! We will contact you soon.', 'success')
        else:
            flash('Sorry, there was an error processing your enquiry. Please try again.', 'error')
        
        return redirect(url_for('public.enquiry'))
    
    return render_template('enquiry.html')