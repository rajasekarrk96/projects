from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlite3

def upgrade():
    # Connect to the SQLite database
    conn = sqlite3.connect('workout_sphere.db')
    cursor = conn.cursor()
    
    # Add the frequency column with a default value of 'Daily'
    cursor.execute('ALTER TABLE routine ADD COLUMN frequency VARCHAR(50) DEFAULT "Daily"')
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    upgrade() 