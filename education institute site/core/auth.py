"""
Authentication and user management using mysql.connector
Replaces Flask-Login and SQLAlchemy User model functionality
"""

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .database import db_manager

class User(UserMixin):
    """User class for Flask-Login compatibility"""
    
    def __init__(self, user_data):
        self.id = user_data['id']
        self.name = user_data['name']
        self.email = user_data['email']
        self.password_hash = user_data['password_hash']
        self.role = user_data['role']
        self._is_active = user_data['is_active']  # Use private attribute
        self.created_at = user_data.get('created_at')
        self.updated_at = user_data.get('updated_at')
    
    def check_password(self, password):
        """Check if provided password matches user's password"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Return user ID as string for Flask-Login"""
        return str(self.id)
    
    @property
    def is_active(self):
        """Return whether user is active"""
        return self._is_active
    
    @property
    def is_authenticated(self):
        """Return True if user is authenticated"""
        return True
    
    @property
    def is_anonymous(self):
        """Return False since this is not an anonymous user"""
        return False
    
    def has_role(self, role):
        """Check if user has specific role"""
        return self.role == role

class AuthService:
    """Authentication service for user management"""
    
    @staticmethod
    def create_user(name, email, password, role='student'):
        """Create a new user"""
        password_hash = generate_password_hash(password)
        
        query = """
            INSERT INTO users (name, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
        """
        
        try:
            result = db_manager.execute_query(
                query, 
                (name, email, password_hash, role)
            )
            return result > 0
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = %s AND is_active = TRUE"
        
        try:
            user_data = db_manager.execute_query(
                query, 
                (user_id,), 
                fetch_one=True
            )
            
            if user_data:
                return User(user_data)
            return None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email"""
        query = "SELECT * FROM users WHERE email = %s AND is_active = TRUE"
        
        try:
            user_data = db_manager.execute_query(
                query, 
                (email,), 
                fetch_one=True
            )
            
            if user_data:
                return User(user_data)
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user with email and password"""
        user = AuthService.get_user_by_email(email)
        
        if user and user.check_password(password):
            return user
        return None
    
    @staticmethod
    def get_all_users(role=None):
        """Get all users, optionally filtered by role"""
        if role:
            query = "SELECT * FROM users WHERE role = %s AND is_active = TRUE ORDER BY name"
            params = (role,)
        else:
            query = "SELECT * FROM users WHERE is_active = TRUE ORDER BY name"
            params = ()
        
        try:
            users_data = db_manager.execute_query(query, params, fetch=True)
            return [User(user_data) for user_data in users_data]
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    @staticmethod
    def update_user(user_id, **kwargs):
        """Update user information"""
        allowed_fields = ['name', 'email', 'role', 'is_active']
        update_fields = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = %s")
                params.append(value)
        
        if not update_fields:
            return False
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
        
        try:
            result = db_manager.execute_query(query, params)
            return result > 0
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    @staticmethod
    def delete_user(user_id):
        """Soft delete user (set is_active to False)"""
        query = "UPDATE users SET is_active = FALSE WHERE id = %s"
        
        try:
            result = db_manager.execute_query(query, (user_id,))
            return result > 0
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    @staticmethod
    def change_password(user_id, new_password):
        """Change user password"""
        password_hash = generate_password_hash(new_password)
        query = "UPDATE users SET password_hash = %s WHERE id = %s"
        
        try:
            result = db_manager.execute_query(query, (password_hash, user_id))
            return result > 0
        except Exception as e:
            print(f"Error changing password: {e}")
            return False

# User loader function for Flask-Login
def load_user(user_id):
    """Load user for Flask-Login"""
    return AuthService.get_user_by_id(int(user_id))
