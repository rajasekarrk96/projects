from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import time
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///proconnect.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

socketio = SocketIO(app)

# Custom Jinja2 filters
@app.template_filter('number_format')
def number_format(value):
    if value is None:
        return ''
    try:
        return "{:,}".format(int(value))
    except (ValueError, TypeError):
        return str(value)

@app.template_filter('currency')
def currency(value, currency_symbol='$'):
    if value is None:
        return ''
    try:
        return f"{currency_symbol}{int(value):,}"
    except (ValueError, TypeError):
        return str(value)

@app.template_filter('truncate')
def truncate(value, length=100, suffix='...'):
    if value is None:
        return ''
    if len(str(value)) <= length:
        return str(value)
    return str(value)[:length] + suffix

@app.template_filter('nl2br')
def nl2br(value):
    if value is None:
        return ''
    return str(value).replace('\n', '<br>')

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.Text)
    profile_picture = db.Column(db.String(200))
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))
    is_company = db.Column(db.Boolean, default=False)
    company_name = db.Column(db.String(100))
    company_description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    skills = db.relationship('UserSkill', backref='user', lazy=True)
    experiences = db.relationship('Experience', backref='user', lazy=True)
    educations = db.relationship('Education', backref='user', lazy=True)
    posts = db.relationship('Post', backref='author', lazy=True)
    connections_sent = db.relationship('Connection', foreign_keys='Connection.sender_id', backref='sender', lazy=True)
    connections_received = db.relationship('Connection', foreign_keys='Connection.receiver_id', backref='receiver', lazy=True)
    job_applications = db.relationship('JobApplication', backref='applicant', lazy=True)
    jobs_posted = db.relationship('Job', backref='company', lazy=True)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class UserSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    skill = db.relationship('Skill', backref='user_skills')

class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    current = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)

class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    institution = db.Column(db.String(100), nullable=False)
    degree = db.Column(db.String(100), nullable=False)
    field_of_study = db.Column(db.String(100))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    current = db.Column(db.Boolean, default=False)

class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.relationship('PostLike', backref='post', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')

class PostLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='comments')

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    location = db.Column(db.String(100))
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    job_type = db.Column(db.String(50))  # full-time, part-time, internship, freelance
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    applications = db.relationship('JobApplication', backref='job', lazy=True)

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cover_letter = db.Column(db.Text)
    resume_url = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            first_name=data['first_name'],
            last_name=data['last_name'],
            is_company=data.get('is_company') == 'on'
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get current user's accepted connections
    accepted_connections = Connection.query.filter(
        ((Connection.sender_id == current_user.id) | (Connection.receiver_id == current_user.id)) &
        (Connection.status == 'accepted')
    ).all()
    
    # Get connected user IDs
    connected_user_ids = []
    for connection in accepted_connections:
        if connection.sender_id == current_user.id:
            connected_user_ids.append(connection.receiver_id)
        else:
            connected_user_ids.append(connection.sender_id)
    
    # Add current user's ID to show their own posts too
    connected_user_ids.append(current_user.id)
    
    # Get posts from connected users and current user
    posts = Post.query.filter(Post.author_id.in_(connected_user_ids)).order_by(Post.created_at.desc()).limit(10).all()
    
    # If no connections, show all posts (for new users)
    if not connected_user_ids or len(connected_user_ids) == 1:
        posts = Post.query.order_by(Post.created_at.desc()).limit(10).all()
    
    # Get current user's stats
    user_posts_count = Post.query.filter_by(author_id=current_user.id).count()
    connections_count = len(connected_user_ids) - 1  # Subtract 1 for current user
    
    return render_template('dashboard.html', 
                         posts=posts, 
                         connections=connections_count,
                         user_posts_count=user_posts_count)

@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.first_name = request.form['first_name']
        current_user.last_name = request.form['last_name']
        current_user.bio = request.form['bio']
        current_user.location = request.form['location']
        current_user.website = request.form['website']
        
        if current_user.is_company:
            current_user.company_name = request.form.get('company_name')
            current_user.company_description = request.form.get('company_description')
        
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                current_user.profile_picture = filename
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile', username=current_user.username))
    
    return render_template('edit_profile.html')

@app.route('/connect/<int:user_id>', methods=['POST'])
@login_required
def send_connection_request(user_id):
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot connect with yourself'}), 400
    
    existing_connection = Connection.query.filter(
        ((Connection.sender_id == current_user.id) & (Connection.receiver_id == user_id)) |
        ((Connection.sender_id == user_id) & (Connection.receiver_id == current_user.id))
    ).first()
    
    if existing_connection:
        return jsonify({'error': 'Connection request already exists'}), 400
    
    connection = Connection(sender_id=current_user.id, receiver_id=user_id)
    db.session.add(connection)
    db.session.commit()
    
    return jsonify({'message': 'Connection request sent successfully'})

@app.route('/connections/<int:request_id>/accept', methods=['POST'])
@login_required
def accept_connection_request(request_id):
    connection = Connection.query.get_or_404(request_id)
    
    if connection.receiver_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    connection.status = 'accepted'
    db.session.commit()
    
    return jsonify({'message': 'Connection request accepted'})

@app.route('/connections/<int:request_id>/reject', methods=['POST'])
@login_required
def reject_connection_request(request_id):
    connection = Connection.query.get_or_404(request_id)
    
    if connection.receiver_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    connection.status = 'rejected'
    db.session.commit()
    
    return jsonify({'message': 'Connection request rejected'})

@app.route('/connections')
@login_required
def connections():
    pending_requests = Connection.query.filter_by(receiver_id=current_user.id, status='pending').all()
    accepted_connections = Connection.query.filter(
        ((Connection.sender_id == current_user.id) | (Connection.receiver_id == current_user.id)) &
        (Connection.status == 'accepted')
    ).all()
    
    return render_template('connections.html', 
                         pending_requests=pending_requests, 
                         accepted_connections=accepted_connections)

@app.route('/post', methods=['POST'])
@login_required
def create_post():
    content = request.form.get('content')
    if not content:
        return jsonify({'error': 'Post content is required'}), 400
    
    post = Post(author_id=current_user.id, content=content)
    
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            if '.' in file.filename:
                file_ext = file.filename.rsplit('.', 1)[1].lower()
                if file_ext in allowed_extensions:
                    filename = secure_filename(file.filename)
                    # Add timestamp to avoid filename conflicts
                    timestamp = int(time.time())
                    name, ext = filename.rsplit('.', 1)
                    filename = f"{name}_{timestamp}.{ext}"
                    
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    post.image_url = filename
                else:
                    return jsonify({'error': 'Invalid file type. Please upload PNG, JPG, JPEG, GIF, or WebP images.'}), 400
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify({'message': 'Post created successfully', 'post_id': post.id})

@app.route('/test')
def test():
    return jsonify({'message': 'Test route working'})

@app.route('/post/<int:post_id>/edit', methods=['POST'])
@login_required
def edit_post(post_id):
    print(f"Edit post called for post_id: {post_id}")
    print(f"Current user: {current_user.id}")
    
    post = Post.query.get_or_404(post_id)
    print(f"Post author_id: {post.author_id}")
    
    # Check if the current user is the author of the post
    if post.author_id != current_user.id:
        print("Unauthorized edit attempt")
        return jsonify({'error': 'You can only edit your own posts'}), 403
    
    content = request.form.get('content')
    print(f"Content received: {content}")
    if not content:
        print("No content provided")
        return jsonify({'error': 'Post content is required'}), 400
    
    # Update post content
    post.content = content
    
    # Handle image update if provided
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            print(f"Image file received: {file.filename}")
            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            if '.' in file.filename:
                file_ext = file.filename.rsplit('.', 1)[1].lower()
                if file_ext in allowed_extensions:
                    filename = secure_filename(file.filename)
                    # Add timestamp to avoid filename conflicts
                    timestamp = int(time.time())
                    name, ext = filename.rsplit('.', 1)
                    filename = f"{name}_{timestamp}.{ext}"
                    
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    post.image_url = filename
                    print(f"Image saved as: {filename}")
                else:
                    print(f"Invalid file type: {file_ext}")
                    return jsonify({'error': 'Invalid file type. Please upload PNG, JPG, JPEG, GIF, or WebP images.'}), 400
    
    db.session.commit()
    print("Post updated successfully")
    
    return jsonify({
        'message': 'Post updated successfully',
        'content': post.content,
        'image_url': post.image_url
    })

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    print(f"Delete post called for post_id: {post_id}")
    print(f"Current user: {current_user.id}")
    
    try:
        post = Post.query.get_or_404(post_id)
        print(f"Post author_id: {post.author_id}")
        
        # Check if the current user is the author of the post
        if post.author_id != current_user.id:
            print("Unauthorized delete attempt")
            return jsonify({'error': 'You can only delete your own posts'}), 403
        
        # Delete the post (cascade will handle likes and comments)
        db.session.delete(post)
        db.session.commit()
        print("Post deleted successfully")
        
        return jsonify({'message': 'Post deleted successfully'})
        
    except Exception as e:
        print(f"Error deleting post: {e}")
        db.session.rollback()
        return jsonify({'error': f'Error deleting post: {str(e)}'}), 500

@app.route('/jobs')
def jobs():
    jobs_list = Job.query.order_by(Job.created_at.desc()).all()
    return render_template('jobs.html', jobs=jobs_list)

@app.route('/jobs/post', methods=['GET', 'POST'])
@login_required
def post_job():
    if not current_user.is_company:
        flash('Only companies can post jobs', 'error')
        return redirect(url_for('jobs'))
    
    if request.method == 'POST':
        job = Job(
            company_id=current_user.id,
            title=request.form['title'],
            description=request.form['description'],
            requirements=request.form['requirements'],
            location=request.form['location'],
            salary_min=request.form.get('salary_min'),
            salary_max=request.form.get('salary_max'),
            job_type=request.form['job_type']
        )
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('jobs'))
    
    return render_template('post_job.html')

@app.route('/jobs/<int:job_id>/apply', methods=['POST'])
@login_required
def apply_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    existing_application = JobApplication.query.filter_by(
        job_id=job_id, applicant_id=current_user.id
    ).first()
    
    if existing_application:
        return jsonify({'error': 'You have already applied for this job'}), 400
    
    application = JobApplication(
        job_id=job_id,
        applicant_id=current_user.id,
        cover_letter=request.form.get('cover_letter')
    )
    
    if 'resume' in request.files:
        file = request.files['resume']
        if file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            application.resume_url = filename
    
    db.session.add(application)
    db.session.commit()
    
    return jsonify({'message': 'Application submitted successfully'})

@app.route('/company/applications')
@login_required
def company_applications():
    if not current_user.is_company:
        flash('Only companies can access this page', 'error')
        return redirect(url_for('dashboard'))
    
    # Get all jobs posted by the company
    company_jobs = Job.query.filter_by(company_id=current_user.id).all()
    job_ids = [job.id for job in company_jobs]
    
    # Get all applications for company's jobs
    applications = JobApplication.query.filter(JobApplication.job_id.in_(job_ids)).order_by(JobApplication.applied_at.desc()).all()
    
    # Group applications by job
    applications_by_job = {}
    for job in company_jobs:
        applications_by_job[job] = [app for app in applications if app.job_id == job.id]
    
    return render_template('company_applications.html', 
                         applications_by_job=applications_by_job,
                         total_applications=len(applications))

@app.route('/company/applications/<int:job_id>')
@login_required
def job_applications(job_id):
    if not current_user.is_company:
        flash('Only companies can access this page', 'error')
        return redirect(url_for('dashboard'))
    
    job = Job.query.get_or_404(job_id)
    
    # Check if the job belongs to the current company
    if job.company_id != current_user.id:
        flash('You can only view applications for your own jobs', 'error')
        return redirect(url_for('company_applications'))
    
    applications = JobApplication.query.filter_by(job_id=job_id).order_by(JobApplication.applied_at.desc()).all()
    
    return render_template('job_applications.html', 
                         job=job,
                         applications=applications)

@app.route('/company/applications/<int:application_id>/status', methods=['POST'])
@login_required
def update_application_status(application_id):
    if not current_user.is_company:
        return jsonify({'error': 'Unauthorized'}), 403
    
    application = JobApplication.query.get_or_404(application_id)
    job = Job.query.get_or_404(application.job_id)
    
    # Check if the job belongs to the current company
    if job.company_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    status = request.form.get('status')
    if status not in ['pending', 'accepted', 'rejected']:
        return jsonify({'error': 'Invalid status'}), 400
    
    application.status = status
    db.session.commit()
    
    return jsonify({'message': f'Application {status} successfully'})

@app.route('/company/applications/<int:application_id>/view')
@login_required
def view_application(application_id):
    if not current_user.is_company:
        flash('Only companies can access this page', 'error')
        return redirect(url_for('dashboard'))
    
    application = JobApplication.query.get_or_404(application_id)
    job = Job.query.get_or_404(application.job_id)
    
    # Check if the job belongs to the current company
    if job.company_id != current_user.id:
        flash('You can only view applications for your own jobs', 'error')
        return redirect(url_for('company_applications'))
    
    return render_template('view_application.html', 
                         application=application,
                         job=job)

# API Routes for AJAX
@app.route('/api/like_post/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    existing_like = PostLike.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        return jsonify({'liked': False})
    else:
        like = PostLike(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
        return jsonify({'liked': True})

@app.route('/api/comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    content = request.json.get('content')
    if not content:
        return jsonify({'error': 'Comment content is required'}), 400
    
    comment = Comment(user_id=current_user.id, post_id=post_id, content=content)
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'id': comment.id,
        'content': comment.content,
        'user_name': f"{comment.user.first_name} {comment.user.last_name}",
        'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
    })

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join')
def handle_join(data):
    room = data['room']
    join_room(room)
    emit('status', {'msg': f'User joined room: {room}'}, room=room)

@socketio.on('leave')
def handle_leave(data):
    room = data['room']
    leave_room(room)
    emit('status', {'msg': f'User left room: {room}'}, room=room)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True) 