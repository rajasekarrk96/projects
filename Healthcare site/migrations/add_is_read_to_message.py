from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import app, db

def upgrade():
    with app.app_context():
        # Add is_read column to Message table
        db.engine.execute('ALTER TABLE message ADD COLUMN is_read BOOLEAN DEFAULT FALSE')

def downgrade():
    with app.app_context():
        # Remove is_read column from Message table
        db.engine.execute('ALTER TABLE message DROP COLUMN is_read') 