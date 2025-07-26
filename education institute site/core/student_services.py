"""
Student-specific services for course completion, certificates, and student dashboard
"""

from .database import db_manager
from datetime import date, datetime
import random
import string

class StudentCourseService:
    """Service for managing student course completions and progress"""
    
    @staticmethod
    def get_student_courses(student_id):
        """Get all courses for a student with completion status"""
        query = """
            SELECT 
                c.id as course_id,
                c.name as course_name,
                c.description,
                c.duration_months,
                c.fee,
                b.id as batch_id,
                b.name as batch_name,
                b.start_date,
                b.end_date,
                s.registration_number,
                cc.completion_date,
                cc.final_grade,
                cc.status as completion_status,
                CASE 
                    WHEN cc.status = 'completed' THEN 'Completed'
                    WHEN cc.status = 'in_progress' THEN 'In Progress'
                    WHEN cc.status = 'dropped' THEN 'Dropped'
                    WHEN b.end_date < CURDATE() THEN 'Completed'
                    ELSE 'In Progress'
                END as display_status
            FROM students s
            JOIN batches b ON s.batch_id = b.id
            JOIN courses c ON b.course_id = c.id
            LEFT JOIN course_completions cc ON s.id = cc.student_id AND c.id = cc.course_id
            WHERE s.id = %s
            ORDER BY b.start_date DESC
        """
        
        try:
            courses = db_manager.execute_query(query, (student_id,), fetch=True)
            return courses or []
        except Exception as e:
            print(f"Error getting student courses: {e}")
            return []
    
    @staticmethod
    def get_completed_courses(student_id):
        """Get only completed courses for a student"""
        query = """
            SELECT 
                c.id as course_id,
                c.name as course_name,
                c.description,
                c.duration_months,
                b.name as batch_name,
                b.start_date,
                b.end_date,
                cc.completion_date,
                cc.final_grade,
                cc.status
            FROM students s
            JOIN batches b ON s.batch_id = b.id
            JOIN courses c ON b.course_id = c.id
            LEFT JOIN course_completions cc ON s.id = cc.student_id AND c.id = cc.course_id
            WHERE s.id = %s 
            AND (cc.status = 'completed' OR (cc.status IS NULL AND b.end_date < CURDATE()))
            ORDER BY COALESCE(cc.completion_date, b.end_date) DESC
        """
        
        try:
            courses = db_manager.execute_query(query, (student_id,), fetch=True)
            return courses or []
        except Exception as e:
            print(f"Error getting completed courses: {e}")
            return []
    
    @staticmethod
    def mark_course_completed(student_id, course_id, batch_id, final_grade=None):
        """Mark a course as completed for a student"""
        query = """
            INSERT INTO course_completions (student_id, batch_id, course_id, completion_date, final_grade, status)
            VALUES (%s, %s, %s, %s, %s, 'completed')
            ON DUPLICATE KEY UPDATE
            completion_date = VALUES(completion_date),
            final_grade = VALUES(final_grade),
            status = 'completed'
        """
        
        try:
            result = db_manager.execute_query(
                query, 
                (student_id, batch_id, course_id, date.today(), final_grade)
            )
            return result > 0
        except Exception as e:
            print(f"Error marking course completed: {e}")
            return False

class CertificateService:
    """Service for managing student certificates"""
    
    @staticmethod
    def generate_certificate_number():
        """Generate a unique certificate number"""
        timestamp = datetime.now().strftime("%Y%m%d")
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"CERT-{timestamp}-{random_part}"
    
    @staticmethod
    def get_student_certificates(student_id):
        """Get all certificates for a student"""
        query = """
            SELECT 
                cert.id,
                cert.certificate_number,
                cert.issue_date,
                cert.certificate_type,
                cert.grade,
                c.name as course_name,
                c.description as course_description,
                u.name as issued_by_name
            FROM certificates cert
            JOIN courses c ON cert.course_id = c.id
            JOIN users u ON cert.issued_by = u.id
            WHERE cert.student_id = %s AND cert.is_active = TRUE
            ORDER BY cert.issue_date DESC
        """
        
        try:
            certificates = db_manager.execute_query(query, (student_id,), fetch=True)
            return certificates or []
        except Exception as e:
            print(f"Error getting student certificates: {e}")
            return []
    
    @staticmethod
    def create_certificate(student_id, course_id, issued_by, grade=None, certificate_type='completion'):
        """Create a new certificate for a student"""
        certificate_number = CertificateService.generate_certificate_number()
        
        query = """
            INSERT INTO certificates (student_id, course_id, certificate_number, issue_date, 
                                    certificate_type, grade, issued_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            result = db_manager.execute_query(
                query, 
                (student_id, course_id, certificate_number, date.today(), 
                 certificate_type, grade, issued_by)
            )
            return certificate_number if result > 0 else None
        except Exception as e:
            print(f"Error creating certificate: {e}")
            return None
    
    @staticmethod
    def get_certificate_by_number(certificate_number):
        """Get certificate details by certificate number"""
        query = """
            SELECT 
                cert.id,
                cert.certificate_number,
                cert.issue_date,
                cert.certificate_type,
                cert.grade,
                s.registration_number,
                u_student.name as student_name,
                c.name as course_name,
                c.description as course_description,
                c.duration_months,
                u_issuer.name as issued_by_name
            FROM certificates cert
            JOIN students s ON cert.student_id = s.id
            JOIN users u_student ON s.user_id = u_student.id
            JOIN courses c ON cert.course_id = c.id
            JOIN users u_issuer ON cert.issued_by = u_issuer.id
            WHERE cert.certificate_number = %s AND cert.is_active = TRUE
        """
        
        try:
            certificate = db_manager.execute_query(query, (certificate_number,), fetch_one=True)
            return certificate
        except Exception as e:
            print(f"Error getting certificate: {e}")
            return None

class StudentDashboardService:
    """Service for student dashboard data"""
    
    @staticmethod
    def get_student_dashboard_data(user_id):
        """Get comprehensive dashboard data for a student"""
        # Get student record
        student_query = """
            SELECT s.*, u.name, u.email 
            FROM students s 
            JOIN users u ON s.user_id = u.id 
            WHERE s.user_id = %s
        """
        
        try:
            student = db_manager.execute_query(student_query, (user_id,), fetch_one=True)
            if not student:
                return None
            
            student_id = student['id']
            
            # Get courses and completion status
            courses = StudentCourseService.get_student_courses(student_id)
            completed_courses = StudentCourseService.get_completed_courses(student_id)
            certificates = CertificateService.get_student_certificates(student_id)
            
            # Get recent attendance
            attendance_query = """
                SELECT a.date, a.status, b.name as batch_name
                FROM attendance a
                JOIN batches b ON a.batch_id = b.id
                WHERE a.student_id = %s
                ORDER BY a.date DESC
                LIMIT 10
            """
            recent_attendance = db_manager.execute_query(attendance_query, (student_id,), fetch=True) or []
            
            # Get recent exam results
            results_query = """
                SELECT er.marks_obtained, e.total_marks, e.title, e.exam_date, b.name as batch_name
                FROM exam_results er
                JOIN exams e ON er.exam_id = e.id
                JOIN batches b ON e.batch_id = b.id
                WHERE er.student_id = %s
                ORDER BY e.exam_date DESC
                LIMIT 5
            """
            recent_results = db_manager.execute_query(results_query, (student_id,), fetch=True) or []
            
            # Get fee records
            fees_query = """
                SELECT amount, payment_date, payment_method, receipt_number
                FROM fees
                WHERE student_id = %s
                ORDER BY payment_date DESC
                LIMIT 10
            """
            fee_records = db_manager.execute_query(fees_query, (student_id,), fetch=True) or []
            
            # Calculate pending fees (total course fee - paid amount)
            total_paid = sum(float(fee.get('amount', 0)) for fee in fee_records)
            course_fee = courses[0].get('fee', 0) if courses else 0
            pending_fee = max(0, float(course_fee) - total_paid)
            
            # Calculate attendance percentage
            attendance_percentage = StudentDashboardService._calculate_attendance_percentage(student_id)
            
            return {
                'student': student,
                'courses': courses,
                'completed_courses': completed_courses,
                'certificates': certificates,
                'recent_attendance': recent_attendance,
                'recent_results': recent_results,
                'fee_records': fee_records,
                'pending_fee': pending_fee,
                'attendance_percentage': attendance_percentage,
                'stats': {
                    'total_courses': len(courses),
                    'completed_courses': len(completed_courses),
                    'certificates_earned': len(certificates),
                    'attendance_percentage': attendance_percentage
                }
            }
            
        except Exception as e:
            print(f"Error getting student dashboard data: {e}")
            return None
    
    @staticmethod
    def _calculate_attendance_percentage(student_id):
        """Calculate attendance percentage for a student"""
        try:
            total_query = "SELECT COUNT(*) as total FROM attendance WHERE student_id = %s"
            present_query = "SELECT COUNT(*) as present FROM attendance WHERE student_id = %s AND status = 'present'"
            
            total = db_manager.execute_query(total_query, (student_id,), fetch_one=True)
            present = db_manager.execute_query(present_query, (student_id,), fetch_one=True)
            
            if total and total['total'] > 0:
                return round((present['present'] / total['total']) * 100, 1)
            return 0.0
        except Exception as e:
            print(f"Error calculating attendance: {e}")
            return 0.0
