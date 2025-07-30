"""
User Page Object
Handles user dashboard and article viewing page logic
"""

from pages.base_page import BasePage
from services.article_service import ArticleService
from models import Comment


class UserDashboardPage(BasePage):
    """Page object for user dashboard"""
    
    def __init__(self):
        super().__init__()
        self.page_name = "user_dashboard"
        self.article_service = ArticleService()
    
    def get_template_name(self):
        return 'user/home.html'
    
    def render_dashboard(self):
        """Render user dashboard with published articles"""
        articles = self.article_service.get_published_articles()
        categories = self.article_service.get_all_categories()
        
        return self.render(articles=articles, categories=categories)


class ArticleViewPage(BasePage):
    """Page object for viewing individual articles"""
    
    def __init__(self):
        super().__init__()
        self.page_name = "article_view"
        self.article_service = ArticleService()
    
    def get_template_name(self):
        return 'user/article.html'
    
    def render_article(self, article_id):
        """
        Render article details with comments
        
        Args:
            article_id (int): Article ID
            
        Returns:
            Rendered template or redirect
        """
        article = self.article_service.get_article_by_id(article_id)
        
        if not article or article.status != 'published':
            self.flash_message('Article not found or not published', 'error')
            return self.redirect_to('user.dashboard')
        
        # Get comments for this article, ordered by creation date
        from models import Comment
        comments = Comment.query.filter_by(article_id=article_id).order_by(Comment.created_at.desc()).all()
        
        return self.render(article=article, comments=comments)


class CommentPage(BasePage):
    """Page object for comment functionality"""
    
    def __init__(self):
        super().__init__()
        self.page_name = "comment"
    
    def get_template_name(self):
        return None  # Comments don't have their own template
    
    def process_add_comment(self, article_id, content):
        """
        Process adding a comment to an article
        
        Args:
            article_id (int): Article ID
            content (str): Comment content
            
        Returns:
            tuple: (success: bool, redirect_url: str, error: str or None)
        """
        if not content or not content.strip():
            self.flash_message('Comment cannot be empty', 'error')
            return False, f'user.article', 'Comment cannot be empty'
        
        user_id = self.get_current_user_id()
        if not user_id:
            self.flash_message('You must be logged in to comment', 'error')
            return False, 'auth.login', 'Not logged in'
        
        try:
            from config import db
            comment = Comment(
                user_id=user_id,
                article_id=article_id,
                content=content.strip()
            )
            
            db.session.add(comment)
            db.session.commit()
            
            self.flash_message('Comment added successfully!', 'success')
            return True, f'user.article', None
            
        except Exception as e:
            from config import db
            db.session.rollback()
            error_msg = f'Failed to add comment: {str(e)}'
            self.flash_message(error_msg, 'error')
            return False, f'user.article', error_msg
