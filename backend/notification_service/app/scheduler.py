from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.pool import ThreadPoolExecutor
from datetime import datetime
import pytz
from . import service


class NotificationScheduler:
    #Background scheduler for deadline reminders and overdue alerts
    def __init__(self, app):
        self.app = app
        singapore_tz = pytz.timezone('Asia/Singapore')
        
        #Configure scheduler with single-threaded executor to run jobs sequentially
        #For console log debugging/representation purpose
        executors = {'default': ThreadPoolExecutor(1)}
        job_defaults = {
            'coalesce': True,           #Combine missed executions
            'max_instances': 1,         #One instance per job
            'misfire_grace_time': 60    #Allow 60s late execution
        }
        
        self.scheduler = BackgroundScheduler(
            executors=executors,
            job_defaults=job_defaults,
            timezone=singapore_tz
        )
        
    def start(self):
        #Start the scheduler with notification jobs
        try:
            singapore_tz = pytz.timezone('Asia/Singapore')
            
            #Single combined job that runs both checks sequentially
            self.scheduler.add_job(
                func=self._run_all_checks,
                trigger=CronTrigger(minute='*', timezone=singapore_tz),      # Testing: Every minute
                #trigger=CronTrigger(minute='0', timezone=singapore_tz),     # Testing: Hourly
                id='notification_check',
                name='Notification Check (Deadline + Overdue)',
                replace_existing=True
            )
            
            self.scheduler.start()
            
            #Print startup info
            current_time = datetime.now(singapore_tz)
            print(f"\n{'='*70}")
            print(f"✅ NOTIFICATION SCHEDULER STARTED")
            print(f"   Time: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            #print(f"   Mode: Production (Hourly)") # Uncomment for testing via hour
            print(f"   Mode: Testing (Every minute)")  
            print(f"{'='*70}")
            
            for job in self.scheduler.get_jobs():
                print(f"📋 {job.name}")
                print(f"   Next run: {job.next_run_time}")
            
            print(f"{'='*70}\n")
            
        except Exception as e:
            print(f"❌ Scheduler failed to start: {e}")
            import traceback
            traceback.print_exc()
    
    def _run_all_checks(self):
        #Execute both deadline and overdue checks sequentially
        with self.app.app_context():
            try:
                #Run deadline reminders first
                service.check_and_send_deadline_reminders()
                
                #Then run overdue alerts
                service.check_and_send_overdue_alerts()
                
            except Exception as e:
                print(f"❌ Notification check error: {e}")
                import traceback
                traceback.print_exc()
    
    def stop(self):
        #Stop the scheduler
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("⏹️  Notification scheduler stopped")
    
    def run_checks_now(self):
        #Manually trigger both checks (for testing)
        with self.app.app_context():
            print("🧪 Manual notification checks triggered")
            service.check_and_send_deadline_reminders()
            service.check_and_send_overdue_alerts()
    
    #Keep individual methods for backward compatibility/testing
    def run_deadline_check_now(self):
        #Manually trigger deadline check only (for testing)
        with self.app.app_context():
            print("🧪 Manual deadline check triggered")
            return service.check_and_send_deadline_reminders()
    
    def run_overdue_check_now(self):
        #Manually trigger overdue check only (for testing)
        with self.app.app_context():
            print("🧪 Manual overdue check triggered")
            return service.check_and_send_overdue_alerts()


def start_notification_scheduler(app):
    #Initialize and start the notification scheduler
    scheduler = NotificationScheduler(app)
    scheduler.start()
    return scheduler