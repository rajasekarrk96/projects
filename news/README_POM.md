# Flask News Portal - Page Object Model (POM) Version

This is a **refactored version** of the Flask News Portal that follows the **Page Object Model (POM)** design pattern for improved code organization, maintainability, and testability.

## 🏗️ Architecture Overview

The application has been restructured into four main layers:

- **📄 Pages Layer** (`/pages/`) - UI logic and page-specific operations
- **⚙️ Services Layer** (`/services/`) - Business logic and data operations  
- **🎮 Controllers Layer** (`/controllers/`) - HTTP routing and request handling
- **🔧 Utils Layer** (`/utils/`) - Common utilities and helper functions

## 📁 Project Structure

```
/news (POM Version)
├── app.py                  # Main Flask application (POM version)
├── config.py               # Database and app configuration
├── models.py               # SQLAlchemy models
├── init_db.py              # Database initialization script
├── approval.py             # Approval workflow logic
├── news_portal.db          # SQLite database
├── requirements.txt        # Python dependencies
├── POM_ARCHITECTURE.md     # Detailed POM documentation
├── README_POM.md           # This file
├── README.md               # Original README
│
├── pages/                  # 📄 Page Objects Layer
│   ├── __init__.py
│   ├── base_page.py        # Abstract base page class
│   ├── auth_page.py        # Authentication pages
│   ├── publisher_page.py   # Publisher pages
│   ├── admin_page.py       # Admin pages
│   ├── user_page.py        # User pages
│   └── superadmin_page.py  # SuperAdmin pages
│
├── services/               # ⚙️ Services Layer
│   ├── __init__.py
│   ├── auth_service.py     # Authentication business logic
│   ├── article_service.py  # Article management logic
│   └── user_service.py     # User management logic
│
├── controllers/            # 🎮 Controllers Layer
│   ├── __init__.py
│   ├── auth_controller.py      # Authentication routes
│   ├── publisher_controller.py # Publisher routes
│   ├── admin_controller.py     # Admin routes
│   ├── user_controller.py      # User routes
│   └── superadmin_controller.py # SuperAdmin routes
│
├── utils/                  # 🔧 Utils Layer
│   ├── __init__.py
│   ├── decorators.py       # Custom decorators
│   └── helpers.py          # Utility functions
│
├── static/                 # Static files (CSS, JS, images)
└── templates/              # Jinja2 templates
    ├── auth/
    ├── publisher/
    ├── admin/
    ├── user/
    └── superadmin/
```

## 🚀 Quick Start

### Prerequisites

- Python 3.6 or higher
- pip (Python package manager)

### Installation & Setup

1. **Navigate to the project directory:**
   ```bash
   cd /path/to/news
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install required packages:**
   ```bash
   pip install flask flask-sqlalchemy werkzeug
   ```

4. **Initialize the database:**
   ```bash
   python init_db.py
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Access the application:**
   Open your browser and go to `http://127.0.0.1:5000/`

## 🔐 Default Credentials

After initializing the database, you can log in with:

- **Username:** admin
- **Password:** admin123

## ✨ Key Features

### 🎯 POM Benefits

- **Separation of Concerns** - Clear separation between UI, business logic, and data access
- **Improved Maintainability** - Changes are isolated to specific layers
- **Enhanced Testability** - Each layer can be tested independently
- **Code Reusability** - Services and utilities can be reused across controllers
- **Better Organization** - Logical file structure and naming conventions

### 🔄 Application Features

- **Role-based Access Control** - User, Publisher, Admin, SuperAdmin roles
- **Article Publishing Workflow** - Draft → Pending → Published/Rejected
- **User Management** - Registration, approval, activation/deactivation
- **Media File Management** - Upload and manage article attachments
- **Approval System** - Centralized approval workflow for various actions
- **Content Categorization** - Organize articles by categories
- **Commenting System** - Users can comment on published articles

## 🎭 User Roles & Permissions

| Role | Permissions |
|------|-------------|
| **User** | View published articles, add comments |
| **Publisher** | Create, edit, submit articles for approval |
| **Admin** | Approve/reject articles, manage users and publishers |
| **SuperAdmin** | Full system access, process approval requests, manage all users |

## 🔧 Development

### Adding New Features

1. **Create Service** - Add business logic in `/services/`
2. **Create Page Object** - Add UI logic in `/pages/`
3. **Create Controller** - Add routes in `/controllers/`
4. **Register Blueprint** - Import and register in `app_pom.py`

### Example: Adding a New Feature

```python
# 1. Service Layer
class NewFeatureService:
    @staticmethod
    def process_data(data):
        # Business logic here
        return result, error

# 2. Page Layer  
class NewFeaturePage(BasePage):
    def get_template_name(self):
        return 'new_feature.html'
    
    def process_form(self, form_data):
        # UI logic here
        return success, redirect_url, error

# 3. Controller Layer
@new_controller.route('/action', methods=['GET', 'POST'])
@role_required(['user'])
def new_action():
    page = NewFeaturePage()
    # Route handling logic
    return page.render()
```

## 🧪 Testing

The POM structure enables comprehensive testing:

- **Unit Tests** - Test individual services and page methods
- **Integration Tests** - Test controller endpoints and workflows
- **Mock Testing** - Easy to mock dependencies between layers

## 📚 Documentation

- **`POM_ARCHITECTURE.md`** - Detailed architecture documentation
- **`README.md`** - Original project documentation
- **Code Comments** - Inline documentation throughout the codebase

## 🔄 Migration from Original

The application now runs with the POM architecture:

- **Run Application:** `python app.py`

The POM version maintains all original functionality while providing better code organization and maintainability.

## 🤝 Contributing

When contributing to the POM version:

1. Follow the established layer patterns
2. Add appropriate error handling
3. Include docstrings for new methods
4. Test your changes thoroughly
5. Update documentation as needed

## 📝 License

This project is for educational purposes. Feel free to use and modify as needed.

---

**Note:** This POM refactoring demonstrates modern software architecture principles applied to a Flask web application, making it more maintainable and scalable for future development.
