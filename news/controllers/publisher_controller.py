"""
Publisher Controller
Handles routing for publisher-related pages
"""

from flask import Blueprint, request
from pages.publisher_page import (
    PublisherDashboardPage, 
    CreateArticlePage, 
    EditArticlePage, 
    ArticleActionsPage
)
from utils.decorators import role_required

# Create Blueprint
publisher_controller = Blueprint('publisher', __name__, url_prefix='/publisher')


@publisher_controller.route('/dashboard')
@role_required(['publisher'])
def dashboard():
    """Handle publisher dashboard"""
    dashboard_page = PublisherDashboardPage()
    return dashboard_page.render_dashboard()


@publisher_controller.route('/create', methods=['GET', 'POST'])
@role_required(['publisher'])
def create_article():
    """Handle article creation"""
    create_page = CreateArticlePage()
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category_id = request.form.get('category_id')
        is_anonymous = 'is_anonymous' in request.form
        media_file = request.files.get('media_file')
        
        success, redirect_url, error = create_page.process_create_article(
            title, content, category_id, is_anonymous, media_file
        )
        
        if success:
            return create_page.redirect_to(redirect_url)
        
        # If creation failed, render form again with error
        return create_page.render_create_form()
    
    # GET request - render creation form
    return create_page.render_create_form()


@publisher_controller.route('/edit/<int:id>', methods=['GET', 'POST'])
@role_required(['publisher'])
def edit_article(id):
    """Handle article editing"""
    edit_page = EditArticlePage()
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category_id = request.form.get('category_id')
        is_anonymous = 'is_anonymous' in request.form
        
        success, redirect_url, error = edit_page.process_edit_article(
            id, title, content, category_id, is_anonymous
        )
        
        if success:
            return edit_page.redirect_to(redirect_url)
        
        # If edit failed, render form again with error
        return edit_page.render_edit_form(id)
    
    # GET request - render edit form
    return edit_page.render_edit_form(id)


@publisher_controller.route('/delete/<int:id>')
@role_required(['publisher'])
def delete_article(id):
    """Handle article deletion"""
    actions_page = ArticleActionsPage()
    success, redirect_url, error = actions_page.process_delete_article(id)
    return actions_page.redirect_to(redirect_url)


@publisher_controller.route('/submit/<int:id>')
@role_required(['publisher'])
def submit_article(id):
    """Handle article submission for approval"""
    actions_page = ArticleActionsPage()
    success, redirect_url, error = actions_page.process_submit_article(id)
    return actions_page.redirect_to(redirect_url)
