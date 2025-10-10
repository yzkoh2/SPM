from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class DeadlineReminder(db.Model):
    
    #Track which deadline reminders have been sent to prevent duplicates.
    # Purpose: Ensure we only send one "7-day reminder" per task, 
    # one "3-day reminder" per task, and one "1-day reminder" per task.
    
    # Without this table, the scheduler would send duplicate reminders
    # every time it runs (potentially every hour = spam!).

    __tablename__ = "deadline_reminders"
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, nullable=False, index=True)
    days_before = db.Column(db.Integer, nullable=False)  # Must be 7, 3, or 1
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Composite unique constraint: Only one reminder per (task_id, days_before) combination
    __table_args__ = (
        db.UniqueConstraint('task_id', 'days_before', name='unique_task_reminder'),
    )
    
    def __repr__(self):
        return f'<DeadlineReminder task_id={self.task_id} days_before={self.days_before}>'