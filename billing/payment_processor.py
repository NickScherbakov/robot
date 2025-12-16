"""
Payment processing module for the Earning Robot.
Integrates with Stripe for payment processing.
"""
import stripe
from backend.config import Config
from backend.database import Transaction
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Initialize Stripe
if Config.STRIPE_SECRET_KEY:
    stripe.api_key = Config.STRIPE_SECRET_KEY


class PaymentProcessor:
    """Handles payment processing operations"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def create_subscription(self, user, email):
        """
        Create a monthly subscription for a user
        
        Args:
            user: User object
            email: Customer email
            
        Returns:
            Stripe checkout session URL
        """
        try:
            # Create or retrieve customer
            customer = stripe.Customer.create(
                email=email,
                metadata={'user_id': user.id}
            )
            
            # Create checkout session for subscription
            session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Monthly AI Robot Subscription',
                            'description': 'Access to AI-powered task automation'
                        },
                        'unit_amount': int(Config.SUBSCRIPTION_MONTHLY_PRICE * 100),
                        'recurring': {
                            'interval': 'month'
                        }
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url='https://example.com/success',
                cancel_url='https://example.com/cancel',
            )
            
            return session.url
            
        except Exception as e:
            logger.error(f"Subscription creation error: {e}")
            raise
    
    def create_micro_payment(self, user, description="AI Task Processing"):
        """
        Create a one-time micro-payment
        
        Args:
            user: User object
            description: Payment description
            
        Returns:
            Stripe checkout session URL
        """
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': description,
                        },
                        'unit_amount': int(Config.MICRO_PAYMENT_PRICE * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='https://example.com/success',
                cancel_url='https://example.com/cancel',
                metadata={'user_id': user.id}
            )
            
            return session.url
            
        except Exception as e:
            logger.error(f"Micro-payment creation error: {e}")
            raise
    
    def record_income(self, amount, category, description, user_id=None, external_id=None):
        """
        Record an income transaction
        
        Args:
            amount: Transaction amount
            category: Transaction category
            description: Transaction description
            user_id: Associated user ID
            external_id: External payment provider ID
        """
        transaction = Transaction(
            user_id=user_id,
            transaction_type='income',
            category=category,
            amount=amount,
            description=description,
            payment_provider='stripe',
            external_id=external_id,
            status='completed'
        )
        
        self.db.add(transaction)
        self.db.commit()
        
        logger.info(f"Income recorded: ${amount} - {description}")
        return transaction
    
    def record_expense(self, amount, category, description):
        """
        Record an expense transaction
        
        Args:
            amount: Transaction amount
            category: Transaction category
            description: Transaction description
        """
        transaction = Transaction(
            transaction_type='expense',
            category=category,
            amount=amount,
            description=description,
            status='completed'
        )
        
        self.db.add(transaction)
        self.db.commit()
        
        logger.info(f"Expense recorded: ${amount} - {description}")
        return transaction
    
    def handle_webhook(self, payload, sig_header):
        """
        Handle Stripe webhook events
        
        Args:
            payload: Webhook payload
            sig_header: Stripe signature header
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, Config.STRIPE_WEBHOOK_SECRET
            )
            
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                self._handle_successful_payment(session)
            
            elif event['type'] == 'invoice.paid':
                invoice = event['data']['object']
                self._handle_subscription_payment(invoice)
            
            elif event['type'] == 'invoice.payment_failed':
                invoice = event['data']['object']
                self._handle_payment_failure(invoice)
                
            return True
            
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return False
    
    def _handle_successful_payment(self, session):
        """Handle successful payment from checkout session"""
        user_id = session.get('metadata', {}).get('user_id')
        amount = session['amount_total'] / 100
        
        self.record_income(
            amount=amount,
            category='micro_payment',
            description='One-time payment',
            user_id=user_id,
            external_id=session['id']
        )
    
    def _handle_subscription_payment(self, invoice):
        """Handle successful subscription payment"""
        customer_id = invoice['customer']
        amount = invoice['amount_paid'] / 100
        
        self.record_income(
            amount=amount,
            category='subscription',
            description='Monthly subscription',
            external_id=invoice['id']
        )
    
    def _handle_payment_failure(self, invoice):
        """Handle failed payment"""
        logger.warning(f"Payment failed for invoice: {invoice['id']}")
