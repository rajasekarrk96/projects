"""
SuperAdmin Page Object
Handles superadmin dashboard and system management page logic
"""

from pages.base_page import BasePage
from services.user_service import UserService
from services.article_service import ArticleService
from approval import get_pending_approval_requests, process_approval_request


class SuperAdminDashboardPage(BasePage):
    """Page object for superadmin dashboard"""
    
    def __init__(self):
        super().__init__()
        self.page_name = "superadmin_dashboard"
        self.user_service = UserService()
        self.article_service = ArticleService()
    
    def get_template_name(self):
        return 'superadmin/dashboard.html'
    
    def render_dashboard(self):
        """Render superadmin dashboard with system statistics"""
        # Get comprehensive statistics
        user_stats = self.user_service.get_user_statistics()
        pending_approvals = get_pending_approval_requests()
        total_articles = len(self.article_service.get_published_articles())
        pending_articles = len(self.article_service.get_articles_by_status('pending'))
        
        context = {
            'user_count': user_stats['total_users'],
            'active_users': user_stats['active_users'],
            'pending_users': user_stats['pending_approval'],
            'article_count': total_articles,
            'pending_articles': pending_articles,
            'pending_approvals': len(pending_approvals),
            'approval_requests': pending_approvals
        }
        
        return self.render(**context)


class ApprovalManagementPage(BasePage):
    """Page object for managing approval requests"""
    
    def __init__(self):
        super().__init__()
        self.page_name = "approval_management"
    
    def get_template_name(self):
        return 'superadmin/approvals.html'
    
    def render_approval_requests(self):
        """Render all pending approval requests"""
        pending_requests = get_pending_approval_requests()
        return self.render(approval_requests=pending_requests)
    
    def process_approval_request(self, request_id, action):
        """
        Process an approval request
        
        Args:
            request_id (int): Approval request ID
            action (str): 'approve' or 'reject'
            
        Returns:
            tuple: (success: bool, redirect_url: str, error: str or None)
        """
        if action not in ['approve', 'reject']:
            error = "Invalid action"
            self.flash_message(error, 'error')
            return False, 'superadmin.approval_requests', error
        
        approved_by = self.get_current_user_id()
        status = 'approved' if action == 'approve' else 'rejected'
        
        success = process_approval_request(request_id, approved_by, status)
        
        if success:
            message = f'Request {action}d successfully!'
            self.flash_message(message, 'success')
            return True, 'superadmin.approval_requests', None
        else:
            error = f'Failed to {action} request'
            self.flash_message(error, 'error')
            return False, 'superadmin.approval_requests', error


class SystemManagementPage(BasePage):
    """Page object for system management operations"""
    
    def __init__(self):
        super().__init__()
        self.page_name = "system_management"
        self.user_service = UserService()
    
    def get_template_name(self):
        return 'superadmin/system_management.html'
    
    def render_system_management(self):
        """Render system management page"""
        all_users = self.user_service.get_all_users()
        return self.render(users=all_users)
    
    def process_user_action(self, user_id, action):
        """
        Process user management actions
        
        Args:
            user_id (int): User ID
            action (str): Action to perform
            
        Returns:
            tuple: (success: bool, redirect_url: str, error: str or None)
        """
        if action == 'activate':
            success, error = self.user_service.activate_user(user_id)
            message = 'User activated successfully!' if success else error
        elif action == 'deactivate':
            success, error = self.user_service.deactivate_user(user_id)
            message = 'User deactivated successfully!' if success else error
        elif action == 'approve':
            success, error = self.user_service.approve_user(user_id)
            message = 'User approved successfully!' if success else error
        elif action == 'reject':
            success, error = self.user_service.reject_user_approval(user_id)
            message = 'User approval rejected successfully!' if success else error
        else:
            success, error = False, 'Invalid action'
            message = error
        
        if success:
            self.flash_message(message, 'success')
        else:
            self.flash_message(message, 'error')
        
        return success, 'superadmin.system_management', error
