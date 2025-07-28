# ProConnect - Professional Networking Platform

A modern, feature-rich professional networking platform built with Flask, designed for students, freelancers, academicians, startups, and training institutes.

## 🚀 Features

### Core Features
- **User Authentication & Profiles**: Secure registration, login, and detailed user profiles
- **Professional Networking**: Connect with other professionals, send/receive connection requests
- **Post Feed**: Share updates, achievements, and insights with your network
- **Job Board**: Post and apply for jobs, internships, and freelance opportunities
- **Real-time Interactions**: Like, comment, and engage with posts
- **File Uploads**: Profile pictures, post images, and resume uploads
- **Responsive Design**: Modern, mobile-friendly interface

### User Roles
- **Individual Users**: Students, professionals, freelancers
- **Companies/Institutions**: Post jobs and manage applications
- **Admin**: Platform management and moderation

### Advanced Features
- **Socket.IO Integration**: Real-time notifications and chat (ready for implementation)
- **AJAX Interactions**: Smooth, dynamic user experience
- **Form Validation**: Client and server-side validation
- **File Management**: Secure file uploads with validation
- **Search & Filters**: Advanced job and user search capabilities

## 🛠️ Tech Stack

### Backend
- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **Flask-Login**: User authentication
- **Flask-SocketIO**: Real-time features
- **Werkzeug**: File uploads and security

### Frontend
- **Bootstrap 5**: Responsive UI framework
- **Font Awesome**: Icons
- **Vanilla JavaScript**: Interactive features
- **CSS3**: Custom styling and animations

### Database
- **SQLite**: Development database (easily switchable to MySQL/PostgreSQL)

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ProConnect
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python app.py
   ```
   This will create the SQLite database with all necessary tables.

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## 🏗️ Project Structure

```
ProConnect/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Custom styles
│   ├── js/
│   │   └── main.js       # Main JavaScript file
│   └── uploads/          # File uploads directory
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Landing page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # User dashboard
│   ├── profile.html      # User profile
│   ├── edit_profile.html # Edit profile
│   ├── jobs.html         # Job listings
│   ├── post_job.html     # Post job form
│   └── connections.html  # Connections management
└── proconnect.db         # SQLite database (created on first run)
```

## 🎯 Usage Guide

### For Individual Users

1. **Registration**: Create an account with your professional details
2. **Profile Setup**: Add your bio, skills, experience, and education
3. **Networking**: Connect with other professionals in your field
4. **Job Search**: Browse and apply for relevant opportunities
5. **Engagement**: Share posts, like, and comment on content

### For Companies

1. **Company Registration**: Register as a company account
2. **Job Posting**: Create detailed job listings with requirements
3. **Application Management**: Review and manage job applications
4. **Brand Building**: Share company updates and achievements

### Key Features Walkthrough

#### Creating Posts
- Navigate to Dashboard
- Use the "Share something" form
- Add text content and optional images
- Posts appear in your network's feed

#### Job Applications
- Browse available jobs
- Click "Apply Now" on desired positions
- Submit cover letter and resume
- Track application status

#### Networking
- Visit user profiles
- Send connection requests
- Accept/reject incoming requests
- Build your professional network

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///proconnect.db
UPLOAD_FOLDER=static/uploads
```

### Database Configuration
The application uses SQLite by default. To switch to MySQL:

1. Install MySQL dependencies:
   ```bash
   pip install PyMySQL
   ```

2. Update the database URI in `app.py`:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/proconnect'
   ```

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
1. Set up a production server (Ubuntu, CentOS, etc.)
2. Install Python, pip, and virtual environment
3. Clone the repository
4. Install dependencies
5. Configure environment variables
6. Use a WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

### Docker Deployment
Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 🔒 Security Features

- **Password Hashing**: Secure password storage using Werkzeug
- **CSRF Protection**: Built-in CSRF protection with Flask-WTF
- **File Upload Security**: Secure file handling with validation
- **SQL Injection Prevention**: Parameterized queries with SQLAlchemy
- **XSS Protection**: Template escaping and input validation

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- All modern browsers

## 🎨 Customization

### Styling
- Modify `static/css/style.css` for custom styles
- Update color variables in CSS for brand consistency
- Add custom animations and transitions

### Functionality
- Extend models in `app.py` for additional features
- Add new routes for custom functionality
- Implement additional API endpoints

## 🧪 Testing

### Manual Testing
1. Test user registration and login
2. Verify profile creation and editing
3. Test job posting and application
4. Check connection functionality
5. Verify post creation and interactions

### Automated Testing
Add test files to test core functionality:

```python
# test_app.py
import unittest
from app import app, db

class ProConnectTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.create_all()

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🚀 Future Enhancements

### Planned Features
- **Real-time Messaging**: Complete Socket.IO implementation
- **Advanced Search**: Elasticsearch integration
- **Email Notifications**: SMTP integration
- **Mobile App**: React Native companion app
- **Analytics Dashboard**: User engagement metrics
- **API Documentation**: Swagger/OpenAPI specs
- **Multi-language Support**: Internationalization
- **Payment Integration**: Premium features and job posting fees

### Technical Improvements
- **Caching**: Redis integration for performance
- **Background Jobs**: Celery for async tasks
- **Microservices**: Service-oriented architecture
- **Containerization**: Docker and Kubernetes
- **CI/CD**: Automated testing and deployment

---

**ProConnect** - Connect, Collaborate, Grow! 🚀 