from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from . import service


class DeadlineReminderScheduler:
    
    #Background scheduler for deadline reminder notifications.
    #Runs every hour to check for tasks with upcoming deadlines and sends reminder emails at 7, 3, and 1 days before.
    
    def __init__(self, app):
        self.app = app
        self.scheduler = BackgroundScheduler()
        
    def start(self):
        #Start the scheduler
        try:
            #Schedule the deadline check to run every hour
            self.scheduler.add_job(
                func=self._run_deadline_check,
                trigger=CronTrigger(minute='*'), #Run at every minute testing
                #trigger=CronTrigger(minute='0'), #Run at the top of every hour
                id='deadline_reminder_check',
                name='Check and send deadline reminders',
                replace_existing=True
            )
            
            self.scheduler.start()
            print("✅ Deadline reminder scheduler started")
            print("   Schedule: Every hour at :00 minutes")
            print(f"   Next run: {self.scheduler.get_jobs()[0].next_run_time}")
            
        except Exception as e:
            print(f"❌ Failed to start scheduler: {e}")
    
    def _run_deadline_check(self):
        #Wrapper to run deadline check with app context
        with self.app.app_context():
            try:
                service.check_and_send_deadline_reminders()
            except Exception as e:
                print(f"❌ Error in scheduled deadline check: {e}")
                import traceback
                traceback.print_exc()
    
    def stop(self):
        #Stop the scheduler
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("⏹️ Deadline reminder scheduler stopped")
    
    def run_now(self):
        #Manually trigger deadline check (for testing)
        with self.app.app_context():
            print("🧪 Manual deadline check triggered")
            return service.check_and_send_deadline_reminders()


def start_deadline_scheduler(app):
    #Initialize and start the deadline reminder schedule
    scheduler = DeadlineReminderScheduler(app)
    scheduler.start()
    return scheduler