from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlite3

def upgrade():
    # Connect to the SQLite database
    conn = sqlite3.connect('workout_sphere.db')
    cursor = conn.cursor()
    
    # Create the exercise table
    cursor.execute('''
        CREATE TABLE exercise (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            sets INTEGER NOT NULL,
            reps INTEGER NOT NULL,
            weight FLOAT,
            notes TEXT,
            workout_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (workout_id) REFERENCES workout (id)
        )
    ''')
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    upgrade() 