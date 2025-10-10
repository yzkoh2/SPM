from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

db = SQLAlchemy()


class DeadlineReminder(db.Model):
    
    #Track which deadline reminders have been sent to prevent duplicates.    
    #Example:
    #Task ID 123 with deadline on Jan 10th:
    #Jan 3rd: Send 7-day reminder, record: (task_id=123, days_before=7)
    #Jan 7th: Send 3-day reminder, record: (task_id=123, days_before=3)
    #Jan 9th: Send 1-day reminder, record: (task_id=123, days_before=1)
    
    __tablename__ = "deadline_reminders"
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, nullable=False, index=True)
    days_before = db.Column(db.Integer, nullable=False)  
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('task_id', 'days_before', name='unique_task_reminder'),
    )
    
    def __repr__(self):
        return f'<DeadlineReminder task_id={self.task_id} days_before={self.days_before}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'days_before': self.days_before,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None
        }
