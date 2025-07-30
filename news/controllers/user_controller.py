"""
User Controller
Handles routing for user-related pages
"""

from flask import Blueprint, request
from pages.user_page import UserDashboardPage, ArticleViewPage, CommentPage
from utils.decorators import role_required, login_required

# Create Blueprint
user_controller = Blueprint('user', __name__, url_prefix='/user')


@user_controller.route('/')
@user_controller.route('/home')
@login_required
def home():
    """Handle user home page (redirects to dashboard)"""
    dashboard_page = UserDashboardPage()
    return dashboard_page.render_dashboard()


@user_controller.route('/dashboard')
@role_required(['user', 'publisher', 'admin', 'superadmin'])
def dashboard():
    """Handle user dashboard"""
    dashboard_page = UserDashboardPage()
    return dashboard_page.render_dashboard()


@user_controller.route('/article/<int:id>')
@login_required
def article(id):
    """Handle viewing individual articles"""
    article_page = ArticleViewPage()
    return article_page.render_article(id)


@user_controller.route('/comment/<int:article_id>', methods=['POST'])
@login_required
def add_comment(article_id):
    """Handle adding comments to articles"""
    comment_page = CommentPage()
    content = request.form.get('content')
    
    success, redirect_url, error = comment_page.process_add_comment(article_id, content)
    return comment_page.redirect_to(redirect_url, id=article_id)


@user_controller.route('/edit-comment/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_comment(id):
    """Handle editing comments"""
    # For now, redirect to article view
    from flask import redirect, url_for
    return redirect(url_for('user.home'))


@user_controller.route('/delete-comment/<int:id>')
@login_required
def delete_comment(id):
    """Handle deleting comments"""
    # For now, redirect to article view
    from flask import redirect, url_for
    return redirect(url_for('user.home'))


@user_controller.route('/like-article/<int:id>')
@login_required
def like_article(id):
    """Handle liking articles"""
    # For now, redirect back to article
    from flask import redirect, url_for
    return redirect(url_for('user.article', id=id))


@user_controller.route('/share-article/<int:id>')
@login_required
def share_article(id):
    """Handle sharing articles"""
    # For now, redirect back to article
    from flask import redirect, url_for
    return redirect(url_for('user.article', id=id))
