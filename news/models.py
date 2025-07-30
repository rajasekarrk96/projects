from config import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Role model
class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    # Relationship
    users = db.relationship('User', backref='role', lazy=True)
    
    def __repr__(self):
        return f'<Role {self.name}>'

# User model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)
    
    # Relationships
    articles = db.relationship('Article', foreign_keys='Article.created_by', backref='author', lazy=True)
    approved_articles = db.relationship('Article', foreign_keys='Article.approved_by', backref='approver', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    approval_requests = db.relationship('ApprovalRequest', foreign_keys='ApprovalRequest.requester_id', backref='requester', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Category model
class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    # Relationship
    articles = db.relationship('Article', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

# Article model
class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    is_anonymous = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='draft')  # draft/published/pending
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    comments = db.relationship('Comment', backref='article', lazy=True, cascade='all, delete-orphan')
    media_files = db.relationship('Media', backref='article', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Article {self.title}>'

# Comment model
class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Comment {self.id}>'

# ApprovalRequest model
class ApprovalRequest(db.Model):
    __tablename__ = 'approval_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_table = db.Column(db.String(50), nullable=False)  # The table name that requires approval
    target_id = db.Column(db.Integer, nullable=False)  # The ID of the record in the target table
    action_type = db.Column(db.String(20), nullable=False)  # create/update/delete
    status = db.Column(db.String(20), default='pending')  # pending/approved/rejected
    
    def __repr__(self):
        return f'<ApprovalRequest {self.id}>'

# Media model
class Media(db.Model):
    __tablename__ = 'media'
    
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return f'<Media {self.id}>'

# System Log model for tracking approval actions
class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    performed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_type = db.Column(db.String(50), nullable=False)  # user, article, comment, etc.
    target_id = db.Column(db.Integer, nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='system_logs', lazy=True)
    
    def __repr__(self):
        return f'<SystemLog {self.id}: {self.action}>'