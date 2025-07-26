"""
Database connection and utility functions using mysql.connector
Handles all MySQL database operations with raw SQL statements
"""

import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime, date
import json
from contextlib import contextmanager

class DatabaseManager:
    """Database manager for MySQL operations using mysql.connector"""
    
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '3307')),
            'database': os.getenv('DB_NAME', 'edusphere_db'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', '1234'),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'autocommit': False
        }
    
    def get_connection(self):
        """Get a new database connection"""
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    @contextmanager
    def get_db_cursor(self, dictionary=True):
        """Context manager for database operations"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            if connection:
                cursor = connection.cursor(dictionary=dictionary)
                yield cursor, connection
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def execute_query(self, query, params=None, fetch=False, fetch_one=False):
        """Execute a single query"""
        with self.get_db_cursor() as (cursor, connection):
            cursor.execute(query, params or ())
            
            if fetch_one:
                result = cursor.fetchone()
            elif fetch:
                result = cursor.fetchall()
            else:
                connection.commit()
                result = cursor.rowcount
            
            return result
    
    def execute_many(self, query, params_list):
        """Execute query with multiple parameter sets"""
        with self.get_db_cursor() as (cursor, connection):
            cursor.executemany(query, params_list)
            connection.commit()
            return cursor.rowcount
    
    def create_database_schema(self):
        """Create all database tables"""
        tables = {
            'users': """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role ENUM('admin', 'staff', 'faculty', 'student') NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'courses': """
                CREATE TABLE IF NOT EXISTS courses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    duration_months INT NOT NULL,
                    fee DECIMAL(10,2) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'batches': """
                CREATE TABLE IF NOT EXISTS batches (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    course_id INT NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE,
                    timing VARCHAR(50),
                    max_students INT DEFAULT 30,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'students': """
                CREATE TABLE IF NOT EXISTS students (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    registration_number VARCHAR(20) UNIQUE NOT NULL,
                    batch_id INT,
                    admission_date DATE DEFAULT (CURRENT_DATE),
                    guardian_name VARCHAR(100),
                    guardian_phone VARCHAR(15),
                    qualification VARCHAR(100),
                    date_of_birth DATE,
                    gender ENUM('Male', 'Female', 'Other'),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'faculty': """
                CREATE TABLE IF NOT EXISTS faculty (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    employee_id VARCHAR(20) UNIQUE NOT NULL,
                    specialization VARCHAR(100),
                    qualification VARCHAR(200),
                    experience_years INT DEFAULT 0,
                    salary DECIMAL(10,2),
                    joining_date DATE DEFAULT (CURRENT_DATE),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'enquiries': """
                CREATE TABLE IF NOT EXISTS enquiries (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    phone VARCHAR(15) NOT NULL,
                    course_interest VARCHAR(100),
                    message TEXT,
                    status ENUM('new', 'contacted', 'converted', 'closed') DEFAULT 'new',
                    follow_up_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'fees': """
                CREATE TABLE IF NOT EXISTS fees (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id INT NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    payment_date DATE DEFAULT (CURRENT_DATE),
                    payment_method ENUM('cash', 'online', 'cheque', 'card') DEFAULT 'cash',
                    receipt_number VARCHAR(50),
                    remarks TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'exams': """
                CREATE TABLE IF NOT EXISTS exams (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    batch_id INT NOT NULL,
                    title VARCHAR(100) NOT NULL,
                    description TEXT,
                    exam_date DATE NOT NULL,
                    total_marks INT NOT NULL,
                    passing_marks INT NOT NULL,
                    created_by INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE,
                    FOREIGN KEY (created_by) REFERENCES users(id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'exam_results': """
                CREATE TABLE IF NOT EXISTS exam_results (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    exam_id INT NOT NULL,
                    student_id INT NOT NULL,
                    marks_obtained INT NOT NULL,
                    remarks TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_exam_student (exam_id, student_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'attendance': """
                CREATE TABLE IF NOT EXISTS attendance (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id INT NOT NULL,
                    batch_id INT NOT NULL,
                    date DATE NOT NULL,
                    status ENUM('present', 'absent', 'late') DEFAULT 'present',
                    marked_by INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE,
                    FOREIGN KEY (marked_by) REFERENCES users(id),
                    UNIQUE KEY unique_student_date (student_id, date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'course_completions': """
                CREATE TABLE IF NOT EXISTS course_completions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id INT NOT NULL,
                    batch_id INT NOT NULL,
                    course_id INT NOT NULL,
                    completion_date DATE NOT NULL,
                    final_grade DECIMAL(5,2),
                    status ENUM('completed', 'in_progress', 'dropped') DEFAULT 'completed',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE,
                    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_student_course (student_id, course_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'certificates': """
                CREATE TABLE IF NOT EXISTS certificates (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id INT NOT NULL,
                    course_id INT NOT NULL,
                    certificate_number VARCHAR(50) UNIQUE NOT NULL,
                    issue_date DATE NOT NULL,
                    certificate_type ENUM('completion', 'achievement', 'participation') DEFAULT 'completion',
                    grade DECIMAL(5,2),
                    issued_by INT NOT NULL,
                    template_path VARCHAR(255),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                    FOREIGN KEY (issued_by) REFERENCES users(id),
                    UNIQUE KEY unique_student_course_cert (student_id, course_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        }
        
        with self.get_db_cursor() as (cursor, connection):
            for table_name, create_sql in tables.items():
                try:
                    cursor.execute(create_sql)
                    print(f"[OK] Table '{table_name}' created/verified successfully")
                except Error as e:
                    print(f"[ERROR] Error creating table '{table_name}': {e}")
                    raise
            
            connection.commit()
            print("[OK] All database tables created successfully!")

# Global database manager instance
db_manager = DatabaseManager()
