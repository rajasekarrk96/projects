from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from core.services import StudentService, EnquiryService, FeeService, BatchService
from core.auth import AuthService
from datetime import datetime, date

# Create Blueprint
staff_bp = Blueprint('staff', __name__, url_prefix='/staff')

# Staff Dashboard
@staff_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'staff':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    # Get dashboard data for staff
    try:
        # Get pending enquiries count (placeholder data)
        pending_enquiries = 5  # This would come from EnquiryService in real implementation
        today_admissions = 2   # This would come from StudentService in real implementation
        
        return render_template('staff/dashboard.html', 
                             pending_enquiries=pending_enquiries,
                             today_admissions=today_admissions,
                             message="Staff dashboard - mysql.connector version")
    except Exception as e:
        print(f"Error loading staff dashboard: {e}")
        return render_template('staff/dashboard.html', 
                             pending_enquiries=0,
                             today_admissions=0,
                             message="Staff dashboard - mysql.connector version")

# Enquiry Management
@staff_bp.route('/enquiries')
@login_required
def enquiries():
    if current_user.role != 'staff':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    return render_template('staff/enquiries.html', message="Enquiries page - mysql.connector version")

# Admissions Management
@staff_bp.route('/admissions')
@login_required
def admissions():
    if current_user.role != 'staff':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    # Sample student data (in real app, this would come from database)
    students = [
        {'id': 1, 'name': 'Amit Kumar', 'email': 'amit@email.com', 'course': 'Python Programming', 'batch': 'Morning Batch A', 'admission_date': '15 Jan 2024', 'status': 'Active'},
        {'id': 2, 'name': 'Priya Sharma', 'email': 'priya@email.com', 'course': 'Web Development', 'batch': 'Evening Batch B', 'admission_date': '20 Jan 2024', 'status': 'Active'},
        {'id': 3, 'name': 'Rahul Singh', 'email': 'rahul@email.com', 'course': 'Data Science', 'batch': 'Weekend Batch', 'admission_date': '25 Jan 2024', 'status': 'Pending'}
    ]
    
    return render_template('staff/admissions.html', students=students, message="Admissions page - mysql.connector version")

# Fee Management
@staff_bp.route('/fees')
@login_required
def fees():
    if current_user.role != 'staff':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    # Sample fee records (in real app, this would come from database)
    fee_records = [
        {'receipt_no': 'FEE001', 'student_name': 'Amit Kumar', 'course': 'Python Programming', 'amount': 15000, 'due_date': '15 Feb 2024', 'payment_date': '12 Feb 2024', 'status': 'Paid'},
        {'receipt_no': 'FEE002', 'student_name': 'Priya Sharma', 'course': 'Web Development', 'amount': 18000, 'due_date': '20 Feb 2024', 'payment_date': None, 'status': 'Pending'},
        {'receipt_no': 'FEE003', 'student_name': 'Rahul Singh', 'course': 'Data Science', 'amount': 22000, 'due_date': '10 Feb 2024', 'payment_date': None, 'status': 'Overdue'}
    ]
    
    return render_template('staff/fees.html', fee_records=fee_records, message="Fees page - mysql.connector version")

# Student Details View
@staff_bp.route('/student/<int:student_id>')
@login_required
def view_student(student_id):
    if current_user.role != 'staff':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    # Sample student detail (in real app, this would come from database)
    student = {
        'id': student_id,
        'name': 'Amit Kumar',
        'email': 'amit@email.com',
        'phone': '+91 9876543210',
        'course': 'Python Programming',
        'batch': 'Morning Batch A',
        'admission_date': '15 Jan 2024',
        'status': 'Active',
        'address': '123 Main Street, Delhi',
        'guardian_name': 'Mr. Kumar',
        'guardian_phone': '+91 9876543211'
    }
    
    return render_template('staff/student_details.html', student=student)

# Fee Receipt View
@staff_bp.route('/fee/receipt/<receipt_no>')
@login_required
def view_receipt(receipt_no):
    if current_user.role != 'staff':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    # Sample receipt data (in real app, this would come from database)
    receipt = {
        'receipt_no': receipt_no,
        'student_name': 'Amit Kumar',
        'course': 'Python Programming',
        'amount': 15000,
        'payment_date': '12 Feb 2024',
        'payment_method': 'Cash',
        'remarks': 'First installment'
    }
    
    return render_template('staff/receipt_details.html', receipt=receipt)

# Print Receipt
@staff_bp.route('/fee/print/<receipt_no>')
@login_required
def print_receipt(receipt_no):
    if current_user.role != 'staff':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    # In a real app, this would generate a PDF or printable version
    flash(f'Receipt {receipt_no} sent to printer', 'success')
    return redirect(url_for('staff.fees'))
