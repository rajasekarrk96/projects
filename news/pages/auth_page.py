"""
Authentication Page Object
Handles login and registration page logic
"""

from pages.base_page import BasePage
from services.auth_service import AuthService


class LoginPage(BasePage):
    """Page object for login functionality"""
    
    def __init__(self):
        super().__init__()
        self.page_name = "login"
        self.auth_service = AuthService()
    
    def get_template_name(self):
        return 'auth/login.html'
    
    def process_login(self, username, password):
        """
        Process user login
        
        Args:
            username (str): Username
            password (str): Password
            
        Returns:
            tuple: (success: bool, redirect_url: str or None, error: str or None)
        """
        user, error = self.auth_service.authenticate_user(username, password)
        
        if error:
            self.flash_message(error, 'error')
            return False, None, error
        
        # Set session data
        self.set_session_data('user_id', user.id)
        self.set_session_data('username', user.username)
        self.set_session_data('role', user.role.name)
        
        self.flash_message(f'Welcome back, {user.username}!', 'success')
        
        # Redirect based on role
        if user.role.name == 'admin':
            return True, 'admin.dashboard', None
        elif user.role.name == 'publisher':
            return True, 'publisher.dashboard', None
        elif user.role.name == 'superadmin':
            return True, 'superadmin.dashboard', None
        else:
            return True, 'user.dashboard', None
    
    def render_login_form(self):
        """Render the login form"""
        return self.render()


class RegistrationPage(BasePage):
    """Page object for registration functionality"""
    
    def __init__(self):
        super().__init__()
        self.page_name = "register"
        self.auth_service = AuthService()
    
    def get_template_name(self):
        return 'auth/register.html'
    
    def process_registration(self, username, email, password, confirm_password, role_name='user'):
        """
        Process user registration
        
        Args:
            username (str): Username
            email (str): Email
            password (str): Password
            confirm_password (str): Password confirmation
            role_name (str): Role name
            
        Returns:
            tuple: (success: bool, redirect_url: str or None, error: str or None)
        """
        # Restrict admin/superadmin role creation to admins only
        if role_name.lower() in ['admin', 'superadmin']:
            error = "Admin and SuperAdmin accounts can only be created by existing admins"
            self.flash_message(error, 'error')
            return False, None, error
        
        # Validate password confirmation
        if password != confirm_password:
            error = "Passwords do not match"
            self.flash_message(error, 'error')
            return False, None, error
        
        user, error = self.auth_service.register_user(username, email, password, role_name)
        
        if error:
            self.flash_message(error, 'error')
            return False, None, error
        
        self.flash_message(
            'Registration successful! Your account is pending approval.', 
            'success'
        )
        
        return True, 'auth.login', None
    
    def render_registration_form(self):
        """Render the registration form with allowed roles for self-registration"""
        # Only allow user and publisher roles for self-registration
        all_roles = self.auth_service.get_all_roles()
        allowed_roles = [role for role in all_roles if role.name.lower() in ['user', 'publisher']]
        return self.render(roles=allowed_roles)


class LogoutPage(BasePage):
    """Page object for logout functionality"""
    
    def __init__(self):
        super().__init__()
        self.page_name = "logout"
    
    def get_template_name(self):
        return None  # Logout doesn't render a template
    
    def process_logout(self):
        """
        Process user logout
        
        Returns:
            str: Redirect URL
        """
        username = self.get_session_data('username', 'User')
        self.clear_session()
        self.flash_message(f'Goodbye, {username}!', 'info')
        return 'index'
