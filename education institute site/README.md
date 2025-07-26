# 🎓 Edusphere Institute Management System

A comprehensive full-stack web application for managing technical training institutes. Built with Python Flask, MySQL, and modern web technologies.

## 🚀 Features

### 🔐 Authentication & User Management
- Role-based access control (Admin, Staff, Faculty, Student)
- Secure login system with password hashing
- User profile management

### 📝 Admission & Enquiry Management
- Student enquiry form with course selection
- Front office staff can follow up and verify enquiries
- Admin approval system for admissions
- Automatic student registration number generation

### 🎓 Course & Batch Management
- Add/edit courses with detailed syllabus and fee structure
- Create batches and assign faculty members
- Track student count by batch
- Course duration and capacity management

### 💸 Fee Management
- Course-wise fee structure
- Payment entry with receipt generation
- Pending fee reports and tracking
- Monthly and yearly revenue statistics

### 📅 Exam & Certification
- Faculty can schedule exams for their batches
- Admin/faculty can update student marks
- Automatic scorecard generation
- Certificate generation for passing students

### 👨‍🏫 Faculty Management
- Faculty profile management with qualifications
- Batch and subject assignments
- Student attendance tracking
- Salary and schedule management

### 📊 Admin Dashboard
- Comprehensive statistics and analytics
- Total students, enquiries, and monthly admissions
- Monthly collection and pending fees overview
- Faculty performance tracking

### ⏱️ Attendance Management
- Student-wise attendance tracking by date and batch
- Staff attendance panel for salary processing
- Attendance percentage calculations

### 💰 Salary Management
- Faculty attendance-based salary calculation
- Salary history and bonus support
- Payment status tracking

### 📧 Notifications & Reports
- Auto-generated PDF certificates and receipts
- Email/SMS alert system (configurable)
- Comprehensive reporting system

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Templating**: Jinja2
- **Authentication**: Flask-Login
- **PDF Generation**: ReportLab
- **Additional**: Chart.js, Font Awesome

## 📋 Prerequisites

- Python 3.8 or higher
- MySQL 5.7 or higher
- pip (Python package installer)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd edusphere-institute-management
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Option A: Using MySQL
1. Create a MySQL database:
```sql
CREATE DATABASE edusphere_db;
```

2. Update database configuration in `app.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/edusphere_db'
```

#### Option B: Using SQLite (for development)
The application will automatically use SQLite if MySQL is not configured.

### 5. Environment Variables
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql+pymysql://username:password@localhost/edusphere_db
```

### 6. Initialize Database
```bash
python init_db.py
```

### 7. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 👥 Demo Accounts

After running the initialization script, you can use these demo accounts:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@edusphere.com | admin123 |
| Staff | staff@edusphere.com | staff123 |
| Faculty | faculty@edusphere.com | faculty123 |
| Student | student@edusphere.com | student123 |

## 📁 Project Structure

```
edusphere-institute-management/
├── app.py                 # Main Flask application
├── models.py             # Database models
├── routes.py             # Application routes
├── init_db.py            # Database initialization script
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
├── .env                 # Environment variables (create this)
└── templates/           # HTML templates
    ├── base.html        # Base template
    ├── index.html       # Landing page
    ├── login.html       # Login page
    ├── enquiry.html     # Enquiry form
    ├── admin/           # Admin templates
    ├── staff/           # Staff templates
    ├── faculty/         # Faculty templates
    └── student/         # Student templates
```

## 🎯 User Roles & Permissions

### 👨‍💼 Admin
- Full system access
- Course and batch management
- Faculty management
- Reports and analytics
- System configuration

### 👩‍💼 Staff (Front Office)
- Enquiry management
- Student admissions
- Fee collection
- Student records

### 👨‍🏫 Faculty
- Batch management
- Attendance tracking
- Exam scheduling and results
- Student performance monitoring

### 👨‍🎓 Student
- View personal information
- Check attendance
- View exam results
- Fee status and history

## 🔧 Configuration

### Database Configuration
Update the database connection string in `app.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/edusphere_db'
```

### Email Configuration (Optional)
To enable email notifications, add email settings to your `.env` file:
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## 📊 Features in Detail

### Dashboard Analytics
- Real-time statistics
- Monthly/yearly reports
- Performance metrics
- Revenue tracking

### Student Management
- Complete student lifecycle
- Academic progress tracking
- Fee management
- Certificate generation

### Faculty Management
- Profile management
- Batch assignments
- Performance tracking
- Salary management

### Course Management
- Flexible course structure
- Syllabus management
- Fee configuration
- Batch scheduling

## 🚀 Deployment

### Production Deployment
1. Set up a production server (Ubuntu/CentOS)
2. Install Python, MySQL, and Nginx
3. Configure environment variables
4. Set up SSL certificate
5. Configure Nginx as reverse proxy
6. Use Gunicorn for WSGI server

### Docker Deployment (Optional)
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

- Password hashing with bcrypt
- Session management
- Role-based access control
- SQL injection prevention
- XSS protection
- CSRF protection

## 📈 Future Enhancements

- Mobile application for students
- Biometric attendance system
- AI-based performance prediction
- UPI/GPay integration for fees
- Video conferencing integration
- Learning management system (LMS)
- Student portal mobile app
- Advanced analytics and reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🎉 Acknowledgments

- Flask community for the excellent framework
- Bootstrap team for the responsive UI components
- Font Awesome for the beautiful icons
- All contributors and testers

---

**Made with ❤️ for educational institutions** 