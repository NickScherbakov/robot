"""
Automated task scheduler for the Earning Robot.
Handles periodic tasks like daily reports.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from backend.config import Config
from backend.database import Database
from billing.reporting import ReportGenerator
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskScheduler:
    """Manages scheduled tasks"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.db = Database(Config.DATABASE_PATH).initialize()
    
    def send_telegram_notification(self, message):
        """
        Send notification via Telegram
        
        Args:
            message: Message text to send
        """
        if not Config.TELEGRAM_BOT_TOKEN or not Config.TELEGRAM_OWNER_ID:
            logger.warning("Telegram not configured, skipping notification")
            return
        
        try:
            url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': Config.TELEGRAM_OWNER_ID,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=data)
            
            if response.status_code == 200:
                logger.info("Telegram notification sent successfully")
            else:
                logger.error(f"Failed to send Telegram notification: {response.text}")
                
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
    
    def generate_daily_report(self):
        """Generate and send daily financial report"""
        logger.info("Generating daily report...")
        
        session = self.db.get_session()
        
        try:
            generator = ReportGenerator(session)
            report = generator.format_report('daily')
            
            # Send report via Telegram
            self.send_telegram_notification(report)
            
            logger.info("Daily report sent successfully")
            
        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
            
        finally:
            session.close()
    
    def generate_weekly_report(self):
        """Generate and send weekly financial report"""
        logger.info("Generating weekly report...")
        
        session = self.db.get_session()
        
        try:
            generator = ReportGenerator(session)
            report = generator.format_report('weekly')
            
            # Send report via Telegram
            self.send_telegram_notification(report)
            
            logger.info("Weekly report sent successfully")
            
        except Exception as e:
            logger.error(f"Error generating weekly report: {e}")
            
        finally:
            session.close()
    
    def check_system_health(self):
        """Check system health and send alerts if needed"""
        logger.info("Checking system health...")
        
        session = self.db.get_session()
        
        try:
            from backend.database import Task
            from sqlalchemy import func
            from datetime import datetime, timedelta
            
            # Check for recent failed tasks
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            failed_tasks = session.query(Task).filter(
                Task.status == 'failed',
                Task.created_at >= one_hour_ago
            ).count()
            
            if failed_tasks > 5:
                alert = f"⚠️ Health Alert: {failed_tasks} tasks failed in the last hour!"
                self.send_telegram_notification(alert)
                logger.warning(alert)
            
        except Exception as e:
            logger.error(f"Error checking system health: {e}")
            
        finally:
            session.close()
    
    def start(self):
        """Start the scheduler with configured tasks"""
        # Parse report time (format: HH:MM)
        report_hour, report_minute = map(int, Config.REPORT_TIME.split(':'))
        
        # Daily report at configured time
        self.scheduler.add_job(
            self.generate_daily_report,
            trigger=CronTrigger(hour=report_hour, minute=report_minute),
            id='daily_report',
            name='Generate Daily Report'
        )
        
        # Weekly report every Monday at configured time
        self.scheduler.add_job(
            self.generate_weekly_report,
            trigger=CronTrigger(day_of_week='mon', hour=report_hour, minute=report_minute),
            id='weekly_report',
            name='Generate Weekly Report'
        )
        
        # Health check every hour
        self.scheduler.add_job(
            self.check_system_health,
            trigger=CronTrigger(minute=0),
            id='health_check',
            name='System Health Check'
        )
        
        self.scheduler.start()
        logger.info("📅 Task scheduler started")
        logger.info(f"Daily reports scheduled for {Config.REPORT_TIME} {Config.TIMEZONE}")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Task scheduler stopped")


if __name__ == '__main__':
    scheduler = TaskScheduler()
    scheduler.start()
    
    # Keep the script running
    try:
        import time
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.stop()
