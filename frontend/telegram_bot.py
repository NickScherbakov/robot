"""
Telegram Bot interface for the Earning Robot.
Provides owner control and user interaction.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from backend.config import Config
from backend.database import Database, User, Task
from backend.ai_providers import AIManager
from billing.payment_processor import PaymentProcessor
from billing.reporting import ReportGenerator
from datetime import datetime
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot for robot control"""
    
    def __init__(self):
        self.db = Database(Config.DATABASE_PATH).initialize()
        self.ai_manager = AIManager()
        self.owner_id = Config.TELEGRAM_OWNER_ID
    
    def is_owner(self, user_id):
        """Check if user is the owner"""
        return str(user_id) == str(self.owner_id)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        welcome_text = f"""
👋 Welcome to the Earning Robot!

I'm an AI-powered automation system that can help you with various tasks.

Available commands:
/help - Show help information
/ask - Ask AI a question
/status - Check robot status
/report - Get financial report
/settings - Configure settings
/selfbot - SelfEarnBot control (autonomous earning)

Let's get started! What would you like to do?
"""
        
        if self.is_owner(user.id):
            welcome_text += "\n🔑 Owner privileges activated!"
        
        await update.message.reply_text(welcome_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📖 Available Commands:

🤖 User Commands:
/start - Start the bot
/help - Show this help message
/ask <question> - Ask AI a question
/status - Check system status

👑 Owner Commands:
/report [daily|weekly|monthly] - Get financial report
/stats - Get detailed statistics
/settings - Configure robot settings
/broadcast <message> - Send message to all users

💡 Examples:
• /ask What is the capital of France?
• /report daily
• /status
"""
        await update.message.reply_text(help_text)
    
    async def ask_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ask command - AI query"""
        user = update.effective_user
        
        if not context.args:
            await update.message.reply_text(
                "Please provide a question. Example: /ask What is AI?"
            )
            return
        
        question = ' '.join(context.args)
        
        # Send "thinking" message
        thinking_msg = await update.message.reply_text("🤔 Processing your request...")
        
        try:
            # Get or create user
            session = self.db.get_session()
            db_user = session.query(User).filter_by(telegram_id=str(user.id)).first()
            if not db_user:
                db_user = User(telegram_id=str(user.id))
                session.add(db_user)
                session.commit()
            
            # Create task record
            task = Task(
                user_id=db_user.id,
                task_type='chat',
                ai_provider='openai',
                input_text=question,
                status='processing'
            )
            session.add(task)
            session.commit()
            
            # Get AI response
            result = self.ai_manager.execute_task(question, provider='openai')
            
            # Update task
            task.output_text = result['response']
            task.tokens_used = result['tokens_used']
            task.cost = result['cost']
            task.status = 'completed'
            task.completed_at = datetime.utcnow()
            session.commit()
            
            # Record expense
            payment_processor = PaymentProcessor(session)
            payment_processor.record_expense(
                amount=result['cost'],
                category='api_cost',
                description=f"OpenAI API - {result['tokens_used']} tokens"
            )
            
            # Send response
            response_text = f"🤖 AI Response:\n\n{result['response']}\n\n"
            response_text += f"📊 Tokens used: {result['tokens_used']} | Cost: ${result['cost']:.4f}"
            
            await thinking_msg.edit_text(response_text)
            
            session.close()
            
        except Exception as e:
            logger.error(f"Error processing AI request: {e}")
            await thinking_msg.edit_text(
                f"❌ Sorry, an error occurred: {str(e)}"
            )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        session = self.db.get_session()
        
        try:
            # Get task statistics
            total_tasks = session.query(Task).count()
            completed_tasks = session.query(Task).filter_by(status='completed').count()
            failed_tasks = session.query(Task).filter_by(status='failed').count()
            
            # Get user count
            total_users = session.query(User).count()
            active_users = session.query(User).filter_by(is_active=True).count()
            
            status_text = f"""
🤖 Robot Status

📊 Tasks:
• Total: {total_tasks}
• Completed: {completed_tasks}
• Failed: {failed_tasks}

👥 Users:
• Total: {total_users}
• Active: {active_users}

✅ System: Online
🕒 Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
            
            await update.message.reply_text(status_text)
            
        finally:
            session.close()
    
    async def report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /report command - owner only"""
        user = update.effective_user
        
        if not self.is_owner(user.id):
            await update.message.reply_text("⛔ This command is only available to the owner.")
            return
        
        report_type = context.args[0] if context.args else 'daily'
        
        if report_type not in ['daily', 'weekly', 'monthly']:
            await update.message.reply_text(
                "Invalid report type. Use: daily, weekly, or monthly"
            )
            return
        
        session = self.db.get_session()
        try:
            generator = ReportGenerator(session)
            report = generator.format_report(report_type)
            await update.message.reply_text(report)
        finally:
            session.close()
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command - owner only"""
        user = update.effective_user
        
        if not self.is_owner(user.id):
            await update.message.reply_text("⛔ This command is only available to the owner.")
            return
        
        keyboard = [
            [InlineKeyboardButton("📊 View Reports", callback_data='settings_reports')],
            [InlineKeyboardButton("💰 Payment Settings", callback_data='settings_payment')],
            [InlineKeyboardButton("🤖 AI Settings", callback_data='settings_ai')],
            [InlineKeyboardButton("❌ Close", callback_data='settings_close')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚙️ Settings Menu",
            reply_markup=reply_markup
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'settings_close':
            await query.edit_message_text("Settings closed.")
        elif query.data == 'settings_reports':
            await query.edit_message_text(
                f"📊 Report Settings\n\n"
                f"Report Time: {Config.REPORT_TIME}\n"
                f"Timezone: {Config.TIMEZONE}"
            )
        elif query.data == 'settings_payment':
            await query.edit_message_text(
                f"💰 Payment Settings\n\n"
                f"Monthly Subscription: ${Config.SUBSCRIPTION_MONTHLY_PRICE}\n"
                f"Micro-payment: ${Config.MICRO_PAYMENT_PRICE}"
            )
        elif query.data == 'settings_ai':
            openai_status = "✅" if Config.OPENAI_API_KEY else "❌"
            mistral_status = "✅" if Config.MISTRAL_API_KEY else "❌"
            
            await query.edit_message_text(
                f"🤖 AI Settings\n\n"
                f"OpenAI: {openai_status}\n"
                f"Mistral: {mistral_status}"
            )
    
    async def selfbot_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /selfbot command - SelfEarnBot control"""
        user = update.effective_user
        
        if not self.is_owner(user.id):
            await update.message.reply_text("❌ This command is only available to the owner")
            return
        
        help_text = """
🤖 SelfEarnBot - AI Content Arbitrage Bot

Available commands:
/selfbot_start - Start SelfBot autonomous operation
/selfbot_stop - Stop SelfBot
/selfbot_status - Check SelfBot status
/selfbot_stats - Get earnings statistics
/selfbot_report - Get detailed report
/selfbot_budget <amount> - Set budget

ℹ️ SelfBot automatically finds content opportunities, generates content with AI, and earns money through content arbitrage.
"""
        await update.message.reply_text(help_text)
    
    async def selfbot_status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /selfbot_status command"""
        user = update.effective_user
        
        if not self.is_owner(user.id):
            await update.message.reply_text("❌ This command is only available to the owner")
            return
        
        try:
            from selfbot.database import SelfBotDatabase
            from selfbot.finance import SelfBotReports
            from selfbot.config import SelfBotConfig
            
            db = SelfBotDatabase(SelfBotConfig.DATABASE_PATH).initialize()
            session = db.get_session()
            reports = SelfBotReports(session)
            
            stats = reports.generate_summary_stats()
            
            status_text = f"""
📊 SelfBot Status

💰 Financial Summary:
├─ Total Revenue: ${stats['total_revenue']:.2f}
├─ Total Costs: ${stats['total_cost']:.2f}
├─ Total Profit: ${stats['total_profit']:.2f}
└─ Avg Profit/Op: ${stats['average_profit_per_operation']:.2f}

📈 Operations:
├─ Opportunities: {stats['total_opportunities']}
├─ Content Generated: {stats['total_content_generated']}
└─ Published: {stats['total_published']}

⚙️ Configuration:
├─ Initial Budget: ${SelfBotConfig.INITIAL_BUDGET:.2f}
├─ Auto Reinvest: {'✅' if SelfBotConfig.AUTO_REINVEST else '❌'}
└─ Scan Interval: {SelfBotConfig.SCAN_INTERVAL}s
"""
            
            await update.message.reply_text(status_text)
            session.close()
            db.close()
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting status: {e}")
    
    async def selfbot_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /selfbot_stats command"""
        user = update.effective_user
        
        if not self.is_owner(user.id):
            await update.message.reply_text("❌ This command is only available to the owner")
            return
        
        try:
            from selfbot.database import SelfBotDatabase
            from selfbot.finance import SelfBotReports
            from selfbot.config import SelfBotConfig
            
            db = SelfBotDatabase(SelfBotConfig.DATABASE_PATH).initialize()
            session = db.get_session()
            reports = SelfBotReports(session)
            
            # Get top performing content types
            top_types = reports.get_top_performing_content_types(limit=3)
            
            stats_text = "📊 SelfBot Performance Stats\n\n"
            stats_text += "🏆 Top Content Types:\n"
            
            for i, (ctype, avg_profit) in enumerate(top_types, 1):
                stats_text += f"{i}. {ctype}: ${avg_profit:.2f} avg profit\n"
            
            await update.message.reply_text(stats_text)
            session.close()
            db.close()
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting stats: {e}")
    
    async def selfbot_report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /selfbot_report command"""
        user = update.effective_user
        
        if not self.is_owner(user.id):
            await update.message.reply_text("❌ This command is only available to the owner")
            return
        
        try:
            from selfbot.database import SelfBotDatabase
            from selfbot.finance import SelfBotReports
            from selfbot.config import SelfBotConfig
            
            db = SelfBotDatabase(SelfBotConfig.DATABASE_PATH).initialize()
            session = db.get_session()
            reports = SelfBotReports(session)
            
            report = reports.generate_cycle_report()
            
            await update.message.reply_text(f"```\n{report}\n```", parse_mode='Markdown')
            session.close()
            db.close()
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error generating report: {e}")
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        # Treat regular messages as AI queries
        user = update.effective_user
        question = update.message.text
        
        context.args = question.split()
        await self.ask_command(update, context)
    
    def run(self):
        """Run the Telegram bot"""
        try:
            Config.validate()
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            return
        
        # Create application
        application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("ask", self.ask_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("report", self.report_command))
        application.add_handler(CommandHandler("settings", self.settings_command))
        
        # SelfBot handlers
        application.add_handler(CommandHandler("selfbot", self.selfbot_command))
        application.add_handler(CommandHandler("selfbot_status", self.selfbot_status_command))
        application.add_handler(CommandHandler("selfbot_stats", self.selfbot_stats_command))
        application.add_handler(CommandHandler("selfbot_report", self.selfbot_report_command))
        
        application.add_handler(CallbackQueryHandler(self.button_callback))
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.message_handler
        ))
        
        logger.info("🤖 Telegram bot starting...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    bot = TelegramBot()
    bot.run()
