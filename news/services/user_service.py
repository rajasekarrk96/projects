"""
User Service Layer
Handles all user-related business logic
"""

from config import db
from models import User, Role
from approval import create_approval_request


class UserService:
    """Service class for user operations"""
    
    @staticmethod
    def get_all_users():
        """
        Get all users
        
        Returns:
            List of User objects
        """
        return User.query.all()
    
    @staticmethod
    def get_users_by_role(role_name):
        """
        Get users by role name
        
        Args:
            role_name (str): Role name
            
        Returns:
            List of User objects
        """
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            return []
        
        return User.query.filter_by(role_id=role.id).all()
    
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
    def activate_user(user_id):
        """
        Activate a user account
        
        Args:
            user_id (int): User ID
            
        Returns:
            tuple: (bool, error message or None)
        """
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        try:
            user.is_active = True
            db.session.commit()
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to activate user: {str(e)}"
    
    @staticmethod
    def deactivate_user(user_id):
        """
        Deactivate a user account
        
        Args:
            user_id (int): User ID
            
        Returns:
            tuple: (bool, error message or None)
        """
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        try:
            user.is_active = False
            db.session.commit()
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to deactivate user: {str(e)}"
    
    @staticmethod
    def approve_user(user_id):
        """
        Approve a user account
        
        Args:
            user_id (int): User ID
            
        Returns:
            tuple: (bool, error message or None)
        """
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        try:
            user.is_approved = True
            db.session.commit()
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to approve user: {str(e)}"
    
    @staticmethod
    def reject_user_approval(user_id):
        """
        Reject user approval
        
        Args:
            user_id (int): User ID
            
        Returns:
            tuple: (bool, error message or None)
        """
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        try:
            user.is_approved = False
            db.session.commit()
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to reject user approval: {str(e)}"
    
    @staticmethod
    def update_user_role(user_id, new_role_name):
        """
        Update user role
        
        Args:
            user_id (int): User ID
            new_role_name (str): New role name
            
        Returns:
            tuple: (bool, error message or None)
        """
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        role = Role.query.filter_by(name=new_role_name).first()
        if not role:
            return False, "Role not found"
        
        try:
            user.role_id = role.id
            db.session.commit()
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to update user role: {str(e)}"
    
    @staticmethod
    def flag_user_for_deactivation(user_id, requester_id):
        """
        Flag user for deactivation (creates approval request)
        
        Args:
            user_id (int): User ID to flag
            requester_id (int): ID of user making the request
            
        Returns:
            tuple: (bool, error message or None)
        """
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        # Create approval request for deactivating user
        approval_request, error = create_approval_request(
            user_id=requester_id,
            target_type='user',
            target_id=user_id,
            action_type='deactivate'
        )
        
        if error:
            return False, error
        
        return True, None
    
    @staticmethod
    def get_user_statistics():
        """
        Get user statistics
        
        Returns:
            dict: User statistics
        """
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        approved_users = User.query.filter_by(is_approved=True).count()
        pending_approval = User.query.filter_by(is_approved=False).count()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'approved_users': approved_users,
            'pending_approval': pending_approval
        }
