from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from core.services import BatchService, AttendanceService, ExamService
from core.auth import AuthService
from datetime import datetime, date

# Create Blueprint
faculty_bp = Blueprint('faculty', __name__, url_prefix='/faculty')

# Faculty Dashboard
@faculty_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'faculty':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    # Create faculty data object (placeholder data for now)
    faculty_data = {
        'employee_id': 'FAC001',
        'qualification': 'M.Tech Computer Science',
        'experience': 5,
        'specialization': 'Python Programming & Web Development',
        'joining_date': datetime(2020, 6, 15),
        'salary': '₹45,000'
    }
    
    return render_template('faculty/dashboard.html', 
                         faculty=faculty_data,
                         message="Faculty dashboard - mysql.connector version")

# Attendance Management
@faculty_bp.route('/attendance')
@login_required
def attendance():
    if current_user.role != 'faculty':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    return render_template('faculty/attendance.html', message="Attendance page - mysql.connector version")

# Exam Management
@faculty_bp.route('/exams')
@login_required
def exams():
    if current_user.role != 'faculty':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    return render_template('faculty/exams.html', message="Exams page - mysql.connector version")

@faculty_bp.route('/add_exam')
@login_required
def add_exam():
    if current_user.role != 'faculty':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    return render_template('faculty/add_exam.html', message="Add Exam page - mysql.connector version")

# Exam Action Routes
@faculty_bp.route('/exam/<exam_id>/start', methods=['POST'])
@login_required
def start_exam(exam_id):
    if current_user.role != 'faculty':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # In real implementation, update exam status in database
    # For now, simulate the action
    flash(f'Exam {exam_id} has been started successfully!', 'success')
    return jsonify({'success': True, 'message': f'Exam {exam_id} started successfully'})

@faculty_bp.route('/exam/<exam_id>/end', methods=['POST'])
@login_required
def end_exam(exam_id):
    if current_user.role != 'faculty':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # In real implementation, end exam and finalize results
    flash(f'Exam {exam_id} has been ended successfully!', 'success')
    return jsonify({'success': True, 'message': f'Exam {exam_id} ended successfully'})

@faculty_bp.route('/exam/<exam_id>/cancel', methods=['POST'])
@login_required
def cancel_exam(exam_id):
    if current_user.role != 'faculty':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # In real implementation, cancel exam and notify students
    flash(f'Exam {exam_id} has been cancelled!', 'warning')
    return jsonify({'success': True, 'message': f'Exam {exam_id} cancelled successfully'})

@faculty_bp.route('/exam/<exam_id>/edit')
@login_required
def edit_exam(exam_id):
    if current_user.role != 'faculty':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    # In real implementation, load exam data for editing
    return render_template('faculty/edit_exam.html', exam_id=exam_id, message="Edit Exam page")

@faculty_bp.route('/exam/<exam_id>/results')
@login_required
def view_exam_results(exam_id):
    if current_user.role != 'faculty':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    # Sample exam results data
    exam_results = {
        'exam_id': exam_id,
        'title': 'Python Programming - Unit Test 1',
        'total_students': 25,
        'submitted': 23,
        'average_score': 78.5,
        'highest_score': 95,
        'lowest_score': 45,
        'students': [
            {'name': 'Amit Kumar', 'score': 85, 'status': 'Submitted'},
            {'name': 'Priya Sharma', 'score': 92, 'status': 'Submitted'},
            {'name': 'Rahul Singh', 'score': 67, 'status': 'Submitted'},
            {'name': 'Sneha Patel', 'score': 88, 'status': 'Submitted'},
        ]
    }
    
    return render_template('faculty/exam_results.html', results=exam_results)

@faculty_bp.route('/exam/<exam_id>/download-report')
@login_required
def download_exam_report(exam_id):
    if current_user.role != 'faculty':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    # In real implementation, generate and return PDF report
    flash(f'Report for exam {exam_id} has been generated and downloaded!', 'success')
    return redirect(url_for('faculty.exams'))

@faculty_bp.route('/exam/<exam_id>/details')
@login_required
def get_exam_details(exam_id):
    if current_user.role != 'faculty':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # Sample exam details data
    exam_details = {
        'exam_id': exam_id,
        'title': 'Data Science - Practical Exam',
        'course': 'Data Science',
        'type': 'Practical',
        'duration': 180,
        'total_marks': 100,
        'students_enrolled': 25,
        'currently_active': 23,
        'submitted': 2,
        'time_remaining': 45,
        'started_at': '9:00 AM',
        'will_end_at': '12:00 PM',
        'student_progress': [
            {'name': 'Amit Kumar', 'status': 'Active', 'progress': 75, 'time_used': 135},
            {'name': 'Priya Sharma', 'status': 'Submitted', 'progress': 100, 'time_used': 165},
            {'name': 'Rahul Singh', 'status': 'Active', 'progress': 60, 'time_used': 120},
        ]
    }
    
    return jsonify(exam_details)
