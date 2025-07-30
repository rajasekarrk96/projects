from config import db, app
from models import Role, User, Category, Article, Comment, ApprovalRequest, Media
from werkzeug.security import generate_password_hash

def init_db():
    # Create all tables
    db.create_all()
    
    # Check if we already have data
    if Role.query.count() == 0:
        # Create roles
        superadmin_role = Role(name='superadmin')
        admin_role = Role(name='admin')
        publisher_role = Role(name='publisher')
        user_role = Role(name='user')
        
        db.session.add_all([superadmin_role, admin_role, publisher_role, user_role])
        db.session.commit()
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            role_id=1,  # admin role
            is_active=True,
            is_approved=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create default categories
        categories = [
            Category(name='Politics'),
            Category(name='Technology'),
            Category(name='Sports'),
            Category(name='Entertainment'),
            Category(name='Science')
        ]
        db.session.add_all(categories)
        db.session.commit()
        
        print('Database initialized with default data!')
    else:
        print('Database already contains data!')

if __name__ == '__main__':
    with app.app_context():
        init_db()