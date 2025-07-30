# Flask News Portal with SQLite3 and SQLAlchemy

This is a role-based Flask news portal application using SQLAlchemy with SQLite3 database. The application includes user management, article publishing, commenting, and approval workflows.

## Database Models

The application includes the following database models:

1. **Users**: Manages user accounts with role-based permissions
   - Fields: id, username, email, password (hashed), role, is_active, is_approved

2. **Roles**: Defines user roles and permissions
   - Fields: id, name

3. **Articles**: Stores news articles
   - Fields: id, title, content, category_id, is_anonymous, status (draft/published/pending), created_by, approved_by, created_at

4. **Comments**: Stores user comments on articles
   - Fields: id, user_id, article_id, content, created_at

5. **Categories**: Organizes articles by topic
   - Fields: id, name

6. **Approval Requests**: Manages content approval workflow
   - Fields: id, requester_id, target_table, target_id, action_type, status

7. **Media**: Stores media files associated with articles
   - Fields: id, article_id, file_path

## Project Structure

```
/news
├── app.py              # Main Flask application
├── config.py           # Database and app configuration
├── models.py           # SQLAlchemy models
├── init_db.py          # Database initialization script
└── news_portal.db      # SQLite database (created on first run)
```

## Setup Instructions

### Prerequisites

- Python 3.6 or higher
- pip (Python package manager)

### Installation

1. Clone the repository or download the source code

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. Install required packages:
   ```
   pip install flask flask-sqlalchemy werkzeug
   ```

4. Initialize the database:
   ```
   python init_db.py
   ```

5. Run the application:
   ```
   python app.py
   ```

6. Access the application at http://127.0.0.1:5000/

## Default Credentials

After initializing the database, you can log in with the following admin credentials:

- Username: admin
- Password: admin123

## Database Schema

The database schema includes proper relationships between tables:

- Users belong to Roles (many-to-one)
- Articles belong to Categories (many-to-one)
- Articles are created by Users (many-to-one)
- Comments belong to Users and Articles (many-to-one)
- Media files belong to Articles (many-to-one)
- Approval requests are created by Users (many-to-one)

## Features

- Role-based access control
- Article publishing workflow with approval process
- User comments on articles
- Media file management for articles
- Content categorization