from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from zoneinfo import ZoneInfo
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
    sent_at = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo('Asia/Singapore')))
    
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

class OverdueAlert(db.Model):
    #Track overdue task alerts to prevent duplicate notifications
    #Example:
    #Task ID 123 with deadline on Jan 10th:
    #Jan 11: Send 1 day overdue, record: (task_id=123, days_overdue=1)
    #Jan 13: Send 3 day overdue, record: (task_id=123, days_overdue=3)
    #Jan X: Send X day overdue, record: (task_id=123, days_overdue=X), will continue to send day by day (1 time each day) until task is marked completed
    __tablename__ = 'overdue_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, nullable=False)
    alert_date = db.Column(db.Date, nullable=False)
    days_overdue = db.Column(db.Integer, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('task_id', 'alert_date', name='unique_task_alert_date'),
    )
    
    def __repr__(self):
        return f'<OverdueAlert task_id={self.task_id} alert_date={self.alert_date} days_overdue={self.days_overdue}>'

class MentionNotification(db.Model):
    #Model to track mention alert notifications sent to prevents duplicate notifications for the same mention.
    __tablename__ = 'mention_notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, nullable=False, index=True)
    comment_id = db.Column(db.Integer, nullable=False, index=True)
    mentioned_user_id = db.Column(db.Integer, nullable=False, index=True)
    author_id = db.Column(db.Integer, nullable=False)
    sent_at = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(ZoneInfo('Asia/Singapore')),
        nullable=False
    )
    
    __table_args__ = (
        db.UniqueConstraint(
            'comment_id', 
            'mentioned_user_id', 
            name='unique_mention_notification'
        ),
    )
    
    def __repr__(self):
        return f'<MentionNotification task_id={self.task_id} mentioned_user={self.mentioned_user_id}>'