"""
Article Service Layer
Handles all article-related business logic
"""

from config import db
from models import Article, Category, Media, User
from datetime import datetime
import os
from flask import current_app
from werkzeug.utils import secure_filename


class ArticleService:
    """Service class for article operations"""
    
    @staticmethod
    def create_article(title, content, category_id, created_by, is_anonymous=False):
        """
        Create a new article
        
        Args:
            title (str): Article title
            content (str): Article content
            category_id (int): Category ID
            created_by (int): User ID of creator
            is_anonymous (bool): Whether article is anonymous
            
        Returns:
            tuple: (Article object or None, error message or None)
        """
        if not title or not content or not category_id:
            return None, "Title, content, and category are required"
        
        # Validate category exists
        category = Category.query.get(category_id)
        if not category:
            return None, "Invalid category"
        
        try:
            new_article = Article(
                title=title,
                content=content,
                category_id=category_id,
                created_by=created_by,
                is_anonymous=is_anonymous,
                status='draft'
            )
            
            db.session.add(new_article)
            db.session.commit()
            
            # Log article creation activity
            from utils.system_logger import log_article_created
            log_article_created(new_article.id, title, created_by)
            
            return new_article, None
            
        except Exception as e:
            db.session.rollback()
            return None, f"Failed to create article: {str(e)}"
    
    @staticmethod
    def update_article(article_id, title, content, category_id, is_anonymous=False):
        """
        Update an existing article
        
        Args:
            article_id (int): Article ID
            title (str): Updated title
            content (str): Updated content
            category_id (int): Updated category ID
            is_anonymous (bool): Whether article is anonymous
            
        Returns:
            tuple: (Article object or None, error message or None)
        """
        article = Article.query.get(article_id)
        if not article:
            return None, "Article not found"
        
        if article.status == 'published':
            return None, "Cannot edit published articles"
        
        if not title or not content or not category_id:
            return None, "Title, content, and category are required"
        
        # Validate category exists
        category = Category.query.get(category_id)
        if not category:
            return None, "Invalid category"
        
        try:
            article.title = title
            article.content = content
            article.category_id = category_id
            article.is_anonymous = is_anonymous
            
            db.session.commit()
            
            return article, None
            
        except Exception as e:
            db.session.rollback()
            return None, f"Failed to update article: {str(e)}"
    
    @staticmethod
    def delete_article(article_id, user_id):
        """
        Delete an article
        
        Args:
            article_id (int): Article ID
            user_id (int): User ID requesting deletion
            
        Returns:
            tuple: (bool, error message or None)
        """
        article = Article.query.get(article_id)
        if not article:
            return False, "Article not found"
        
        # Check if user owns the article or is admin
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        if article.created_by != user_id and user.role.name not in ['admin', 'superadmin']:
            return False, "You don't have permission to delete this article"
        
        try:
            db.session.delete(article)
            db.session.commit()
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to delete article: {str(e)}"
    
    @staticmethod
    def submit_article_for_approval(article_id):
        """
        Submit article for approval
        
        Args:
            article_id (int): Article ID
            
        Returns:
            tuple: (bool, error message or None)
        """
        from flask import session
        from approval import create_approval_request
        
        article = Article.query.get(article_id)
        if not article:
            return False, "Article not found"
        
        if article.status != 'draft':
            return False, "Only draft articles can be submitted for approval"
        
        try:
            # Update article status
            article.status = 'pending'
            
            # Create approval request
            user_id = session.get('user_id')
            if user_id:
                approval_request, error = create_approval_request(
                    user_id=user_id,
                    target_type='article',
                    target_id=article_id,
                    action_type='create'
                )
                
                if error:
                    db.session.rollback()
                    return False, f"Failed to create approval request: {error}"
            
            db.session.commit()
            
            # Log article submission activity
            from utils.system_logger import log_article_submitted
            log_article_submitted(article_id, article.title, user_id)
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to submit article: {str(e)}"
    
    @staticmethod
    def approve_article(article_id, approved_by):
        """
        Approve an article
        
        Args:
            article_id (int): Article ID
            approved_by (int): User ID of approver
            
        Returns:
            tuple: (bool, error message or None)
        """
        article = Article.query.get(article_id)
        if not article:
            return False, "Article not found"
        
        if article.status != 'pending':
            return False, "Only pending articles can be approved"
        
        try:
            article.status = 'published'
            article.approved_by = approved_by
            db.session.commit()
            
            # Log article approval activity
            from utils.system_logger import log_article_approved
            log_article_approved(article_id, article.title, approved_by)
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to approve article: {str(e)}"
    
    @staticmethod
    def reject_article(article_id):
        """
        Reject an article
        
        Args:
            article_id (int): Article ID
            
        Returns:
            tuple: (bool, error message or None)
        """
        article = Article.query.get(article_id)
        if not article:
            return False, "Article not found"
        
        if article.status != 'pending':
            return False, "Only pending articles can be rejected"
        
        try:
            article.status = 'draft'
            db.session.commit()
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to reject article: {str(e)}"
    
    @staticmethod
    def get_articles_by_user(user_id):
        """
        Get all articles created by a user
        
        Args:
            user_id (int): User ID
            
        Returns:
            List of Article objects
        """
        return Article.query.filter_by(created_by=user_id).all()
    
    @staticmethod
    def get_articles_by_status(status):
        """
        Get articles by status
        
        Args:
            status (str): Article status
            
        Returns:
            List of Article objects
        """
        return Article.query.filter_by(status=status).all()
    
    @staticmethod
    def get_published_articles():
        """
        Get all published articles
        
        Returns:
            List of Article objects
        """
        return Article.query.filter_by(status='published').all()
    
    @staticmethod
    def get_article_by_id(article_id):
        """
        Get article by ID
        
        Args:
            article_id (int): Article ID
            
        Returns:
            Article object or None
        """
        return Article.query.get(article_id)
    
    @staticmethod
    def save_media_file(file, article_id):
        """
        Save uploaded media file
        
        Args:
            file: Uploaded file object
            article_id (int): Article ID
            
        Returns:
            str: File path or None if failed
        """
        if not file:
            return None
        
        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads')
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        
        # Secure the filename and save the file
        filename = secure_filename(file.filename)
        # Add timestamp to filename to avoid duplicates
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        file_path = os.path.join(uploads_dir, filename)
        file.save(file_path)
        
        # Create media record in database
        relative_path = f"/static/uploads/{filename}"
        media = Media(article_id=article_id, file_path=relative_path)
        db.session.add(media)
        db.session.commit()
        
        return relative_path
    
    @staticmethod
    def get_all_categories():
        """
        Get all categories
        
        Returns:
            List of Category objects
        """
        return Category.query.all()
