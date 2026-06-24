"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
DOKU Payment Service
Service layer for DOKU payment gateway integration
"""

import logging
import uuid
import json
import hmac
import hashlib
import base64
import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Tuple
from flask import current_app

from models import db, User, UserCoins, CoinTransaction, UserPoints, PointTransaction, PaymentSession
from config.doku_config import doku_config, PAYMENT_METHODS, PAYMENT_STATUS_MAPPING
from celery_app.circuit_breaker import get_payment_circuit_breaker, CircuitBreakerOpenException

logger = logging.getLogger(__name__)

class DOKUPaymentService:
    """Service for handling DOKU payment operations"""
    
    def __init__(self):
        self.config = doku_config
    
    def create_checkout_payment(self,
                              user_id: int,
                              amount: float,
                              payment_type: str,
                              description: str = "",
                              payment_methods: Optional[list] = None,
                              return_url: Optional[str] = None,
                              coins_to_deliver: Optional[int] = None,
                              package_id: Optional[int] = None) -> Dict[str, Any]:
        """Create DOKU Checkout payment session"""
        try:
            # Reload configuration from database to get latest settings
            self.config._load_from_database()
            
            # Check if DOKU is configured
            if not self.config.is_configured():
                return {
                    'success': False,
                    'message': 'DOKU payment gateway is not configured. Please contact administrator.'
                }
            
            # Get user information
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Generate unique order ID
            order_id = self._generate_order_id(payment_type, user_id)
            
            # Create payment request
            # Handle user name and email with proper fallbacks
            customer_name = user.username  # Use username as primary name
            if user.first_name or user.last_name:
                name_parts = [part for part in [user.first_name, user.last_name] if part]
                if name_parts:
                    customer_name = " ".join(name_parts)
            
            customer_email = user.email or f"{user.username}@example.com"  # Provide fallback email
            
            payment_request = self.config.create_payment_request(
                amount=amount,
                order_id=order_id,
                customer_name=customer_name,
                customer_email=customer_email,
                description=description,
                payment_methods=payment_methods,
                return_url=return_url
            )
            
            # Log the payment request for debugging
            logger.info(f"DOKU Payment Request: {json.dumps(payment_request, indent=2)}")
            
            # Make API request to DOKU
            response = self.config.make_api_request(
                endpoint='checkout_token',
                method='POST',
                data=payment_request
            )
            
            # Store payment session in database
            payment_session = self._store_payment_session(
                user_id=user_id,
                order_id=order_id,
                amount=amount,
                payment_type=payment_type,
                description=description,
                doku_response=response,
                coins_to_deliver=coins_to_deliver,
                package_id=package_id
            )
            
            logger.info(f"DOKU Checkout payment created for user {user_id}, order {order_id}")
            
            return {
                'success': True,
                'payment_url': response.get('response', {}).get('payment', {}).get('url'),
                'order_id': order_id,
                'payment_session_id': payment_session.id,
                'amount': amount,
                'currency': self.config.default_currency
            }
            
        except Exception as e:
            logger.error(f"Failed to create DOKU checkout payment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_direct_payment(self,
                            user_id: int,
                            amount: float,
                            payment_type: str,
                            payment_method: str,
                            description: str = "") -> Dict[str, Any]:
        """Create DOKU Direct API payment"""
        try:
            # Reload configuration from database to get latest settings
            self.config._load_from_database()
            
            # Check if DOKU is configured
            if not self.config.is_configured():
                return {
                    'success': False,
                    'message': 'DOKU payment gateway is not configured. Please contact administrator.'
                }
            
            # Get user information
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Validate payment method
            if payment_method not in PAYMENT_METHODS:
                raise ValueError(f"Unsupported payment method: {payment_method}")
            
            # Generate unique order ID
            order_id = self._generate_order_id(payment_type, user_id)
            
            # Create payment request
            payment_request = self.config.create_direct_payment_request(
                amount=amount,
                order_id=order_id,
                customer_name=f"{user.first_name} {user.last_name}".strip() or user.username,
                customer_email=user.email,
                payment_method=PAYMENT_METHODS[payment_method],
                description=description
            )
            
            # Make API request to DOKU
            response = self.config.make_api_request(
                endpoint='direct_payment',
                method='POST',
                data=payment_request
            )
            
            # Store payment session in database
            payment_session = self._store_payment_session(
                user_id=user_id,
                order_id=order_id,
                amount=amount,
                payment_type=payment_type,
                description=description,
                doku_response=response,
                payment_method=payment_method
            )
            
            logger.info(f"DOKU Direct payment created for user {user_id}, order {order_id}")
            
            return {
                'success': True,
                'payment_data': response,
                'order_id': order_id,
                'payment_session_id': payment_session.id,
                'amount': amount,
                'currency': self.config.default_currency
            }
            
        except Exception as e:
            logger.error(f"Failed to create DOKU direct payment: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_payment_status(self, order_id: str, force_check: bool = False) -> Dict[str, Any]:
        """Check payment status from DOKU using correct API endpoint"""
        try:
            # Get payment session to check timing
            payment_session = self._get_payment_session(order_id)
            if payment_session:
                # Check if enough time has passed since payment creation (DOKU recommends 60 seconds)
                from datetime import datetime, timezone
                time_since_creation = datetime.now(timezone.utc) - payment_session.created_at.replace(tzinfo=timezone.utc)
                if not force_check and time_since_creation.total_seconds() < 60:
                    remaining_seconds = 60 - int(time_since_creation.total_seconds())
                    return {
                        'success': False,
                        'error': f'Please wait {remaining_seconds} more seconds before checking status',
                        'wait_seconds': remaining_seconds,
                        'status': 'waiting'
                    }

            # Reload configuration from database to get latest settings
            self.config._load_from_database()

            # Check if DOKU is configured
            if not self.config.is_configured():
                return {
                    'success': False,
                    'error': 'DOKU is not configured'
                }

            # Use the correct endpoint with invoice_number in URL path
            # The endpoint is /orders/v1/status/{invoice_number} so we need to construct the full URL
            status_url = f"{self.config.endpoints['check_status']}/{order_id}"

            # For GET requests, we need to pass empty data dict and handle URL differently
            headers = self.config.get_headers()

            # Generate signature for GET request (no digest needed for GET)
            request_id = self.config._generate_request_id()
            timestamp = self.config._get_timestamp()

            # For GET requests, string to sign doesn't include digest
            string_to_sign = f"Client-Id:{self.config.client_id}\nRequest-Id:{request_id}\nRequest-Timestamp:{timestamp}\nRequest-Target:{status_url.replace(self.config.base_url, '')}"
            signature_bytes = hmac.new(
                self.config.secret_key.encode('utf-8'),
                string_to_sign.encode('utf-8'),
                hashlib.sha256
            ).digest()
            signature = base64.b64encode(signature_bytes).decode('utf-8')

            headers.update({
                'Request-Id': request_id,
                'Request-Timestamp': timestamp,
                'Signature': f"HMACSHA256={signature}"
            })

            # Get circuit breaker
            circuit_breaker = get_payment_circuit_breaker()

            def _make_status_request():
                """Make GET request to DOKU status API"""
                response = requests.get(status_url, headers=headers, timeout=30)
                response.raise_for_status()
                return response.json()

            # Execute request through circuit breaker
            response = circuit_breaker.call(_make_status_request)

            logger.info(f"DOKU status check raw response for {order_id}: {response}")

            # Parse the response according to DOKU's format
            # Response structure varies by payment method, but always contains transaction.status
            transaction_status = response.get('transaction', {}).get('status', 'UNKNOWN')
            order_status = response.get('order', {}).get('status', 'UNKNOWN')

            logger.info(f"DOKU status check parsed - transaction: {transaction_status}, order: {order_status}")

            # Use transaction status as primary, order status as fallback
            final_status = transaction_status if transaction_status != 'UNKNOWN' else order_status

            # Map DOKU status to our internal status
            mapped_status = PAYMENT_STATUS_MAPPING.get(final_status, 'unknown')

            # Fallback mapping for partial matches
            if mapped_status == 'unknown':
                final_status_lower = final_status.lower()
                if 'success' in final_status_lower or 'paid' in final_status_lower or 'completed' in final_status_lower:
                    mapped_status = 'completed'
                elif 'cancel' in final_status_lower or 'cancelled' in final_status_lower:
                    mapped_status = 'cancelled'
                elif 'fail' in final_status_lower or 'failed' in final_status_lower:
                    mapped_status = 'failed'
                elif 'expire' in final_status_lower or 'expired' in final_status_lower:
                    mapped_status = 'expired'
                elif 'pending' in final_status_lower or 'waiting' in final_status_lower:
                    mapped_status = 'pending'

            logger.info(f"DOKU status check for order {order_id}: final_status='{final_status}' -> mapped='{mapped_status}'")

            # Debug: Log what status DOKU actually returned if still unknown
            if mapped_status == 'unknown':
                logger.warning(f"DOKU returned unmapped status '{final_status}' for order {order_id}. transaction='{transaction_status}', order='{order_status}'. Full response: {response}")

            # Update payment session status if it's different from what we have
            payment_session = self._get_payment_session(order_id)
            if payment_session and payment_session.status != mapped_status:
                logger.info(f"Updating payment session {order_id} status from {payment_session.status} to {mapped_status}")
                try:
                    self._update_payment_status(payment_session, mapped_status, response)
                except Exception as update_error:
                    logger.error(f"Failed to update payment session status: {str(update_error)}")

            # 🔄 CRITICAL FIX: Auto-process completed payments if webhook was missed
            if mapped_status == 'completed' and payment_session and not payment_session.processed_at:
                logger.warning(f"⚠️ PAYMENT {order_id} COMPLETED BUT WEBHOOK MISSED - AUTO-PROCESSING NOW")
                try:
                    # Double-check that this payment hasn't been processed before
                    if payment_session.status != 'completed' or not payment_session.notification_received:
                        self._process_successful_payment(payment_session, response)
                        logger.info(f"✅ AUTO-PROCESSED: Payment {order_id} - coins delivered via status check")
                    else:
                        logger.info(f"ℹ️ Payment {order_id} already processed, skipping duplicate processing")
                except Exception as process_error:
                    logger.error(f"❌ AUTO-PROCESS FAILED for {order_id}: {str(process_error)}", exc_info=True)
                    # Don't fail the status check if processing fails - it can be retried

            # 🔄 Handle failed payments - mark as processed but don't deliver coins
            elif mapped_status in ['failed', 'cancelled', 'expired'] and payment_session and not payment_session.processed_at:
                logger.warning(f"⚠️ PAYMENT {order_id} {mapped_status.upper()} - MARKING AS PROCESSED WITHOUT COIN DELIVERY")
                try:
                    # Just mark as processed to prevent it from showing as pending forever
                    payment_session.processed_at = datetime.now(timezone.utc)
                    db.session.commit()
                    logger.info(f"✅ MARKED {mapped_status.upper()}: Payment {order_id} - no coins delivered")
                except Exception as process_error:
                    logger.error(f"❌ FAILED TO MARK PAYMENT AS PROCESSED: {order_id}: {str(process_error)}", exc_info=True)

            return {
                'success': True,
                'status': mapped_status,
                'doku_status': transaction_status,
                'payment_data': response,
                'order_id': order_id
            }

        except CircuitBreakerOpenException as e:
            logger.error(f"DOKU status check circuit breaker open: {e}")
            return {
                'success': False,
                'error': f"DOKU service temporarily unavailable: {e}"
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"DOKU status check API error: {str(e)}")
            return {
                'success': False,
                'error': f"DOKU API request failed: {str(e)}"
            }

        except Exception as e:
            logger.error(f"Failed to check DOKU payment status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def handle_notification(self, notification_data: Dict[str, Any], signature: str, timestamp: str) -> Dict[str, Any]:
        """Handle DOKU payment notification with proper status parsing"""
        try:
            # Verify notification signature
            import json
            request_body = json.dumps(notification_data, sort_keys=True)
            if not self.config.verify_notification_signature(request_body, signature, timestamp):
                logger.warning("Invalid DOKU notification signature")
                return {'success': False, 'error': 'Invalid signature'}

            # Extract order ID - try multiple possible locations
            order_id = None
            if 'order' in notification_data and 'invoice_number' in notification_data['order']:
                order_id = notification_data['order']['invoice_number']
            elif 'invoice_number' in notification_data:
                order_id = notification_data['invoice_number']
            elif 'order_id' in notification_data:
                order_id = notification_data['order_id']

            if not order_id:
                logger.warning("Missing order ID in DOKU notification")
                logger.debug(f"Notification data: {notification_data}")
                return {'success': False, 'error': 'Missing order ID'}

            # Extract status - handle different notification formats
            # Standard format: transaction.status
            # QRIS format: TXNSTATUS (S for Success, F for Failed)
            # Fallback: direct status field
            status = None
            doku_raw_status = None

            if 'transaction' in notification_data and 'status' in notification_data['transaction']:
                # Standard DOKU notification format
                doku_raw_status = notification_data['transaction']['status']
            elif 'TXNSTATUS' in notification_data:
                # QRIS specific format
                txn_status = notification_data['TXNSTATUS']
                if txn_status == 'S':
                    doku_raw_status = 'SUCCESS'
                elif txn_status == 'F':
                    doku_raw_status = 'FAILED'
                else:
                    doku_raw_status = 'UNKNOWN'
            elif 'status' in notification_data:
                # Fallback
                doku_raw_status = notification_data['status']
            else:
                logger.warning(f"No status found in notification for order {order_id}")
                logger.debug(f"Notification data: {notification_data}")
                return {'success': False, 'error': 'Missing status in notification'}

            # Map DOKU status to our internal status
            status = PAYMENT_STATUS_MAPPING.get(doku_raw_status, 'unknown')

            logger.info(f"DOKU notification for order {order_id}: raw_status={doku_raw_status}, mapped_status={status}")

            # Get payment session from database
            payment_session = self._get_payment_session(order_id)
            if not payment_session:
                logger.warning(f"Payment session not found for order {order_id}")
                return {'success': False, 'error': 'Payment session not found'}

            # Update payment status
            self._update_payment_status(payment_session, status, notification_data)

            # Process payment if successful - but only if not already processed
            if status == 'completed':
                # Check if payment was already processed to prevent double delivery
                if payment_session.status == 'completed' and payment_session.notification_received:
                    logger.warning(f"Payment {order_id} already processed, skipping duplicate processing")
                    return {'success': True, 'processed': True, 'order_id': order_id, 'status': status, 'duplicate': True}

                self._process_successful_payment(payment_session, notification_data)

            logger.info(f"DOKU notification processed for order {order_id}, status: {status} (raw: {doku_raw_status})")

            return {'success': True, 'processed': True, 'order_id': order_id, 'status': status}

        except Exception as e:
            logger.error(f"Failed to handle DOKU notification: {str(e)}")
            logger.debug(f"Notification data that caused error: {notification_data}")
            return {'success': False, 'error': str(e)}
    
    def _generate_order_id(self, payment_type: str, user_id: int) -> str:
        """Generate unique order ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = str(uuid.uuid4())[:8]
        return f"LYL-{payment_type.upper()}-{user_id}-{timestamp}-{random_suffix}"
    
    def _store_payment_session(self,
                             user_id: int,
                             order_id: str,
                             amount: float,
                             payment_type: str,
                             description: str,
                             doku_response: Dict[str, Any],
                             payment_method: Optional[str] = None,
                             coins_to_deliver: Optional[int] = None,
                             package_id: Optional[int] = None) -> PaymentSession:
        """Store payment session in database"""
        try:
            # Create PaymentSession record
            payment_session = PaymentSession(
                user_id=user_id,
                order_id=order_id,
                amount=amount,
                payment_type=payment_type,
                description=description,
                payment_method=payment_method,
                coins_to_deliver=coins_to_deliver,
                package_id=package_id,
                provider_response=doku_response,
                payment_url=doku_response.get('response', {}).get('payment', {}).get('url'),
                expires_at=datetime.now(timezone.utc).replace(second=0, microsecond=0) + timedelta(seconds=self.config.payment_timeout)
            )
            
            db.session.add(payment_session)
            db.session.commit()
            
            return payment_session
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to store payment session: {str(e)}")
            raise
    
    def _get_payment_session(self, order_id: str) -> Optional[PaymentSession]:
        """Get payment session from database"""
        try:
            payment_session = PaymentSession.query.filter_by(order_id=order_id).first()
            return payment_session
            
        except Exception as e:
            logger.error(f"Failed to get payment session: {str(e)}")
            return None
    
    def _update_payment_status(self, payment_session: PaymentSession, status: str, notification_data: Dict[str, Any]):
        """Update payment status in database"""
        try:
            # Update payment session status
            new_status = PAYMENT_STATUS_MAPPING.get(status, 'unknown')
            payment_session.update_status(
                new_status=new_status,
                notification_data=notification_data,
                provider_transaction_id=notification_data.get('transaction', {}).get('id')
            )
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update payment status: {str(e)}")
            raise
    
    def _process_successful_payment(self, payment_session: PaymentSession, notification_data: Dict[str, Any]):
        """Process successful payment and update user wallet/points"""
        try:
            user_id = payment_session.user_id
            amount = float(payment_session.amount)
            payment_type = payment_session.payment_type

            # Get user
            user = User.query.get(user_id)
            if not user:
                logger.error(f"User {user_id} not found for payment processing")
                return

            logger.info(f"Processing {payment_type} payment for user {user_id}, amount: {amount}")

            # Process based on payment type with transaction safety
            try:
                if payment_type == 'coin_purchase':
                    self._process_coin_purchase(user, amount, payment_session)
                elif payment_type == 'premium_subscription':
                    self._process_premium_subscription(user, amount, payment_session)
                elif payment_type == 'content_purchase':
                    self._process_content_purchase(user, amount, payment_session)
                else:
                    logger.warning(f"Unknown payment type: {payment_type}")
                    return

                # Mark payment as processed to prevent double processing
                payment_session.processed_at = datetime.now(timezone.utc)
                db.session.commit()

                logger.info(f"✅ Successfully processed {payment_type} payment for user {user_id}")

            except Exception as processing_error:
                db.session.rollback()
                logger.error(f"❌ Failed to process {payment_type} payment for user {user_id}: {str(processing_error)}")
                # Re-raise to maintain error handling flow
                raise processing_error

        except Exception as e:
            logger.error(f"❌ Critical error in payment processing: {str(e)}")
            # Don't re-raise here as it's handled at caller level
            raise
    
    def _process_coin_purchase(self, user: User, amount: float, payment_session: PaymentSession):
        """Process coin purchase payment"""
        try:
            # Use stored coins_to_deliver if available, otherwise calculate from amount
            coins_to_add = payment_session.coins_to_deliver
            if coins_to_add is None:
                # Fallback: Calculate coins based on amount (e.g., 1 coin = 100 IDR)
                coins_to_add = int(amount / 100)  # Adjust rate as needed
                logger.warning(f"No coins_to_deliver stored for payment {payment_session.order_id}, using calculated amount: {coins_to_add}")
            else:
                logger.info(f"Delivering {coins_to_add} coins from stored coins_to_deliver for payment {payment_session.order_id}")
            
            # Get or create user coins record
            user_coins = UserCoins.query.filter_by(user_id=user.id).first()
            if not user_coins:
                user_coins = UserCoins(user_id=user.id)
                db.session.add(user_coins)
            
            # Add coins
            user_coins.add_coins(
                coins=coins_to_add,
                coin_type='topup',
                source='doku_payment',
                description=f'Coin purchase via DOKU - {coins_to_add} coins',
                context_data={
                    'payment_session_id': payment_session.id,
                    'order_id': payment_session.order_id,
                    'amount_paid': amount
                },
                payment_provider='doku',
                payment_id=payment_session.order_id,
                amount_paid=amount,
                currency='IDR'
            )
            
            db.session.commit()
            
            logger.info(f"Added {coins_to_add} coins to user {user.id} via DOKU payment")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to process coin purchase: {str(e)}")
            raise
    
    def _process_premium_subscription(self, user: User, amount: float, payment_session: Dict[str, Any]):
        """Process premium subscription payment"""
        try:
            # Calculate subscription duration based on amount
            # Basic: 50,000 IDR = 1 month, Premium: 150,000 IDR = 1 month
            if amount >= 150000:
                duration_days = 30  # 1 month premium
                subscription_type = 'premium'
            elif amount >= 50000:
                duration_days = 30  # 1 month basic
                subscription_type = 'basic'
            else:
                duration_days = 7  # 1 week trial
                subscription_type = 'trial'
            
            # Update user premium access
            from datetime import timedelta
            from models import UserSubscription
            
            start_date = datetime.now(timezone.utc)
            end_date = start_date + timedelta(days=duration_days)
            
            # Create subscription record
            subscription = UserSubscription(
                user_id=user.id,
                subscription_type=subscription_type,
                status='active',
                start_date=start_date,
                end_date=end_date,
                payment_provider='doku',
                payment_id=payment_session.order_id,
                amount=amount,
                currency='IDR',
                auto_renew=False
            )
            
            db.session.add(subscription)
            
            # Update user premium access
            user.has_premium_access = True
            user.premium_expires_at = end_date
            
            db.session.commit()
            
            logger.info(f"Activated {subscription_type} subscription for user {user.id} via DOKU payment")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to process premium subscription: {str(e)}")
            raise
    
    def _process_content_purchase(self, user: User, amount: float, payment_session: Dict[str, Any]):
        """Process content purchase payment"""
        try:
            # Add points to user account
            points_to_add = int(amount / 100)  # 1 point per 100 IDR
            
            # Get or create user points record
            user_points = UserPoints.query.filter_by(user_id=user.id).first()
            if not user_points:
                user_points = UserPoints(user_id=user.id)
                db.session.add(user_points)
            
            # Add points
            leveled_up = user_points.add_points(
                points=points_to_add,
                source='doku_payment',
                description=f'Content purchase via DOKU - {points_to_add} points',
                context_data={
                    'payment_session_id': payment_session.id,
                    'order_id': payment_session.order_id,
                    'amount_paid': amount
                }
            )
            
            db.session.commit()
            
            logger.info(f"Added {points_to_add} points to user {user.id} via DOKU payment")
            
            # Handle level up notification if applicable
            if leveled_up:
                logger.info(f"User {user.id} leveled up to level {user_points.current_level}")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to process content purchase: {str(e)}")
            raise

# Global instance
doku_service = DOKUPaymentService()
