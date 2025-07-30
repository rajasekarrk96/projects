"""
Utility helper functions for the Flask News Portal
"""

import os
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename


class FileHelper:
    """Helper class for file operations"""
    
    @staticmethod
    def save_uploaded_file(file, upload_folder='uploads', prefix=''):
        """
        Save an uploaded file with security measures
        
        Args:
            file: Uploaded file object
            upload_folder (str): Folder name within static directory
            prefix (str): Prefix for filename
            
        Returns:
            tuple: (relative_path: str or None, error: str or None)
        """
        if not file or not file.filename:
            return None, "No file provided"
        
        try:
            # Create uploads directory if it doesn't exist
            uploads_dir = os.path.join(current_app.root_path, 'static', upload_folder)
            if not os.path.exists(uploads_dir):
                os.makedirs(uploads_dir)
            
            # Secure the filename and add timestamp
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            
            if prefix:
                filename = f"{prefix}_{timestamp}_{filename}"
            else:
                filename = f"{timestamp}_{filename}"
            
            file_path = os.path.join(uploads_dir, filename)
            file.save(file_path)
            
            # Return relative path for web access
            relative_path = f"/static/{upload_folder}/{filename}"
            return relative_path, None
            
        except Exception as e:
            return None, f"Failed to save file: {str(e)}"
    
    @staticmethod
    def delete_file(file_path):
        """
        Delete a file from the filesystem
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            tuple: (success: bool, error: str or None)
        """
        try:
            if file_path.startswith('/static/'):
                # Convert web path to filesystem path
                file_path = file_path[1:]  # Remove leading slash
                full_path = os.path.join(current_app.root_path, file_path)
            else:
                full_path = file_path
            
            if os.path.exists(full_path):
                os.remove(full_path)
                return True, None
            else:
                return False, "File not found"
                
        except Exception as e:
            return False, f"Failed to delete file: {str(e)}"


class ValidationHelper:
    """Helper class for data validation"""
    
    @staticmethod
    def validate_email(email):
        """
        Basic email validation
        
        Args:
            email (str): Email address
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not email or '@' not in email or '.' not in email:
            return False
        
        parts = email.split('@')
        if len(parts) != 2:
            return False
        
        local, domain = parts
        if not local or not domain:
            return False
        
        return True
    
    @staticmethod
    def validate_password_strength(password):
        """
        Validate password strength
        
        Args:
            password (str): Password
            
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        return True, "Password is valid"
    
    @staticmethod
    def validate_required_fields(data, required_fields):
        """
        Validate that required fields are present and not empty
        
        Args:
            data (dict): Data to validate
            required_fields (list): List of required field names
            
        Returns:
            tuple: (is_valid: bool, missing_fields: list)
        """
        missing_fields = []
        
        for field in required_fields:
            if field not in data or not data[field] or str(data[field]).strip() == '':
                missing_fields.append(field)
        
        return len(missing_fields) == 0, missing_fields


class DateHelper:
    """Helper class for date operations"""
    
    @staticmethod
    def format_datetime(dt, format_string='%Y-%m-%d %H:%M:%S'):
        """
        Format datetime object to string
        
        Args:
            dt (datetime): Datetime object
            format_string (str): Format string
            
        Returns:
            str: Formatted datetime string
        """
        if not dt:
            return ""
        
        return dt.strftime(format_string)
    
    @staticmethod
    def get_time_ago(dt):
        """
        Get human-readable time ago string
        
        Args:
            dt (datetime): Datetime object
            
        Returns:
            str: Time ago string (e.g., "2 hours ago")
        """
        if not dt:
            return ""
        
        now = datetime.utcnow()
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
