from app import db
from sqlalchemy import text

def upgrade():
    # Add new columns to Appointment table
    with db.engine.connect() as conn:
        conn.execute(text('ALTER TABLE appointment ADD COLUMN payment_method VARCHAR(20)'))
        conn.execute(text('ALTER TABLE appointment ADD COLUMN payment_details TEXT'))
        conn.execute(text('ALTER TABLE appointment ADD COLUMN payment_status VARCHAR(20) DEFAULT "pending"'))
        conn.execute(text('COMMIT'))

if __name__ == '__main__':
    upgrade()
    print("Migration completed successfully!") 