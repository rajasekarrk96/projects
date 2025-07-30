"""
Authentication Service Layer
Handles all authentication-related business logic
"""

from werkzeug.security import generate_password_hash, check_password_hash
from config import db
from models import User, Role
from approval import create_approval_request


class AuthService:
    """Service class for authentication operations"""
    
    @staticmethod
    def authenticate_user(username, password):
        """
        Authenticate user with username and password
        
        Args:
            username (str): Username
            password (str): Password
            
        Returns:
            tuple: (User object or None, error message or None)
        """
        if not username or not password:
            return None, "Username and password are required"
        
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return None, "Invalid username or password"
        
        if not user.check_password(password):
            return None, "Invalid username or password"
        
        if not user.is_active:
            return None, "Your account has been deactivated"
        
        if not user.is_approved:
            return None, "Your account is pending approval"
        
        return user, None
    
    @staticmethod
    def register_user(username, email, password, role_name='user'):
        """
        Register a new user
        
        Args:
            username (str): Username
            email (str): Email address
            password (str): Password
            role_name (str): Role name (default: 'user')
            
        Returns:
            tuple: (User object or None, error message or None)
        """
        # Validate input
        if not username or not email or not password:
            return None, "All fields are required"
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return None, "Username already exists"
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return None, "Email already exists"
        
        # Get role
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            return None, "Invalid role"
        
        try:
            # Create new user
            user = User(
                username=username,
                email=email,
                role_id=role.id,
                is_active=True,
                is_approved=False  # Requires approval
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # Create approval request for new user
            create_approval_request(
                user_id=user.id,
                target_type='user',
                target_id=user.id,
                action_type='approve_registration'
            )
            
            return user, None
            
        except Exception as e:
            db.session.rollback()
            return None, f"Registration failed: {str(e)}"
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Get user by ID
        
        Args:
            user_id (int): User ID
            
        Returns:
            User object or None
        """
        return User.query.get(user_id)
    
    @staticmethod
    def check_user_role(user_id, allowed_roles):
        """
        Check if user has required role
        
        Args:
            user_id (int): User ID
            allowed_roles (list): List of allowed role names
            
        Returns:
            tuple: (bool, error message or None)
        """
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        if not user.is_active or not user.is_approved:
            return False, "User account is not active or approved"
        
        role = Role.query.get(user.role_id)
        if not role or role.name.lower() not in [r.lower() for r in allowed_roles]:
            return False, "Insufficient permissions"
        
        return True, None
    
    @staticmethod
    def create_admin_user(username, email, password, role_name):
        """
        Create admin or superadmin user (only callable by admins)
        
        Args:
            username (str): Username
            email (str): Email address
            password (str): Password
            role_name (str): Role name (admin or superadmin)
            
        Returns:
            tuple: (User object or None, error message or None)
        """
        # Validate input
        if not username or not email or not password:
            return None, "All fields are required"
        
        # Validate role is admin or superadmin
        if role_name.lower() not in ['admin', 'superadmin']:
            return None, "Only admin and superadmin roles can be created through this method"
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return None, "Username already exists"
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return None, "Email already exists"
        
        # Get role
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            return None, "Invalid role"
        
        try:
            # Create new admin user with auto-approval
            user = User(
                username=username,
                email=email,
                role_id=role.id,
                is_active=True,
                is_approved=True  # Admin-created accounts are auto-approved
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return user, None
            
        except Exception as e:
            db.session.rollback()
            return None, f"Account creation failed: {str(e)}"
    
    @staticmethod
    def get_all_roles():
        """
        Get all available roles
        
        Returns:
            List of Role objects
        """
        return Role.query.all()
