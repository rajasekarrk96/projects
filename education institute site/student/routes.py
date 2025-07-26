from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from core.services import StudentService, AttendanceService, ExamService, FeeService
from core.student_services import StudentDashboardService, StudentCourseService, CertificateService
from datetime import datetime
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

# Create Blueprint
student_bp = Blueprint('student', __name__, url_prefix='/student')

# Student Dashboard
@student_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('public.index'))  # Avoid redirect loop
    
    try:
        # Get comprehensive dashboard data
        dashboard_data = StudentDashboardService.get_student_dashboard_data(current_user.id)
        
        if not dashboard_data:
            flash('Student profile not found. Please contact administrator.', 'error')
            return redirect(url_for('public.index'))  # Avoid redirect loop
        
        # Debug: Print available data keys
        print(f"Dashboard data keys: {list(dashboard_data.keys())}")
        print(f"Pending fee: {dashboard_data.get('pending_fee', 'MISSING')}")
        print(f"Attendance percentage: {dashboard_data.get('attendance_percentage', 'MISSING')}")
        
        return render_template('student/dashboard.html', data=dashboard_data)
        
    except Exception as e:
        print(f"Student dashboard error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Dashboard temporarily unavailable: {str(e)}', 'error')
        # Return a simple error page instead of redirecting to avoid loops
        return render_template('error.html', 
                             error_title='Dashboard Error',
                             error_message=f'Student dashboard is temporarily unavailable: {str(e)}',
                             back_url=url_for('public.index')), 500

# My Courses
@student_bp.route('/courses')
@login_required
def courses():
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    dashboard_data = StudentDashboardService.get_student_dashboard_data(current_user.id)
    if not dashboard_data:
        flash('Student profile not found', 'error')
        return redirect(url_for('public.dashboard'))
    
    return render_template('student/courses.html', data=dashboard_data)

# Completed Courses
@student_bp.route('/completed-courses')
@login_required
def completed_courses():
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    dashboard_data = StudentDashboardService.get_student_dashboard_data(current_user.id)
    if not dashboard_data:
        flash('Student profile not found', 'error')
        return redirect(url_for('public.dashboard'))
    
    return render_template('student/completed_courses.html', data=dashboard_data)

# Certificates
@student_bp.route('/certificates')
@login_required
def certificates():
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    dashboard_data = StudentDashboardService.get_student_dashboard_data(current_user.id)
    if not dashboard_data:
        flash('Student profile not found', 'error')
        return redirect(url_for('public.dashboard'))
    
    return render_template('student/certificates.html', data=dashboard_data)

# Download Certificate
@student_bp.route('/certificate/<certificate_number>/download')
@login_required
def download_certificate(certificate_number):
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    certificate = CertificateService.get_certificate_by_number(certificate_number)
    if not certificate:
        flash('Certificate not found', 'error')
        return redirect(url_for('student.certificates'))
    
    # Create PDF certificate
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Certificate content
    title = Paragraph("<para align=center><b>CERTIFICATE OF COMPLETION</b></para>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 20))
    
    content = f"""
    <para align=center>This is to certify that</para>
    <para align=center><b>{certificate['student_name']}</b></para>
    <para align=center>has successfully completed the course</para>
    <para align=center><b>{certificate['course_name']}</b></para>
    <para align=center>Duration: {certificate['duration_months']} months</para>
    """
    
    if certificate['grade']:
        content += f"<para align=center>Grade: {certificate['grade']}%</para>"
    
    content += f"""
    <para align=center>Issue Date: {certificate['issue_date']}</para>
    <para align=center>Certificate Number: {certificate['certificate_number']}</para>
    <para align=center>Issued by: {certificate['issued_by_name']}</para>
    """
    
    story.append(Paragraph(content, styles['Normal']))
    doc.build(story)
    
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"certificate_{certificate_number}.pdf",
        mimetype='application/pdf'
    )

# Results
@student_bp.route('/results')
@login_required
def results():
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    dashboard_data = StudentDashboardService.get_student_dashboard_data(current_user.id)
    if not dashboard_data:
        flash('Student profile not found', 'error')
        return redirect(url_for('public.dashboard'))
    
    return render_template('student/results.html', data=dashboard_data)

# Attendance
@student_bp.route('/attendance')
@login_required
def attendance():
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    dashboard_data = StudentDashboardService.get_student_dashboard_data(current_user.id)
    if not dashboard_data:
        flash('Student profile not found', 'error')
        return redirect(url_for('public.dashboard'))
    
    return render_template('student/attendance.html', data=dashboard_data)

# Fees
@student_bp.route('/fees')
@login_required
def fees():
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('public.dashboard'))
    
    dashboard_data = StudentDashboardService.get_student_dashboard_data(current_user.id)
    if not dashboard_data:
        flash('Student profile not found', 'error')
        return redirect(url_for('public.dashboard'))
    
    return render_template('student/fees.html', data=dashboard_data)
