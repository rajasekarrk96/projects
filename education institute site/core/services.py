"""
Data services for all entities using mysql.connector
Replaces SQLAlchemy model functionality with raw SQL operations
"""

from datetime import datetime, date, timedelta
from .database import db_manager

class StudentService:
    """Service for student-related database operations"""
    
    @staticmethod
    def create_student(user_id, registration_number, batch_id=None, **kwargs):
        """Create a new student record"""
        query = """
            INSERT INTO students (user_id, registration_number, batch_id, admission_date, 
                                guardian_name, guardian_phone, qualification, date_of_birth, gender)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            user_id,
            registration_number,
            batch_id,
            kwargs.get('admission_date', date.today()),
            kwargs.get('guardian_name'),
            kwargs.get('guardian_phone'),
            kwargs.get('qualification'),
            kwargs.get('date_of_birth'),
            kwargs.get('gender')
        )
        
        try:
            result = db_manager.execute_query(query, params)
            return result > 0
        except Exception as e:
            print(f"Error creating student: {e}")
            return False
    
    @staticmethod
    def get_student_by_id(student_id):
        """Get student by ID with user details"""
        query = """
            SELECT s.*, u.name, u.email, u.role, b.name as batch_name, c.name as course_name
            FROM students s
            JOIN users u ON s.user_id = u.id
            LEFT JOIN batches b ON s.batch_id = b.id
            LEFT JOIN courses c ON b.course_id = c.id
            WHERE s.id = %s AND s.is_active = TRUE
        """
        
        try:
            return db_manager.execute_query(query, (student_id,), fetch_one=True)
        except Exception as e:
            print(f"Error getting student: {e}")
            return None
    
    @staticmethod
    def get_all_students():
        """Get all active students"""
        query = """
            SELECT s.*, u.name, u.email, b.name as batch_name, c.name as course_name
            FROM students s
            JOIN users u ON s.user_id = u.id
            LEFT JOIN batches b ON s.batch_id = b.id
            LEFT JOIN courses c ON b.course_id = c.id
            WHERE s.is_active = TRUE
            ORDER BY s.admission_date DESC
        """
        
        try:
            return db_manager.execute_query(query, fetch=True)
        except Exception as e:
            print(f"Error getting students: {e}")
            return []
    
    @staticmethod
    def get_students_by_batch(batch_id):
        """Get all students in a specific batch"""
        query = """
            SELECT s.*, u.name, u.email, u.phone, s.created_at
            FROM students s
            JOIN users u ON s.user_id = u.id
            WHERE s.batch_id = %s AND s.is_active = TRUE
            ORDER BY s.admission_date DESC
        """
        
        try:
            return db_manager.execute_query(query, (batch_id,), fetch=True)
        except Exception as e:
            print(f"Error getting students by batch: {e}")
            return []

class CourseService:
    """Service for course-related database operations"""
    
    @staticmethod
    def create_course(name, description, duration_months, fee):
        """Create a new course"""
        query = """
            INSERT INTO courses (name, description, duration_months, fee)
            VALUES (%s, %s, %s, %s)
        """
        
        try:
            result = db_manager.execute_query(query, (name, description, duration_months, fee))
            return result > 0
        except Exception as e:
            print(f"Error creating course: {e}")
            return False
    
    @staticmethod
    def get_all_courses():
        """Get all active courses"""
        query = "SELECT * FROM courses WHERE is_active = TRUE ORDER BY name"
        
        try:
            return db_manager.execute_query(query, fetch=True)
        except Exception as e:
            print(f"Error getting courses: {e}")
            return []
    
    @staticmethod
    def get_course_by_id(course_id):
        """Get course by ID"""
        query = "SELECT * FROM courses WHERE id = %s AND is_active = TRUE"
        
        try:
            return db_manager.execute_query(query, (course_id,), fetch_one=True)
        except Exception as e:
            print(f"Error getting course: {e}")
            return None

class BatchService:
    """Service for batch-related database operations"""
    
    @staticmethod
    def create_batch(course_id, name, start_date, end_date=None, timing=None, max_students=30):
        """Create a new batch"""
        query = """
            INSERT INTO batches (course_id, name, start_date, end_date, timing, max_students)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        try:
            result = db_manager.execute_query(
                query, 
                (course_id, name, start_date, end_date, timing, max_students)
            )
            return result > 0
        except Exception as e:
            print(f"Error creating batch: {e}")
            return False
    
    @staticmethod
    def get_all_batches():
        """Get all active batches with course details"""
        query = """
            SELECT b.*, c.name as course_name, c.duration_months, c.fee,
                   COUNT(s.id) as student_count
            FROM batches b
            JOIN courses c ON b.course_id = c.id
            LEFT JOIN students s ON b.id = s.batch_id AND s.is_active = TRUE
            WHERE b.is_active = TRUE
            GROUP BY b.id
            ORDER BY b.start_date DESC
        """
        
        try:
            return db_manager.execute_query(query, fetch=True)
        except Exception as e:
            print(f"Error getting batches: {e}")
            return []
    
    @staticmethod
    def get_batch_by_id(batch_id):
        """Get batch by ID with course details"""
        query = """
            SELECT b.*, c.name as course_name, c.duration_months, c.fee,
                   COUNT(s.id) as student_count
            FROM batches b
            JOIN courses c ON b.course_id = c.id
            LEFT JOIN students s ON b.id = s.batch_id AND s.is_active = TRUE
            WHERE b.id = %s AND b.is_active = TRUE
            GROUP BY b.id
        """
        
        try:
            return db_manager.execute_query(query, (batch_id,), fetch_one=True)
        except Exception as e:
            print(f"Error getting batch: {e}")
            return None
    
    @staticmethod
    def update_batch(batch_id, name, start_date, end_date=None, timing=None, max_students=30, is_active=True):
        """Update batch information"""
        query = """
            UPDATE batches 
            SET name = %s, start_date = %s, end_date = %s, timing = %s, 
                max_students = %s, is_active = %s
            WHERE id = %s
        """
        
        try:
            result = db_manager.execute_query(
                query, 
                (name, start_date, end_date, timing, max_students, is_active, batch_id)
            )
            return result > 0
        except Exception as e:
            print(f"Error updating batch: {e}")
            return False
    
    @staticmethod
    def delete_batch(batch_id):
        """Delete batch (soft delete by setting is_active to FALSE)"""
        query = "UPDATE batches SET is_active = FALSE WHERE id = %s"
        
        try:
            result = db_manager.execute_query(query, (batch_id,))
            return result > 0
        except Exception as e:
            print(f"Error deleting batch: {e}")
            return False

class EnquiryService:
    """Service for enquiry-related database operations"""
    
    @staticmethod
    def create_enquiry(name, email, phone, course_interest=None, message=None):
        """Create a new enquiry"""
        query = """
            INSERT INTO enquiries (name, email, phone, course_interest, message)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        try:
            result = db_manager.execute_query(
                query, 
                (name, email, phone, course_interest, message)
            )
            return result > 0
        except Exception as e:
            print(f"Error creating enquiry: {e}")
            return False
    
    @staticmethod
    def get_all_enquiries():
        """Get all enquiries"""
        query = "SELECT * FROM enquiries ORDER BY created_at DESC"
        
        try:
            return db_manager.execute_query(query, fetch=True)
        except Exception as e:
            print(f"Error getting enquiries: {e}")
            return []
    
    @staticmethod
    def update_enquiry_status(enquiry_id, status, follow_up_date=None):
        """Update enquiry status"""
        query = "UPDATE enquiries SET status = %s, follow_up_date = %s WHERE id = %s"
        
        try:
            result = db_manager.execute_query(query, (status, follow_up_date, enquiry_id))
            return result > 0
        except Exception as e:
            print(f"Error updating enquiry: {e}")
            return False

class FeeService:
    """Service for fee-related database operations"""
    
    @staticmethod
    def create_fee_record(student_id, amount, payment_method='cash', receipt_number=None, remarks=None):
        """Create a new fee record"""
        query = """
            INSERT INTO fees (student_id, amount, payment_method, receipt_number, remarks)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        try:
            result = db_manager.execute_query(
                query, 
                (student_id, amount, payment_method, receipt_number, remarks)
            )
            return result > 0
        except Exception as e:
            print(f"Error creating fee record: {e}")
            return False
    
    @staticmethod
    def get_student_fees(student_id):
        """Get all fee records for a student"""
        query = """
            SELECT f.*, s.registration_number, u.name as student_name
            FROM fees f
            JOIN students s ON f.student_id = s.id
            JOIN users u ON s.user_id = u.id
            WHERE f.student_id = %s
            ORDER BY f.payment_date DESC
        """
        
        try:
            return db_manager.execute_query(query, (student_id,), fetch=True)
        except Exception as e:
            print(f"Error getting student fees: {e}")
            return []

class ExamService:
    """Service for exam-related database operations"""
    
    @staticmethod
    def create_exam(batch_id, title, description, exam_date, total_marks, passing_marks, created_by):
        """Create a new exam"""
        query = """
            INSERT INTO exams (batch_id, title, description, exam_date, total_marks, passing_marks, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            result = db_manager.execute_query(
                query, 
                (batch_id, title, description, exam_date, total_marks, passing_marks, created_by)
            )
            return result > 0
        except Exception as e:
            print(f"Error creating exam: {e}")
            return False
    
    @staticmethod
    def get_batch_exams(batch_id):
        """Get all exams for a batch"""
        query = """
            SELECT e.*, b.name as batch_name, c.name as course_name, u.name as created_by_name
            FROM exams e
            JOIN batches b ON e.batch_id = b.id
            JOIN courses c ON b.course_id = c.id
            JOIN users u ON e.created_by = u.id
            WHERE e.batch_id = %s
            ORDER BY e.exam_date DESC
        """
        
        try:
            return db_manager.execute_query(query, (batch_id,), fetch=True)
        except Exception as e:
            print(f"Error getting batch exams: {e}")
            return []

class AttendanceService:
    """Service for attendance-related database operations"""
    
    @staticmethod
    def mark_attendance(student_id, batch_id, date, status, marked_by):
        """Mark attendance for a student"""
        query = """
            INSERT INTO attendance (student_id, batch_id, date, status, marked_by)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE status = VALUES(status), marked_by = VALUES(marked_by)
        """
        
        try:
            result = db_manager.execute_query(
                query, 
                (student_id, batch_id, date, status, marked_by)
            )
            return result > 0
        except Exception as e:
            print(f"Error marking attendance: {e}")
            return False
    
    @staticmethod
    def get_student_attendance(student_id, start_date=None, end_date=None):
        """Get attendance records for a student"""
        if start_date and end_date:
            query = """
                SELECT a.*, b.name as batch_name, u.name as marked_by_name
                FROM attendance a
                JOIN batches b ON a.batch_id = b.id
                JOIN users u ON a.marked_by = u.id
                WHERE a.student_id = %s AND a.date BETWEEN %s AND %s
                ORDER BY a.date DESC
            """
            params = (student_id, start_date, end_date)
        else:
            query = """
                SELECT a.*, b.name as batch_name, u.name as marked_by_name
                FROM attendance a
                JOIN batches b ON a.batch_id = b.id
                JOIN users u ON a.marked_by = u.id
                WHERE a.student_id = %s
                ORDER BY a.date DESC
                LIMIT 30
            """
            params = (student_id,)
        
        try:
            return db_manager.execute_query(query, params, fetch=True)
        except Exception as e:
            print(f"Error getting student attendance: {e}")
            return []

class DashboardService:
    """Service for dashboard statistics and data"""
    
    @staticmethod
    def get_dashboard_stats():
        """Get dashboard statistics"""
        stats = {}
        
        try:
            # Total students
            result = db_manager.execute_query(
                "SELECT COUNT(*) as count FROM students WHERE is_active = TRUE", 
                fetch_one=True
            )
            stats['total_students'] = result['count'] if result else 0
            
            # Total courses
            result = db_manager.execute_query(
                "SELECT COUNT(*) as count FROM courses WHERE is_active = TRUE", 
                fetch_one=True
            )
            stats['total_courses'] = result['count'] if result else 0
            
            # Active batches
            result = db_manager.execute_query(
                "SELECT COUNT(*) as count FROM batches WHERE is_active = TRUE", 
                fetch_one=True
            )
            stats['active_batches'] = result['count'] if result else 0
            
            # Total enquiries this month
            result = db_manager.execute_query(
                "SELECT COUNT(*) as count FROM enquiries WHERE MONTH(created_at) = MONTH(CURRENT_DATE())", 
                fetch_one=True
            )
            stats['monthly_enquiries'] = result['count'] if result else 0
            
            # Total revenue this month
            result = db_manager.execute_query(
                "SELECT COALESCE(SUM(amount), 0) as total FROM fees WHERE MONTH(payment_date) = MONTH(CURRENT_DATE())", 
                fetch_one=True
            )
            stats['monthly_revenue'] = float(result['total']) if result else 0.0
            
            return stats
            
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {
                'total_students': 0,
                'total_courses': 0,
                'active_batches': 0,
                'monthly_enquiries': 0,
                'monthly_revenue': 0.0
            }
