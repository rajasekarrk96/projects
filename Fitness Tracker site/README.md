# Workout Sphere - Flask Application

A fitness tracking web application built with Flask, SQLite, and Tailwind CSS.

## Features

- User authentication (register, login, profile management)
- Track workouts and exercises
- Create and manage workout routines
- Social feed to share workout progress
- Responsive design for mobile and desktop

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. Clone the repository

```bash
git clone https://github.com/yourusername/workout-sphere.git
cd workout-sphere/flask_app
```

2. Create a virtual environment (optional but recommended)

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Initialize the database

```bash
python app.py
```

5. Run the application

```bash
flask run
# or
python app.py
```

6. Open your browser and navigate to `http://127.0.0.1:5000`

## Project Structure

```
flask_app/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── static/                # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
└── templates/             # HTML templates
    ├── layout.html        # Base template
    ├── index.html         # Landing page
    ├── dashboard.html     # User dashboard
    └── ...
```

## Technologies Used

- **Backend**: Flask, SQLAlchemy, SQLite
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Authentication**: Flask session management

## License

MIT