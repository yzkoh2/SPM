from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class DeadlineReminder(db.Model):
    Track sent deadline reminders to prevent duplicates
    __tablename__ = "deadline_reminders"
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, nullable=False)
    days_before = db.Column(db.Integer, nullable=False)  # 7, 3, or 1
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Prevent duplicate reminders for same task + interval
    __table_args__ = (
        db.UniqueConstraint('task_id', 'days_before', name='unique_task_reminder'),
    )