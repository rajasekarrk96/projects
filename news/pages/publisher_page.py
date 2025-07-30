"""
Publisher Page Object
Handles publisher dashboard and article management page logic
"""

from pages.base_page import BasePage
from services.article_service import ArticleService


class PublisherDashboardPage(BasePage):
    """Page object for publisher dashboard"""
    
    def __init__(self):
        super().__init__()
        self.page_name = "publisher_dashboard"
        self.article_service = ArticleService()
    
    def get_template_name(self):
        return 'publisher/dashboard.html'
    
    def render_dashboard(self):
        """Render publisher dashboard with user's articles"""
        user_id = self.get_current_user_id()
        articles = self.article_service.get_articles_by_user(user_id)
        
        return self.render(articles=articles)


class CreateArticlePage(BasePage):
    """Page object for creating articles"""
    
    def __init__(self):
        super().__init__()
        self.page_name = "create_article"
        self.article_service = ArticleService()
    
    def get_template_name(self):
        return 'publisher/create.html'
    
    def render_create_form(self):
        """Render article creation form"""
        categories = self.article_service.get_all_categories()
        return self.render(categories=categories)
    
    def process_create_article(self, title, content, category_id, is_anonymous=False, media_file=None):
        """
        Process article creation
        
        Args:
            title (str): Article title
            content (str): Article content
            category_id (int): Category ID
            is_anonymous (bool): Whether article is anonymous
            media_file: Uploaded media file
            
        Returns:
            tuple: (success: bool, redirect_url: str or None, error: str or None)
        """
        user_id = self.get_current_user_id()
        
        article, error = self.article_service.create_article(
            title=title,
            content=content,
            category_id=int(category_id),
            created_by=user_id,
            is_anonymous=is_anonymous
        )
        
        if error:
            self.flash_message(error, 'error')
            return False, None, error
        
        # Handle media file upload if provided
        if media_file and media_file.filename:
            media_path = self.article_service.save_media_file(media_file, article.id)
            if not media_path:
                self.flash_message('Failed to upload media file', 'warning')
        
        self.flash_message('Article created successfully!', 'success')
        return True, 'publisher.dashboard', None


class EditArticlePage(BasePage):
    """Page object for editing articles"""
    
    def __init__(self):
        super().__init__()
        self.page_name = "edit_article"
        self.article_service = ArticleService()
    
    def get_template_name(self):
        return 'publisher/edit.html'
    
    def render_edit_form(self, article_id):
        """
        Render article edit form
        
        Args:
            article_id (int): Article ID
            
        Returns:
            Rendered template or redirect
        """
        article = self.article_service.get_article_by_id(article_id)
        
        if not article:
            self.flash_message('Article not found', 'error')
            return self.redirect_to('publisher.dashboard')
        
        # Check if user owns the article
        user_id = self.get_current_user_id()
        if article.created_by != user_id:
            self.flash_message('You can only edit your own articles', 'error')
            return self.redirect_to('publisher.dashboard')
        
        # Check if article can be edited
        if article.status == 'published':
            self.flash_message('Published articles cannot be edited', 'error')
            return self.redirect_to('publisher.dashboard')
        
        categories = self.article_service.get_all_categories()
        return self.render(article=article, categories=categories)
    
    def process_edit_article(self, article_id, title, content, category_id, is_anonymous=False):
        """
        Process article editing
        
        Args:
            article_id (int): Article ID
            title (str): Updated title
            content (str): Updated content
            category_id (int): Updated category ID
            is_anonymous (bool): Whether article is anonymous
            
        Returns:
            tuple: (success: bool, redirect_url: str or None, error: str or None)
        """
        article, error = self.article_service.update_article(
            article_id=article_id,
            title=title,
            content=content,
            category_id=int(category_id),
            is_anonymous=is_anonymous
        )
        
        if error:
            self.flash_message(error, 'error')
            return False, None, error
        
        self.flash_message('Article updated successfully!', 'success')
        return True, 'publisher.dashboard', None


class ArticleActionsPage(BasePage):
    """Page object for article actions (delete, submit)"""
    
    def __init__(self):
        super().__init__()
        self.page_name = "article_actions"
        self.article_service = ArticleService()
    
    def get_template_name(self):
        return None  # Actions don't render templates
    
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
        
        return success, 'publisher.dashboard', error
    
    def process_submit_article(self, article_id):
        """
        Process article submission for approval
        
        Args:
            article_id (int): Article ID
            
        Returns:
            tuple: (success: bool, redirect_url: str, message: str)
        """
        success, error = self.article_service.submit_article_for_approval(article_id)
        
        if error:
            self.flash_message(error, 'error')
        else:
            self.flash_message('Article submitted for approval!', 'success')
        
        return success, 'publisher.dashboard', error
