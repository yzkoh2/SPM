-- Tracks which deadline reminders have been sent to prevent duplicates
CREATE TABLE deadline_reminders (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    days_before INTEGER NOT NULL CHECK (days_before IN (7, 3, 1)),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure we only send one reminder per (task_id, days_before) combination
    UNIQUE(task_id, days_before)
);

-- Indexes for faster lookups
CREATE INDEX idx_deadline_reminders_task ON deadline_reminders(task_id);
CREATE INDEX idx_deadline_reminders_days ON deadline_reminders(days_before);
CREATE INDEX idx_deadline_reminders_sent_at ON deadline_reminders(sent_at);

COMMENT ON TABLE deadline_reminders IS 'Tracks deadline reminder notifications (7, 3, 1 days before) to prevent duplicates';