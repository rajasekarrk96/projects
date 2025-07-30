"""
Admin Page Object
Handles admin dashboard and management page logic
"""

from pages.base_page import BasePage
from services.article_service import ArticleService
from services.user_service import UserService
from services.auth_service import AuthService
from approval import get_pending_approval_requests


class AdminDashboardPage(BasePage):
    """Page object for admin dashboard"""
    
    def __init__(self):
        super().__init__()
        self.page_name = "admin_dashboard"
        self.article_service = ArticleService()
        self.user_service = UserService()
    
    def get_template_name(self):
        return 'admin/dashboard.html'
    
    def render_dashboard(self):
        """Render admin dashboard with statistics"""
        # Get statistics
        user_stats = self.user_service.get_user_statistics()
        pending_articles = len(self.article_service.get_articles_by_status('pending'))
        pending_approvals = len(get_pending_approval_requests())
        total_articles = len(self.article_service.get_published_articles())
        
        context = {
            'user_count': user_stats['total_users'],
            'article_count': total_articles,
            'pending_articles': pending_articles,
            'pending_approvals': pending_approvals
        }
        
        return self.render(**context)


class UserManagementPage(BasePage):
    """Page object for user management"""
    
    def __init__(self):
        super().__init__()
        self.page_name = "user_management"
        self.user_service = UserService()
    
    def get_template_name(self):
        return 'admin/users.html'
    
    def render_users_list(self):
        """Render users management page"""
        users = self.user_service.get_all_users()
        roles = self.user_service.get_all_roles() if hasattr(self.user_service, 'get_all_roles') else []
        
        return self.render(users=users, roles=roles)
    
    def render_publishers_list(self):
        """Render publishers management page"""
        publishers = self.user_service.get_users_by_role('publisher')
        return self.render(template_name='admin/publishers.html', publishers=publishers)


class ArticleApprovalPage(BasePage):
    """Page object for article approval"""
    
    def __init__(self):
        super().__init__()
        self.page_name = "article_approval"
        self.article_service = ArticleService()
    
    def get_template_name(self):
        return 'admin/pending_articles.html'
    
    def render_pending_articles(self):
        """Render pending articles for approval"""
        pending_articles = self.article_service.get_articles_by_status('pending')
        return self.render(articles=pending_articles)
    
    def render_article_details(self, article_id):
        """
        Render article details for review
        
        Args:
            article_id (int): Article ID
            
        Returns:
            Rendered template or redirect
        """
        article = self.article_service.get_article_by_id(article_id)
        
        if not article:
            self.flash_message('Article not found', 'error')
            return self.redirect_to('admin.pending_articles')
        
        return self.render(template_name='admin/article_details.html', article=article)
    
    def process_approve_article(self, article_id):
        """
        Process article approval
        
        Args:
            article_id (int): Article ID
            
        Returns:
            tuple: (success: bool, redirect_url: str, message: str)
        """
        user_id = self.get_current_user_id()
        success, error = self.article_service.approve_article(article_id, user_id)
        
        if error:
            self.flash_message(error, 'error')
        else:
            self.flash_message('Article approved successfully!', 'success')
        
        return success, 'admin.pending_articles', error
    
    def process_reject_article(self, article_id):
        """
        Process article rejection
        
        Args:
            article_id (int): Article ID
            
        Returns:
            tuple: (success: bool, redirect_url: str, message: str)
        """
        success, error = self.article_service.reject_article(article_id)
        
        if error:
            self.flash_message(error, 'error')
        else:
            self.flash_message('Article rejected successfully!', 'success')
        
        return success, 'admin.pending_articles', error
    
    def process_delete_article(self, article_id):
        """
        Process article deletion
        
        Args:
            article_id (int): Article ID
            
        Returns:
            tuple: (success: bool, redirect_url: str, message: str)
        """
        user_id = self.get_current_user_id()
        success, error = self.article_service.delete_article(article_id, user_id)
        
        if error:
            self.flash_message(error, 'error')
        else:
            self.flash_message('Article deleted successfully!', 'success')
        
        return success, 'admin.pending_articles', error


class UserActionsPage(BasePage):
    """Page object for user actions"""
    
    def __init__(self):
        super().__init__()
        self.page_name = "user_actions"
        self.user_service = UserService()
    
    def get_template_name(self):
        return None  # Actions don't render templates
    
    def process_flag_user(self, user_id):
        """
        Process user flagging for deactivation
        
        Args:
            user_id (int): User ID to flag
            
        Returns:
            tuple: (success: bool, redirect_url: str, message: str)
        """
        requester_id = self.get_current_user_id()
        success, error = self.user_service.flag_user_for_deactivation(user_id, requester_id)
        
        if error:
            self.flash_message(error, 'error')
        else:
            self.flash_message('User flagged for deactivation. Request sent to Super Admin.', 'success')
        
        return success, 'admin.view_users', error


class AdminUserCreationPage(BasePage):
    """Page object for admin user creation"""
    
    def __init__(self):
        super().__init__()
        self.page_name = "admin_user_creation"
        self.auth_service = AuthService()
    
    def get_template_name(self):
        return 'admin/create_user.html'
    
    def render_create_user_form(self):
        """Render form for creating admin/superadmin users"""
        # Only show admin and superadmin roles for admin creation
        all_roles = self.auth_service.get_all_roles()
        admin_roles = [role for role in all_roles if role.name.lower() in ['admin', 'superadmin']]
        return self.render(roles=admin_roles)
    
    def process_create_admin_user(self, username, email, password, confirm_password, role_name):
        """
        Process admin user creation
        
        Args:
            username (str): Username
            email (str): Email
            password (str): Password
            confirm_password (str): Password confirmation
            role_name (str): Role name (admin or superadmin)
            
        Returns:
            tuple: (success: bool, redirect_url: str or None, error: str or None)
        """
        # Validate that only admin/superadmin roles are being created
        if role_name.lower() not in ['admin', 'superadmin']:
            error = "This interface is only for creating admin and superadmin accounts"
            self.flash_message(error, 'error')
            return False, None, error
        
        # Validate password confirmation
        if password != confirm_password:
            error = "Passwords do not match"
            self.flash_message(error, 'error')
            return False, None, error
        
        # Create the admin user with auto-approval
        user, error = self.auth_service.create_admin_user(username, email, password, role_name)
        
        if error:
            self.flash_message(error, 'error')
            return False, None, error
        
        self.flash_message(
            f'{role_name.title()} account created successfully for {username}!', 
            'success'
        )
        
        return True, 'admin.view_users', None
