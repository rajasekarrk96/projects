"""
Database initialization script using mysql.connector
Creates database schema and populates with demo data

Usage Commands:
python init_mysql_db.py

Prerequisites:
1. MySQL server running on port 3307
2. Create database: CREATE DATABASE edusphere_db;
3. Update .env file with MySQL credentials

Demo Account Credentials:
Admin: admin@edusphere.com / admin123
Staff: staff@edusphere.com / staff123
Faculty: faculty@edusphere.com / faculty123
Student: student@edusphere.com / student123
"""

import sys
import os
from datetime import date, timedelta
import random
from werkzeug.security import generate_password_hash

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import db_manager
from core.auth import AuthService
from core.services import (
    CourseService, BatchService, StudentService, 
    EnquiryService, FeeService, ExamService, AttendanceService
)

def clear_existing_data():
    """Clear all existing data from database"""
    print("Clearing existing data...")
    
    tables_to_clear = [
        'attendance', 'exam_results', 'exams', 'fees', 
        'enquiries', 'students', 'faculty', 'batches', 
        'courses', 'users'
    ]
    
    with db_manager.get_db_cursor() as (cursor, connection):
        # Disable foreign key checks temporarily
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        for table in tables_to_clear:
            cursor.execute(f"DELETE FROM {table}")
            print(f"  Cleared {table}")
        
        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        connection.commit()
    
    print("All existing data cleared!")

def create_demo_users():
    """Create demo user accounts"""
    print("Creating demo users...")
    
    users = [
        {
            'name': 'System Administrator',
            'email': 'admin@edusphere.com',
            'password': 'admin123',
            'role': 'admin'
        },
        {
            'name': 'Staff Member',
            'email': 'staff@edusphere.com',
            'password': 'staff123',
            'role': 'staff'
        },
        {
            'name': 'Faculty Member',
            'email': 'faculty@edusphere.com',
            'password': 'faculty123',
            'role': 'faculty'
        },
        {
            'name': 'Student User',
            'email': 'student@edusphere.com',
            'password': 'student123',
            'role': 'student'
        }
    ]
    
    created_users = {}
    
    for user_data in users:
        success = AuthService.create_user(
            name=user_data['name'],
            email=user_data['email'],
            password=user_data['password'],
            role=user_data['role']
        )
        
        if success:
            user = AuthService.get_user_by_email(user_data['email'])
            created_users[user_data['role']] = user
            print(f"  Created {user_data['role']}: {user_data['email']}")
        else:
            print(f"  Failed to create {user_data['role']}: {user_data['email']}")
    
    return created_users

def create_demo_courses():
    """Create demo courses"""
    print("Creating demo courses...")
    
    courses = [
        {
            'name': 'Full Stack Web Development',
            'description': 'Complete web development course covering HTML, CSS, JavaScript, React, Node.js, and databases.',
            'duration_months': 6,
            'fee': 45000.00
        },
        {
            'name': 'Data Science & Machine Learning',
            'description': 'Comprehensive data science course with Python, pandas, scikit-learn, and deep learning.',
            'duration_months': 8,
            'fee': 55000.00
        },
        {
            'name': 'Digital Marketing',
            'description': 'Complete digital marketing course covering SEO, SEM, social media, and analytics.',
            'duration_months': 4,
            'fee': 25000.00
        },
        {
            'name': 'Mobile App Development',
            'description': 'Learn to build mobile apps for Android and iOS using React Native and Flutter.',
            'duration_months': 5,
            'fee': 40000.00
        }
    ]
    
    created_courses = []
    
    for course_data in courses:
        success = CourseService.create_course(
            name=course_data['name'],
            description=course_data['description'],
            duration_months=course_data['duration_months'],
            fee=course_data['fee']
        )
        
        if success:
            print(f"  Created course: {course_data['name']}")
            created_courses.append(course_data)
        else:
            print(f"  Failed to create course: {course_data['name']}")
    
    return CourseService.get_all_courses()

def create_demo_batches(courses):
    """Create demo batches"""
    print("Creating demo batches...")
    
    if not courses:
        print("  No courses available to create batches")
        return []
    
    batches_data = [
        {
            'course_id': courses[0]['id'],
            'name': 'FSWD-2024-01',
            'start_date': date.today() - timedelta(days=30),
            'end_date': date.today() + timedelta(days=150),
            'timing': '10:00 AM - 1:00 PM',
            'max_students': 25
        },
        {
            'course_id': courses[1]['id'],
            'name': 'DSML-2024-01',
            'start_date': date.today() - timedelta(days=15),
            'end_date': date.today() + timedelta(days=225),
            'timing': '2:00 PM - 5:00 PM',
            'max_students': 20
        }
    ]
    
    for batch_data in batches_data:
        success = BatchService.create_batch(
            course_id=batch_data['course_id'],
            name=batch_data['name'],
            start_date=batch_data['start_date'],
            end_date=batch_data['end_date'],
            timing=batch_data['timing'],
            max_students=batch_data['max_students']
        )
        
        if success:
            print(f"  Created batch: {batch_data['name']}")
        else:
            print(f"  Failed to create batch: {batch_data['name']}")
    
    return BatchService.get_all_batches()

def create_demo_student_data(users, batches):
    """Create demo student profile and related data"""
    print("Creating demo student data...")
    
    if 'student' not in users or not batches:
        print("  Missing student user or batches")
        return None
    
    student_user = users['student']
    batch = batches[0]
    
    # Create student profile
    success = StudentService.create_student(
        user_id=student_user.id,
        registration_number='STU001',
        batch_id=batch['id'],
        admission_date=date.today() - timedelta(days=30),
        guardian_name='Parent Name',
        guardian_phone='9876543214',
        qualification='B.Tech',
        date_of_birth=date(2000, 1, 1),
        gender='Male'
    )
    
    if success:
        print("  Created student profile")
        students = StudentService.get_all_students()
        return students[0] if students else None
    else:
        print("  Failed to create student profile")
        return None

def create_demo_enquiries():
    """Create demo enquiries"""
    print("Creating demo enquiries...")
    
    enquiries = [
        {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '9876543210',
            'course_interest': 'Full Stack Web Development',
            'message': 'Interested in learning web development.'
        },
        {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'phone': '9876543216',
            'course_interest': 'Data Science & Machine Learning',
            'message': 'Looking for data science course information.'
        }
    ]
    
    for enquiry_data in enquiries:
        success = EnquiryService.create_enquiry(
            name=enquiry_data['name'],
            email=enquiry_data['email'],
            phone=enquiry_data['phone'],
            course_interest=enquiry_data['course_interest'],
            message=enquiry_data['message']
        )
        
        if success:
            print(f"  Created enquiry from: {enquiry_data['name']}")
        else:
            print(f"  Failed to create enquiry from: {enquiry_data['name']}")

def create_demo_fees(student):
    """Create demo fee records"""
    print("Creating demo fee records...")
    
    if not student:
        print("  No student available for fee records")
        return
    
    fees = [
        {
            'student_id': student['id'],
            'amount': 15000.00,
            'payment_method': 'online',
            'receipt_number': 'RCP001',
            'remarks': 'First installment'
        },
        {
            'student_id': student['id'],
            'amount': 15000.00,
            'payment_method': 'cash',
            'receipt_number': 'RCP002',
            'remarks': 'Second installment'
        }
    ]
    
    for fee_data in fees:
        success = FeeService.create_fee_record(
            student_id=fee_data['student_id'],
            amount=fee_data['amount'],
            payment_method=fee_data['payment_method'],
            receipt_number=fee_data['receipt_number'],
            remarks=fee_data['remarks']
        )
        
        if success:
            print(f"  Created fee record: {fee_data['receipt_number']}")
        else:
            print(f"  Failed to create fee record: {fee_data['receipt_number']}")

def init_mysql_database():
    """Initialize MySQL database with demo data"""
    print("=" * 50)
    print("Edusphere Institute Management System")
    print("MySQL Database Initialization")
    print("=" * 50)
    
    try:
        # Test database connection
        connection = db_manager.get_connection()
        if not connection:
            print("Failed to connect to MySQL database!")
            print("Please ensure:")
            print("1. MySQL server is running on port 3307")
            print("2. Database 'edusphere_db' exists")
            print("3. Credentials in .env file are correct")
            return False
        
        connection.close()
        print("Database connection successful!")
        
        # Create database schema
        print("\nCreating database schema...")
        db_manager.create_database_schema()
        
        # Clear existing data
        clear_existing_data()
        
        # Create demo data
        print("\nCreating demo data...")
        users = create_demo_users()
        courses = create_demo_courses()
        batches = create_demo_batches(courses)
        student = create_demo_student_data(users, batches)
        create_demo_enquiries()
        create_demo_fees(student)
        
        print("\n" + "=" * 50)
        print("Database initialization completed successfully!")
        print("\nDemo Account Credentials:")
        print("-" * 30)
        print("Admin:")
        print("  Email: admin@edusphere.com")
        print("  Password: admin123")
        print("\nStaff:")
        print("  Email: staff@edusphere.com")
        print("  Password: staff123")
        print("\nFaculty:")
        print("  Email: faculty@edusphere.com")
        print("  Password: faculty123")
        print("\nStudent:")
        print("  Email: student@edusphere.com")
        print("  Password: student123")
        print("\n" + "=" * 50)
        print("Edusphere Institute Management System is ready!")
        print("Run 'python main.py' to start the application")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\nDatabase initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    init_mysql_database()
