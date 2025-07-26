from flask import Flask, request, redirect, url_for, session, flash, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workout_sphere.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    profile_image = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    duration = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    date = db.Column(db.Date, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    feed_posts = db.relationship('FeedPost', backref='workout_post', lazy='dynamic')
    exercises = db.relationship('Exercise', backref='workout', lazy='dynamic', cascade='all, delete-orphan')

class Routine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_duration = db.Column(db.Integer, default=0)
    frequency = db.Column(db.String(50), default='Daily')
    workouts = db.relationship('Workout', secondary='routine_workouts', backref='routines')

class RoutineWorkouts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    routine_id = db.Column(db.Integer, db.ForeignKey('routine.id'), nullable=False)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False)

class FeedPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False)
    likes = db.Column(db.Integer, default=0)
    liked_by = db.relationship('User', secondary='post_likes', backref='liked_posts')
    
    user = db.relationship('User', backref='posts')
    workout = db.relationship('Workout', backref='posts')
    comments = db.relationship('FeedComment', backref='post', lazy='dynamic', cascade='all, delete-orphan')

post_likes = db.Table('post_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('feed_post.id'), primary_key=True)
)

class FeedComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('feed_post.id'), nullable=False)
    
    user = db.relationship('User', backref='comments')

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def volume(self):
        return self.sets * self.reps * (self.weight or 0)

@app.route('/api/feed/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    if 'user_id' not in session:
        return {'success': False, 'error': 'Not logged in'}, 401
    
    user = User.query.get(session['user_id'])
    post = FeedPost.query.get_or_404(post_id)
    
    if user in post.liked_by:
        post.liked_by.remove(user)
    else:
        post.liked_by.append(user)
    
    db.session.commit()
    return {'success': True, 'likes': len(post.liked_by)}

@app.route('/api/feed/<int:post_id>/comments', methods=['GET', 'POST'])
def post_comments(post_id):
    if 'user_id' not in session:
        return {'success': False, 'error': 'Not logged in'}, 401
    
    if request.method == 'POST':
        content = request.json.get('content')
        if not content:
            return {'success': False, 'error': 'Content is required'}, 400
        
        new_comment = FeedComment(
            content=content,
            user_id=session['user_id'],
            post_id=post_id
        )
        db.session.add(new_comment)
        db.session.commit()
        return {'success': True, 'comment': {
            'id': new_comment.id,
            'content': new_comment.content,
            'created_at': new_comment.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'user': {
                'name': new_comment.user.name,
                'profile_image': new_comment.user.profile_image
            }
        }}
    else:
        comments = FeedComment.query.filter_by(post_id=post_id).order_by(FeedComment.created_at.desc()).all()
        return {'success': True, 'comments': [{
            'id': c.id,
            'content': c.content,
            'created_at': c.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'user': {
                'name': c.user.name,
                'profile_image': c.user.profile_image
            }
        } for c in comments]}

@app.route('/api/feed/<int:post_id>/edit', methods=['POST'])
def edit_post(post_id):
    if 'user_id' not in session:
        return {'success': False, 'error': 'Not logged in'}, 401
    
    post = FeedPost.query.get_or_404(post_id)
    if post.user_id != session['user_id']:
        return {'success': False, 'error': 'Unauthorized'}, 403
    
    content = request.json.get('content')
    if not content:
        return {'success': False, 'error': 'Content is required'}, 400
    
    post.content = content
    db.session.commit()
    return {'success': True}

@app.route('/api/feed/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    if 'user_id' not in session:
        return {'success': False, 'error': 'Not logged in'}, 401
    
    post = FeedPost.query.get_or_404(post_id)
    if post.user_id != session['user_id']:
        return {'success': False, 'error': 'Unauthorized'}, 403
    
    db.session.delete(post)
    db.session.commit()
    return {'success': True}

@app.route('/workout/<int:workout_id>')
def workout_detail(workout_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
        
    workout = Workout.query.get_or_404(workout_id)
    if workout.user_id != session['user_id']:
        return redirect(url_for('workouts'))
        
    return render_template('workout-detail.html', 
        workout=workout,
        current_user=User.query.get(session['user_id'])
    )

@app.route('/routine/<int:routine_id>')
def routine_detail(routine_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
        
    routine = Routine.query.get_or_404(routine_id)
    if routine.user_id != session['user_id']:
        return redirect(url_for('routines'))
        
    return render_template('routine-detail.html', 
        routine=routine,
        current_user=User.query.get(session['user_id'])
    )

@app.route('/')
def index():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return render_template('index.html', current_user=user)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('index'))
    
    return render_template('profile.html', user=user, current_user=user)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('index'))
    
    user.name = request.form.get('name')
    user.email = request.form.get('email')
    user.bio = request.form.get('bio')
    
    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file and file.filename:
            # Ensure filename is secure
            filename = secure_filename(file.filename)
            # Create unique filename
            unique_filename = f"{user.id}_{int(datetime.utcnow().timestamp())}_{filename}"
            # Save file
            file.save(os.path.join(app.root_path, 'static', 'uploads', unique_filename))
            # Update database
            user.profile_image = url_for('static', filename=f'uploads/{unique_filename}')
    
    db.session.commit()
    flash('Profile updated successfully!')
    return redirect(url_for('profile'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Successfully logged in!')
            return redirect(url_for('dashboard'))
        
        flash('Invalid email or password')
        return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([name, email, password, confirm_password]):
            flash('All fields are required')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('index'))
    
    # Get workout statistics
    total_workouts = Workout.query.filter_by(user_id=user.id).count()
    total_duration = db.session.query(db.func.sum(Workout.duration)).filter_by(user_id=user.id).scalar() or 0
    total_routines = Routine.query.filter_by(user_id=user.id).count()
    recent_workouts = Workout.query.filter_by(user_id=user.id).order_by(Workout.created_at.desc()).limit(3).all()
    routines_list = Routine.query.filter_by(user_id=user.id).all()
    
    return render_template('dashboard.html', 
        user=user,
        total_workouts=total_workouts,
        total_duration=total_duration,
        total_routines=total_routines,
        recent_workouts=recent_workouts,
        routines_list=routines_list,
        workout=recent_workouts[0] if recent_workouts else None
    )

@app.route('/workouts')
def workouts():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('index'))
    
    # Get all workouts for the current user
    user_workouts = Workout.query.filter_by(user_id=user.id).order_by(Workout.date.desc()).all()
    
    # Get all exercises for these workouts
    workout_ids = [workout.id for workout in user_workouts]
    exercises = Exercise.query.filter(Exercise.workout_id.in_(workout_ids)).all()
    
    # Create a dictionary to store exercises by workout
    exercises_by_workout = {}
    for exercise in exercises:
        if exercise.workout_id not in exercises_by_workout:
            exercises_by_workout[exercise.workout_id] = []
        exercises_by_workout[exercise.workout_id].append(exercise)
    
    # Calculate total volume for each workout
    workout_volumes = {}
    for workout in user_workouts:
        total_volume = sum(exercise.volume for exercise in exercises_by_workout.get(workout.id, []))
        workout_volumes[workout.id] = total_volume
    
    return render_template('workouts.html', 
                         user=user,
                         workouts=user_workouts,
                         exercises_by_workout=exercises_by_workout,
                         workout_volumes=workout_volumes)

@app.route('/add_workout', methods=['GET', 'POST'])
def add_workout():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        duration = request.form.get('duration')
        
        if not all([title, duration]):
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('add_workout'))
        
        # Automatically set today's date
        today = datetime.now().date()
        
        workout = Workout(
            title=title,
            description=description,
            duration=duration,
            date=today,
            user_id=user.id
        )
        db.session.add(workout)
        db.session.flush()  # Get the workout ID
        
        # Process exercises
        exercises = request.form.getlist('exercises')
        for i in range(0, len(exercises), 4):
            if i + 3 < len(exercises):
                name = exercises[i]
                sets = exercises[i + 1]
                reps = exercises[i + 2]
                weight = exercises[i + 3]
                
                if not weight or float(weight) <= 0:
                    flash('Please enter a valid weight greater than 0 for all exercises', 'error')
                    db.session.rollback()
                    return redirect(url_for('add_workout'))
                
                exercise = Exercise(
                    name=name,
                    sets=sets,
                    reps=reps,
                    weight=weight,
                    workout_id=workout.id
                )
                db.session.add(exercise)
        
        db.session.commit()
        flash('Workout added successfully!', 'success')
        return redirect(url_for('workouts'))
    
    return render_template('add-workout.html')

@app.route('/workout_progress')
def workout_progress():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('index'))
    
    # Get the current (most recent) and previous workouts
    workouts = Workout.query.filter_by(user_id=user.id).order_by(Workout.created_at.desc()).limit(2).all()
    
    current_workout = workouts[0] if workouts else None
    previous_workout = workouts[1] if len(workouts) > 1 else None
    
    # Calculate total volume for each workout
    current_volume = sum(exercise.volume for exercise in current_workout.exercises) if current_workout else 0
    previous_volume = sum(exercise.volume for exercise in previous_workout.exercises) if previous_workout else 0
    
    return render_template('workout-progress.html',
        user=user,
        current_workout=current_workout,
        previous_workout=previous_workout,
        current_volume=current_volume,
        previous_volume=previous_volume
    )

@app.route('/routines')
def routines():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('index'))
    
    workouts = Workout.query.filter_by(user_id=user.id).all()
    routines = Routine.query.filter_by(user_id=user.id).all()
    return render_template('routines.html', user=user, workouts=workouts, routines=routines)

@app.route('/add-routine', methods=['GET', 'POST'])
def add_routine():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('index'))
    
    workouts = Workout.query.filter_by(user_id=user.id).all()
    
    if request.method == 'POST':
        name = request.form.get('routine_name')
        description = request.form.get('routine_description')
        frequency = request.form.get('frequency', 'Daily')
        workout_ids = request.form.getlist('workouts')
        
        if not name:
            flash('Routine name is required')
            return redirect(url_for('add_routine'))
            
        if len(workout_ids) < 2:
            flash('Please select at least 2 workouts')
            return redirect(url_for('add_routine'))
            
        try:
            new_routine = Routine(
                name=name,
                description=description,
                frequency=frequency,
                user_id=user.id
            )
            db.session.add(new_routine)
            db.session.commit()
            
            for workout_id in workout_ids:
                routine_workout = RoutineWorkouts(
                    routine_id=new_routine.id,
                    workout_id=workout_id
                )
                db.session.add(routine_workout)
            
            db.session.commit()
            flash('Routine created successfully!')
            return redirect(url_for('routines'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.')
            return redirect(url_for('add_routine'))
    
    return render_template('add-routine.html', user=user, workouts=workouts)

@app.route('/feed')
def feed():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('index'))
    
    workouts = Workout.query.filter_by(user_id=user.id).all()
    posts = FeedPost.query.order_by(FeedPost.created_at.desc()).all()
    popular_workouts = Workout.query.join(FeedPost).group_by(Workout).order_by(db.func.count(FeedPost.id).desc()).limit(5).all()
    return render_template('feed.html', user=user, current_user=user, user_workouts=workouts, posts=posts)

@app.route('/create_feed_post', methods=['POST'])
def create_feed_post():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('index'))
    
    workout_id = request.form.get('workout_id')
    description = request.form.get('description')
    
    if not workout_id:
        flash('Please select a workout')
        return redirect(url_for('feed'))
        
    if not description or not description.strip():
        flash('Post description cannot be empty')
        return redirect(url_for('feed'))
    

    
    new_post = FeedPost(
        content=description,
        user_id=user.id,
        workout_id=workout_id
    )
    
    if 'post_image' in request.files:
        file = request.files['post_image']
        if file and file.filename:
            filename = secure_filename(file.filename)
            unique_filename = f"post_{new_post.id}_{int(datetime.utcnow().timestamp())}_{filename}"
            file.save(os.path.join(app.root_path, 'static', 'uploads', unique_filename))
            new_post.post_image = unique_filename
    
    db.session.add(new_post)
    db.session.commit()
    
    flash('Post created successfully!')
    return redirect(url_for('feed'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([current_password, new_password, confirm_password]):
            flash('All fields are required')
            return redirect(url_for('change_password'))
            
        if not check_password_hash(user.password, current_password):
            flash('Current password is incorrect')
            return redirect(url_for('change_password'))
            
        if new_password != confirm_password:
            flash('New passwords do not match')
            return redirect(url_for('change_password'))
            
        user.password = generate_password_hash(new_password)
        db.session.commit()
        flash('Password changed successfully!')
        return redirect(url_for('profile'))
    
    return render_template('change-password.html', user=user)

@app.route('/edit_workout/<int:workout_id>', methods=['GET', 'POST'])
def edit_workout(workout_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('index'))
    
    workout = Workout.query.get_or_404(workout_id)
    if workout.user_id != user.id:
        flash('You do not have permission to edit this workout')
        return redirect(url_for('workouts'))
    
    if request.method == 'POST':
        workout.title = request.form.get('title')
        workout.description = request.form.get('description')
        workout.duration = request.form.get('duration')
        
        if not all([workout.title, workout.duration]):
            flash('Title and duration are required')
            return redirect(url_for('edit_workout', workout_id=workout_id))
        
        try:
            # Delete existing exercises
            Exercise.query.filter_by(workout_id=workout.id).delete()
            
            # Add new exercises
            exercises = request.form.getlist('exercises')
            for i in range(0, len(exercises), 4):
                if i + 3 < len(exercises):
                    exercise = Exercise(
                        name=exercises[i],
                        sets=int(exercises[i + 1]),
                        reps=int(exercises[i + 2]),
                        weight=float(exercises[i + 3]) if exercises[i + 3] else None,
                        workout_id=workout.id
                    )
                    db.session.add(exercise)
            
            db.session.commit()
            flash('Workout updated successfully!')
            return redirect(url_for('workouts'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.')
            return redirect(url_for('edit_workout', workout_id=workout_id))
    
    return render_template('edit-workout.html', user=user, workout=workout)

@app.route('/delete_workout/<int:workout_id>', methods=['GET'])
def delete_workout(workout_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('index'))
    
    workout = Workout.query.get_or_404(workout_id)
    if workout.user_id != user.id:
        flash('You do not have permission to delete this workout')
        return redirect(url_for('workouts'))
    
    try:
        # Delete associated exercises first
        Exercise.query.filter_by(workout_id=workout.id).delete()
        
        # Delete associated feed posts
        FeedPost.query.filter_by(workout_id=workout.id).delete()
        
        # Delete the workout
        db.session.delete(workout)
        db.session.commit()
        flash('Workout deleted successfully!')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the workout')
        print(f"Error deleting workout: {str(e)}")  # For debugging
    
    return redirect(url_for('workouts'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)