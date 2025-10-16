DROP TABLE IF EXISTS deadline_reminders CASCADE;
DROP TABLE IF EXISTS overdue_alerts CASCADE;
DROP INDEX IF EXISTS idx_deadline_reminders_task;
DROP INDEX IF EXISTS idx_deadline_reminders_days;
DROP INDEX IF EXISTS idx_deadline_reminders_sent_at;
DROP INDEX IF EXISTS idx_overdue_alerts_task;
DROP INDEX IF EXISTS idx_overdue_alerts_date;
DROP INDEX IF EXISTS idx_overdue_alerts_sent_at;

-- Tracks which deadline reminders have been sent to prevent duplicates
CREATE TABLE deadline_reminders (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    days_before INTEGER NOT NULL CHECK (days_before IN (7, 3, 1)),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure we only send one reminder per (task_id, days_before) combination
    UNIQUE(task_id, days_before)
);

-- Tracks which overdue alerts have been sent to prevent duplicate daily notifications
CREATE TABLE overdue_alerts (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    alert_date DATE NOT NULL,  -- Date when the alert was sent
    days_overdue INTEGER NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure we only send one alert per task per day
    UNIQUE(task_id, alert_date)
);

-- Indexes for faster lookups
CREATE INDEX idx_deadline_reminders_task ON deadline_reminders(task_id);
CREATE INDEX idx_deadline_reminders_days ON deadline_reminders(days_before);
CREATE INDEX idx_deadline_reminders_sent_at ON deadline_reminders(sent_at);
CREATE INDEX idx_overdue_alerts_task ON overdue_alerts(task_id);
CREATE INDEX idx_overdue_alerts_date ON overdue_alerts(alert_date);
CREATE INDEX idx_overdue_alerts_sent_at ON overdue_alerts(sent_at);

COMMENT ON TABLE deadline_reminders IS 'Tracks deadline reminder notifications (7, 3, 1 days before) to prevent duplicates';
COMMENT ON TABLE overdue_alerts IS 'Tracks overdue task notifications sent daily to prevent duplicates';
