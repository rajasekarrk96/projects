"""
Base Page Object Model class for the Flask News Portal
This class provides common functionality for all page objects
"""

from flask import render_template, flash, redirect, url_for, session
from abc import ABC, abstractmethod


class BasePage(ABC):
    """
    Abstract base class for all page objects.
    Provides common functionality and enforces structure.
    """
    
    def __init__(self):
        self.template_folder = None
        self.page_name = None
    
    @abstractmethod
    def get_template_name(self):
        """Return the template name for this page"""
        pass
    
    def render(self, **context):
        """
        Render the page template with given context
        
        Args:
            **context: Template context variables
            
        Returns:
            Rendered template response
        """
        template_name = self.get_template_name()
        return render_template(template_name, **context)
    
    def flash_message(self, message, category='info'):
        """
        Flash a message to the user
        
        Args:
            message (str): Message to display
            category (str): Message category (info, success, warning, error)
        """
        flash(message, category)
    
    def redirect_to(self, endpoint, **values):
        """
        Redirect to another page
        
        Args:
            endpoint (str): Flask endpoint name
            **values: URL parameters
            
        Returns:
            Redirect response
        """
        return redirect(url_for(endpoint, **values))
    
    def get_current_user_id(self):
        """
        Get the current logged-in user ID from session
        
        Returns:
            int: User ID or None if not logged in
        """
        return session.get('user_id')
    
    def is_user_logged_in(self):
        """
        Check if user is logged in
        
        Returns:
            bool: True if user is logged in, False otherwise
        """
        return 'user_id' in session
    
    def clear_session(self):
        """Clear the user session"""
        session.clear()
    
    def set_session_data(self, key, value):
        """
        Set session data
        
        Args:
            key (str): Session key
            value: Session value
        """
        session[key] = value
    
    def get_session_data(self, key, default=None):
        """
        Get session data
        
        Args:
            key (str): Session key
            default: Default value if key not found
            
        Returns:
            Session value or default
        """
        return session.get(key, default)
