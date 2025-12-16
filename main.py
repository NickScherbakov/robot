"""
Main entry point for the Earning Robot.
Runs all components together.
"""
from backend.app import app
from backend.scheduler import TaskScheduler
from frontend.telegram_bot import TelegramBot
from backend.config import Config
import threading
import logging
import sys

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def run_flask_server():
    """Run Flask API server"""
    logger.info("🌐 Starting Flask API server...")
    app.run(host=Config.HOST, port=Config.PORT, debug=False, use_reloader=False)


def run_telegram_bot():
    """Run Telegram bot"""
    logger.info("🤖 Starting Telegram bot...")
    bot = TelegramBot()
    bot.run()


def run_scheduler():
    """Run task scheduler"""
    logger.info("📅 Starting task scheduler...")
    scheduler = TaskScheduler()
    scheduler.start()
    
    # Keep scheduler running
    try:
        import time
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.stop()


def main():
    """Main entry point - runs all components"""
    print("""
    ╔═══════════════════════════════════════╗
    ║     🤖 EARNING ROBOT STARTING 🤖     ║
    ╚═══════════════════════════════════════╝
    """)
    
    try:
        # Validate configuration
        Config.validate()
        logger.info("✅ Configuration validated")
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        logger.error("Please check your .env file")
        sys.exit(1)
    
    # Start components in separate threads
    threads = []
    
    # Start Flask server
    flask_thread = threading.Thread(target=run_flask_server, daemon=True)
    flask_thread.start()
    threads.append(flask_thread)
    
    # Start scheduler
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    threads.append(scheduler_thread)
    
    # Run Telegram bot in main thread (it has its own event loop)
    try:
        run_telegram_bot()
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down gracefully...")
        sys.exit(0)


if __name__ == '__main__':
    main()
