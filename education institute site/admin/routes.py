from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from core.auth import AuthService
from core.services import (
    CourseService, BatchService, StudentService, EnquiryService, 
    FeeService, DashboardService, AttendanceService
)
from werkzeug.security import generate_password_hash
from datetime import datetime, date

# Create Blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin Dashboard
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    # Get dashboard statistics using new service
    stats = DashboardService.get_dashboard_stats()
    
    # Add pending enquiries count (placeholder data for now)
    pending_enquiries = 8  # This would come from EnquiryService in real implementation
    
    return render_template('admin/dashboard.html', stats=stats, pending_enquiries=pending_enquiries)

# Course Management
@admin_bp.route('/courses')
@login_required
def courses():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    courses = CourseService.get_all_courses()
    return render_template('admin/courses.html', courses=courses)

@admin_bp.route('/courses/add', methods=['GET', 'POST'])
@login_required
def add_course():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    if request.method == 'POST':
        success = CourseService.create_course(
            name=request.form['name'],
            description=request.form['description'],
            duration_months=int(request.form['duration_months']),
            fee=float(request.form['fee'])
        )
        
        if success:
            flash('Course added successfully', 'success')
        else:
            flash('Error adding course', 'error')
        
        return redirect(url_for('admin.courses'))
    
    return render_template('admin/add_course.html')

# Batch Management
@admin_bp.route('/batches')
@login_required
def batches():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    batches = BatchService.get_all_batches()
    return render_template('admin/batches.html', batches=batches)

@admin_bp.route('/batches/add', methods=['GET', 'POST'])
@login_required
def add_batch():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    if request.method == 'POST':
        success = BatchService.create_batch(
            course_id=int(request.form['course_id']),
            name=request.form['name'],
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date() if request.form.get('end_date') else None,
            timing=request.form.get('timing'),
            max_students=int(request.form['max_students'])
        )
        
        if success:
            flash('Batch added successfully', 'success')
        else:
            flash('Error adding batch', 'error')
        
        return redirect(url_for('admin.batches'))
    
    courses = CourseService.get_all_courses()
    faculties = AuthService.get_all_users(role='faculty')
    return render_template('admin/add_batch.html', courses=courses, faculties=faculties)

@admin_bp.route('/batches/<int:batch_id>/view')
@login_required
def view_batch(batch_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    batch = BatchService.get_batch_by_id(batch_id)
    if not batch:
        flash('Batch not found', 'error')
        return redirect(url_for('admin.batches'))
    
    # Get batch students and statistics
    batch_students = StudentService.get_students_by_batch(batch_id)
    batch_stats = {
        'total_students': len(batch_students),
        'active_students': len([s for s in batch_students if s.get('is_active', True)]),
        'completion_rate': 75,  # Sample data
        'attendance_rate': 85   # Sample data
    }
    
    return render_template('admin/view_batch.html', batch=batch, students=batch_students, stats=batch_stats)

@admin_bp.route('/batches/<int:batch_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_batch(batch_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    batch = BatchService.get_batch_by_id(batch_id)
    if not batch:
        flash('Batch not found', 'error')
        return redirect(url_for('admin.batches'))
    
    if request.method == 'POST':
        success = BatchService.update_batch(
            batch_id=batch_id,
            name=request.form['name'],
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date() if request.form.get('end_date') else None,
            timing=request.form.get('timing'),
            max_students=int(request.form['max_students']),
            is_active=request.form.get('is_active') == 'on'
        )
        
        if success:
            flash('Batch updated successfully', 'success')
        else:
            flash('Error updating batch', 'error')
        
        return redirect(url_for('admin.batches'))
    
    courses = CourseService.get_all_courses()
    return render_template('admin/edit_batch.html', batch=batch, courses=courses)

@admin_bp.route('/batches/<int:batch_id>/delete', methods=['POST'])
@login_required
def delete_batch(batch_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    batch = BatchService.get_batch_by_id(batch_id)
    if not batch:
        return jsonify({'success': False, 'message': 'Batch not found'}), 404
    
    # Check if batch has students enrolled
    batch_students = StudentService.get_students_by_batch(batch_id)
    if batch_students:
        return jsonify({
            'success': False, 
            'message': f'Cannot delete batch with {len(batch_students)} enrolled students'
        }), 400
    
    success = BatchService.delete_batch(batch_id)
    if success:
        return jsonify({'success': True, 'message': 'Batch deleted successfully'})
    else:
        return jsonify({'success': False, 'message': 'Error deleting batch'}), 500

# Student Management
@admin_bp.route('/students/<int:student_id>/view')
@login_required
def view_student(student_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    student = StudentService.get_student_by_id(student_id)
    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('admin.batches'))
    
    # Get student's fee records
    fee_records = FeeService.get_student_fees(student_id)
    
    # Get student's attendance records (last 30 days)
    attendance_records = AttendanceService.get_student_attendance(student_id)
    
    # Calculate attendance percentage
    if attendance_records:
        present_count = len([a for a in attendance_records if a['status'] == 'present'])
        attendance_percentage = (present_count / len(attendance_records)) * 100
    else:
        attendance_percentage = 0
    
    # Get student statistics
    student_stats = {
        'total_fees_paid': sum([float(fee['amount']) for fee in fee_records]) if fee_records else 0,
        'attendance_percentage': round(attendance_percentage, 1),
        'total_classes': len(attendance_records),
        'classes_attended': len([a for a in attendance_records if a['status'] == 'present']) if attendance_records else 0
    }
    
    return render_template('admin/view_student.html', 
                         student=student, 
                         fee_records=fee_records, 
                         attendance_records=attendance_records[:10],  # Show last 10 records
                         stats=student_stats)

# Faculty Management
@admin_bp.route('/faculty')
@login_required
def faculty():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    faculty_list = AuthService.get_all_users(role='faculty')
    return render_template('admin/faculty.html', faculty_list=faculty_list)

@admin_bp.route('/faculty/add', methods=['GET', 'POST'])
@login_required
def add_faculty():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    if request.method == 'POST':
        # Create faculty user account
        success = AuthService.create_user(
            name=request.form['name'],
            email=request.form['email'],
            password=request.form['password'],
            role='faculty'
        )
        
        if success:
            flash('Faculty added successfully', 'success')
        else:
            flash('Error adding faculty', 'error')
        
        return redirect(url_for('admin.faculty'))
    
    return render_template('admin/add_faculty.html')

# Enquiry Management
@admin_bp.route('/enquiries')
@login_required
def enquiries():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    # Get all enquiries
    enquiries = EnquiryService.get_all_enquiries()
    
    return render_template('admin/enquiries.html', enquiries=enquiries)

# Reports
@admin_bp.route('/reports')
@login_required
def reports():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    # Get dashboard statistics for reports
    stats = DashboardService.get_dashboard_stats()
    
    return render_template('admin/reports.html', stats=stats) 