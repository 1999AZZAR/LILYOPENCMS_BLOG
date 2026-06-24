"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Enhanced Wallet Service
Comprehensive coin and wallet management with audit trails, security, and integrations
Robust coin system with bronze coin management and expiration features
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from models import db, User, UserCoins, CoinTransaction, CoinPackage, PaymentSession, UserAchievement, Achievement, PricingConfig, BronzeCoinExpiry, CoinSystemConfig
from flask import current_app
import json
import hashlib
import time
from functools import wraps

logger = logging.getLogger(__name__)

class WalletService:
    """Enhanced wallet service with comprehensive coin management"""

    # Bronze coin management configuration
    BRONZE_COIN_EXPIRY_DAYS = 365  # 1 year expiry like Play Store
    BRONZE_COIN_ENABLED_KEY = 'bronze_coins_enabled'
    BRONZE_COIN_EXPIRY_ENABLED_KEY = 'bronze_coin_expiry_enabled'

    # Rate limiting configuration
    RATE_LIMIT_REQUESTS = 100  # requests per window
    RATE_LIMIT_WINDOW = 3600   # 1 hour in seconds
    RATE_LIMIT_CACHE_TTL = 3600

    @staticmethod
    def get_user_wallet(user_id: int) -> Dict:
        """Get comprehensive user wallet information"""
        try:
            user_coins = UserCoins.query.filter_by(user_id=user_id).first()
            
            if not user_coins:
                # Create wallet if it doesn't exist
                user_coins = WalletService.create_user_wallet(user_id)
            
            # Get recent transactions
            recent_transactions = CoinTransaction.query.filter_by(user_id=user_id)\
                .order_by(CoinTransaction.created_at.desc())\
                .limit(10).all()
            
            # Get user info
            user = User.query.get(user_id)
            
            return {
                'success': True,
                'wallet': {
                    'user_id': user_id,
                    'username': user.username if user else 'Unknown',
                    'bronze_coins': int(user_coins.bronze_coins or 0),
                    'gold_coins': int(user_coins.gold_coins or 0),
                    # Backward compatibility
                    'achievement_coins': int(user_coins.achievement_coins or 0),
                    'topup_coins': int(user_coins.topup_coins or 0),
                    'total_coins': user_coins.get_total_coins(),
                    'total_bronze_earned': int(user_coins.total_bronze_coins_earned or 0),
                    'total_gold_purchased': int(user_coins.total_gold_coins_purchased or 0),
                    # Backward compatibility - use different key names to avoid conflicts
                    'total_achievement_earned': int(user_coins.total_achievement_coins_earned or 0),
                    'total_topup_purchased': int(user_coins.total_topup_coins_purchased or 0),
                    'total_coins_spent': int(user_coins.total_coins_spent or 0),
                    'created_at': user_coins.created_at.isoformat() if user_coins.created_at else None,
                    'updated_at': user_coins.updated_at.isoformat() if user_coins.updated_at else None
                },
                'recent_transactions': [
                    WalletService.format_transaction(transaction) 
                    for transaction in recent_transactions
                ],
                'user_info': {
                    'is_premium': user.is_premium if user else False,
                    'has_premium_access': user.has_premium_access if user else False,
                    'premium_expires_at': user.premium_expires_at.isoformat() if user and user.premium_expires_at else None
                }
            }
        except Exception as e:
            logger.error(f"Error getting user wallet for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to retrieve wallet information'
            }
    
    @staticmethod
    def create_user_wallet(user_id: int) -> UserCoins:
        """Create a new user wallet"""
        try:
            user_coins = UserCoins(user_id=user_id)
            db.session.add(user_coins)
            db.session.commit()
            
            # Log wallet creation
            WalletService.log_transaction(
                user_id=user_id,
                coin_type='system',
                coins_change=0,
                source='wallet_creation',
                description='User wallet created',
                context_data={'action': 'wallet_creation'}
            )
            
            logger.info(f"Created new wallet for user {user_id}")
            return user_coins
            
        except Exception as e:
            logger.error(f"Error creating wallet for user {user_id}: {str(e)}")
            db.session.rollback()
            raise
    
    @staticmethod
    def add_coins(user_id: int, coins: int, coin_type: str, source: str, 
                  description: str = None, context_data: Dict = None,
                  payment_provider: str = None, payment_id: str = None, 
                  amount_paid: Decimal = None, currency: str = 'IDR') -> Dict:
        """Add coins to user wallet with comprehensive logging"""
        try:
            if coins <= 0:
                return {
                    'success': False,
                    'error': 'Invalid coin amount'
                }
            
            user_coins = UserCoins.query.filter_by(user_id=user_id).first()
            if not user_coins:
                user_coins = WalletService.create_user_wallet(user_id)
            
            # Validate coin type
            if coin_type not in ['achievement', 'topup', 'bonus', 'refund', 'admin_grant', 'bronze', 'gold']:
                return {
                    'success': False,
                    'error': 'Invalid coin type'
                }
            
            # Add coins
            success = user_coins.add_coins(
                coins=coins,
                coin_type=coin_type,
                source=source,
                description=description,
                context_data=context_data,
                payment_provider=payment_provider,
                payment_id=payment_id,
                amount_paid=amount_paid,
                currency=currency
            )
            
            if success:
                db.session.commit()
                
                # Log the transaction
                WalletService.log_transaction(
                    user_id=user_id,
                    coin_type=coin_type,
                    coins_change=coins,
                    source=source,
                    description=description or f"Added {coins} {coin_type} coins",
                    context_data=context_data,
                    payment_provider=payment_provider,
                    payment_id=payment_id,
                    amount_paid=amount_paid,
                    currency=currency
                )
                
                logger.info(f"Successfully added {coins} {coin_type} coins to user {user_id}")
                
                return {
                    'success': True,
                    'coins_added': coins,
                    'coin_type': coin_type,
                    'new_balance': user_coins.get_total_coins(),
                    'message': f'Successfully added {coins} coins'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to add coins'
                }
                
        except Exception as e:
            logger.error(f"Error adding coins to user {user_id}: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': 'Failed to add coins'
            }
    
    @staticmethod
    def spend_coins(user_id: int, coins: int, coin_type: str, source: str,
                    description: str = None, context_data: Dict = None) -> Dict:
        """Spend coins from user wallet with validation and logging"""
        try:
            if coins <= 0:
                return {
                    'success': False,
                    'error': 'Invalid coin amount'
                }
            
            user_coins = UserCoins.query.filter_by(user_id=user_id).first()
            if not user_coins:
                return {
                    'success': False,
                    'error': 'User wallet not found'
                }
            
            # Check if user has enough coins
            if not WalletService.can_afford(user_id, coins, coin_type):
                return {
                    'success': False,
                    'error': 'Insufficient coins',
                    'required': coins,
                    'available': user_coins.get_total_coins(),
                    'coin_type': coin_type
                }
            
            # Spend coins
            success = user_coins.spend_coins(
                coins=coins,
                coin_type=coin_type,
                source=source,
                description=description,
                context_data=context_data
            )
            
            if success:
                db.session.commit()
                
                # Log the transaction
                WalletService.log_transaction(
                    user_id=user_id,
                    coin_type=coin_type,
                    coins_change=-coins,  # Negative for spending
                    source=source,
                    description=description or f"Spent {coins} {coin_type} coins",
                    context_data=context_data
                )
                
                logger.info(f"Successfully spent {coins} {coin_type} coins from user {user_id}")
                
                return {
                    'success': True,
                    'coins_spent': coins,
                    'coin_type': coin_type,
                    'new_balance': user_coins.get_total_coins(),
                    'message': f'Successfully spent {coins} coins'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to spend coins'
                }
                
        except Exception as e:
            logger.error(f"Error spending coins from user {user_id}: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': 'Failed to spend coins'
            }
    
    @staticmethod
    def can_afford(user_id: int, required_coins: int, coin_type: str = 'any') -> bool:
        """Check if user can afford the required coins"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            # Premium users bypass coin requirements for most content
            if user.is_premium and coin_type != 'admin_deduction':
                return True
            
            user_coins = UserCoins.query.filter_by(user_id=user_id).first()
            if not user_coins:
                return False
            
            if coin_type == 'achievement':
                return user_coins.bronze_coins >= required_coins
            elif coin_type in ['topup', 'gold']:
                return user_coins.gold_coins >= required_coins
            elif coin_type == 'any':
                return user_coins.get_total_coins() >= required_coins
            elif coin_type == 'admin_deduction':
                # Admin deductions can go negative
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking affordability for user {user_id}: {str(e)}")
            return False
    
    @staticmethod
    def process_payment_success(payment_session_id: str) -> Dict:
        """Process successful payment and add coins to user wallet"""
        try:
            # Get payment session
            payment_session = PaymentSession.query.filter_by(id=payment_session_id).first()
            if not payment_session:
                return {
                    'success': False,
                    'error': 'Payment session not found'
                }
            
            if payment_session.status != 'completed':
                return {
                    'success': False,
                    'error': 'Payment not completed'
                }
            
            # Check if coins already added
            existing_transaction = CoinTransaction.query.filter_by(
                user_id=payment_session.user_id,
                payment_id=payment_session.order_id,
                source='purchase'
            ).first()
            
            if existing_transaction:
                return {
                    'success': False,
                    'error': 'Coins already added for this payment'
                }
            
            # Calculate coins based on package or amount
            coins_to_add = 0
            package_info = None
            
            if payment_session.payment_type == 'coin_purchase':
                # Get package info if available
                package_id = payment_session.context_data.get('package_id') if payment_session.context_data else None
                if package_id:
                    package = CoinPackage.query.get(package_id)
                    if package:
                        coins_to_add = package.total_coins
                        package_info = package.to_dict()
                else:
                    # Fallback to amount-based calculation (100 IDR = 1 coin)
                    coins_to_add = int(float(payment_session.amount) / 100)
            
            if coins_to_add <= 0:
                return {
                    'success': False,
                    'error': 'Invalid coin amount'
                }
            
            # Add coins to user wallet
            result = WalletService.add_coins(
                user_id=payment_session.user_id,
                coins=coins_to_add,
                coin_type='topup',
                source='purchase',
                description=f'Coin purchase - {coins_to_add} coins',
                context_data={
                    'payment_session_id': payment_session_id,
                    'package_id': package_id,
                    'package_info': package_info,
                    'payment_provider': 'doku',
                    'order_id': payment_session.order_id
                },
                payment_provider='doku',
                payment_id=payment_session.order_id,
                amount_paid=Decimal(str(payment_session.amount)),
                currency=payment_session.currency
            )
            
            if result['success']:
                # Update payment session with coin info
                if not payment_session.context_data:
                    payment_session.context_data = {}
                payment_session.context_data.update({
                    'coins_added': coins_to_add,
                    'coin_transaction_id': result.get('transaction_id')
                })
                db.session.commit()
                
                logger.info(f"Successfully processed payment {payment_session_id}: added {coins_to_add} coins to user {payment_session.user_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing payment success for session {payment_session_id}: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': 'Failed to process payment'
            }
    
    @staticmethod
    def get_transaction_history(user_id: int, limit: int = 50, offset: int = 0, 
                               coin_type: str = None, source: str = None) -> Dict:
        """Get user's transaction history with filtering"""
        try:
            query = CoinTransaction.query.filter_by(user_id=user_id)
            
            if coin_type:
                query = query.filter_by(coin_type=coin_type)
            
            if source:
                query = query.filter_by(source=source)
            
            total_count = query.count()
            transactions = query.order_by(CoinTransaction.created_at.desc())\
                .offset(offset).limit(limit).all()
            
            return {
                'success': True,
                'transactions': [WalletService.format_transaction(t) for t in transactions],
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            }
            
        except Exception as e:
            logger.error(f"Error getting transaction history for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to retrieve transaction history'
            }
    
    @staticmethod
    def format_transaction(transaction: CoinTransaction) -> Dict:
        """Format transaction for API response"""
        return {
            'id': transaction.id,
            'coin_type': transaction.coin_type,
            'coins_change': transaction.coins_change,
            'source': transaction.source,
            'description': transaction.description,
            'context_data': transaction.context_data,
            'payment_provider': transaction.payment_provider,
            'payment_id': transaction.payment_id,
            'amount_paid': float(transaction.amount_paid) if transaction.amount_paid else None,
            'currency': transaction.currency,
            'created_at': transaction.created_at.isoformat() if transaction.created_at else None,
            'is_positive': transaction.is_positive,
            'formatted_change': f"{'+' if transaction.coins_change > 0 else ''}{transaction.coins_change}",
            'formatted_amount': f"{transaction.amount_paid} {transaction.currency}" if transaction.amount_paid else None
        }
    
    @staticmethod
    def log_transaction(user_id: int, coin_type: str, coins_change: int, 
                       source: str, description: str = None, context_data: Dict = None,
                       payment_provider: str = None, payment_id: str = None,
                       amount_paid: Decimal = None, currency: str = 'IDR'):
        """Log transaction for audit purposes"""
        try:
            # This creates a system-level transaction log
            transaction = CoinTransaction(
                user_id=user_id,
                coin_type=coin_type,
                coins_change=coins_change,
                source=source,
                description=description,
                context_data=context_data,
                payment_provider=payment_provider,
                payment_id=payment_id,
                amount_paid=amount_paid,
                currency=currency
            )
            
            db.session.add(transaction)
            # Note: Don't commit here as it's called within other methods that handle commits
            
        except Exception as e:
            logger.error(f"Error logging transaction for user {user_id}: {str(e)}")
    
    @staticmethod
    def get_wallet_statistics(user_id: int) -> Dict:
        """Get comprehensive wallet statistics"""
        try:
            user_coins = UserCoins.query.filter_by(user_id=user_id).first()
            if not user_coins:
                return {
                    'success': False,
                    'error': 'User wallet not found'
                }
            
            # Get transaction counts by type
            transaction_stats = db.session.query(
                CoinTransaction.coin_type,
                CoinTransaction.source,
                db.func.count(CoinTransaction.id).label('count'),
                db.func.sum(db.case(
                    (CoinTransaction.coins_change > 0, CoinTransaction.coins_change),
                    else_=0
                )).label('total_earned'),
                db.func.sum(db.case(
                    (CoinTransaction.coins_change < 0, db.func.abs(CoinTransaction.coins_change)),
                    else_=0
                )).label('total_spent')
            ).filter_by(user_id=user_id)\
            .group_by(CoinTransaction.coin_type, CoinTransaction.source)\
            .all()
            
            # Get recent activity
            recent_activity = CoinTransaction.query.filter_by(user_id=user_id)\
                .order_by(CoinTransaction.created_at.desc())\
                .limit(10).all()
            
            # Create earning sources dictionary
            earning_sources = {}
            for stat in transaction_stats:
                if stat.total_earned and stat.total_earned > 0:
                    source_key = stat.source.replace(' ', '_').lower()
                    earning_sources[source_key] = int(stat.total_earned)
            
            # Calculate totals
            total_earned = sum(earning_sources.values())
            total_spent = sum(int(stat.total_spent) if stat.total_spent else 0 for stat in transaction_stats)
            total_transactions = sum(stat.count for stat in transaction_stats)
            
            return {
                'success': True,
                'current_balance': user_coins.get_total_coins(),
                'total_earned': total_earned,
                'total_spent': total_spent,
                'total_transactions': total_transactions,
                'earning_sources': earning_sources,
                'wallet_stats': {
                    'current_balance': user_coins.get_total_coins(),
                    'bronze_coins': user_coins.bronze_coins,
                    'gold_coins': user_coins.gold_coins,
                    # Backward compatibility
                    'achievement_coins': user_coins.achievement_coins,
                    'topup_coins': user_coins.topup_coins,
                    'total_bronze_earned': user_coins.total_bronze_coins_earned,
                    'total_gold_purchased': user_coins.total_gold_coins_purchased,
                    # Backward compatibility
                    'total_earned': user_coins.total_achievement_coins_earned,
                    'total_purchased': user_coins.total_topup_coins_purchased,
                    'total_spent': user_coins.total_coins_spent,
                    'wallet_age_days': (datetime.now(timezone.utc) - (user_coins.created_at.replace(tzinfo=timezone.utc) if user_coins.created_at and user_coins.created_at.tzinfo is None else user_coins.created_at)).days if user_coins.created_at else 0
                },
                'transaction_stats': [
                    {
                        'coin_type': stat.coin_type,
                        'source': stat.source,
                        'count': stat.count,
                        'total_earned': int(stat.total_earned) if stat.total_earned else 0,
                        'total_spent': int(stat.total_spent) if stat.total_spent else 0
                    }
                    for stat in transaction_stats
                ],
                'recent_activity': [
                    WalletService.format_transaction(transaction) 
                    for transaction in recent_activity
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting wallet statistics for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to retrieve wallet statistics'
            }
    
    @staticmethod
    def transfer_coins(from_user_id: int, to_user_id: int, coins: int, 
                      coin_type: str = 'any', description: str = None) -> Dict:
        """Transfer coins between users (admin function)"""
        try:
            # Validate input
            if coins <= 0:
                return {
                    'success': False,
                    'error': 'Invalid coin amount'
                }
            
            if from_user_id == to_user_id:
                return {
                    'success': False,
                    'error': 'Cannot transfer to self'
                }
            
            # Check if sender has enough coins
            if not WalletService.can_afford(from_user_id, coins, coin_type):
                return {
                    'success': False,
                    'error': 'Sender has insufficient coins'
                }
            
            # Spend from sender
            spend_result = WalletService.spend_coins(
                user_id=from_user_id,
                coins=coins,
                coin_type=coin_type,
                source='transfer_out',
                description=description or f'Transfer to user {to_user_id}',
                context_data={'transfer_to': to_user_id}
            )
            
            if not spend_result['success']:
                return spend_result
            
            # Add to receiver
            add_result = WalletService.add_coins(
                user_id=to_user_id,
                coins=coins,
                coin_type=coin_type,
                source='transfer_in',
                description=description or f'Transfer from user {from_user_id}',
                context_data={'transfer_from': from_user_id}
            )
            
            if not add_result['success']:
                # Rollback the spend operation
                WalletService.add_coins(
                    user_id=from_user_id,
                    coins=coins,
                    coin_type=coin_type,
                    source='transfer_rollback',
                    description=f'Rollback transfer to user {to_user_id}',
                    context_data={'rollback_for': to_user_id}
                )
                return add_result
            
            return {
                'success': True,
                'coins_transferred': coins,
                'coin_type': coin_type,
                'from_user': from_user_id,
                'to_user': to_user_id,
                'message': f'Successfully transferred {coins} coins'
            }
            
        except Exception as e:
            logger.error(f"Error transferring coins from {from_user_id} to {to_user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to transfer coins'
            }

    # ===== BRONZE COIN MANAGEMENT METHODS =====

    @staticmethod
    def is_bronze_coin_system_enabled() -> bool:
        """Check if bronze coin earning system is enabled"""
        try:
            enabled = CoinSystemConfig.get_config_value(
                WalletService.BRONZE_COIN_ENABLED_KEY,
                True,  # Default to enabled
                'bool'
            )
            return enabled
        except Exception as e:
            logger.error(f"Error checking bronze coin system status: {str(e)}")
            return True  # Default to enabled on error

    @staticmethod
    def set_bronze_coin_system_enabled(enabled: bool, admin_user_id: int = None) -> Dict:
        """Enable or disable the bronze coin earning system"""
        try:
            CoinSystemConfig.set_config_value(
                key=WalletService.BRONZE_COIN_ENABLED_KEY,
                value=enabled,
                config_type='bool',
                description='Enable or disable bronze coin earning system',
                category='bronze_coins',
                created_by=admin_user_id,
                updated_by=admin_user_id
            )

            logger.info(f"Bronze coin system {'enabled' if enabled else 'disabled'}")
            return {
                'success': True,
                'bronze_coins_enabled': enabled,
                'message': f"Bronze coin system {'enabled' if enabled else 'disabled'} successfully"
            }
        except Exception as e:
            logger.error(f"Error setting bronze coin system status: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to update bronze coin system status'
            }

    @staticmethod
    def is_bronze_coin_expiry_enabled() -> bool:
        """Check if bronze coin expiry is enabled"""
        try:
            enabled = CoinSystemConfig.get_config_value(
                WalletService.BRONZE_COIN_EXPIRY_ENABLED_KEY,
                True,  # Default to enabled
                'bool'
            )
            return enabled
        except Exception as e:
            logger.error(f"Error checking bronze coin expiry status: {str(e)}")
            return True  # Default to enabled on error

    @staticmethod
    def set_bronze_coin_expiry_enabled(enabled: bool, admin_user_id: int = None) -> Dict:
        """Enable or disable bronze coin expiration"""
        try:
            CoinSystemConfig.set_config_value(
                key=WalletService.BRONZE_COIN_EXPIRY_ENABLED_KEY,
                value=enabled,
                config_type='bool',
                description='Enable or disable bronze coin expiration (Play Store style)',
                category='expiry',
                created_by=admin_user_id,
                updated_by=admin_user_id
            )

            logger.info(f"Bronze coin expiry {'enabled' if enabled else 'disabled'}")
            return {
                'success': True,
                'bronze_coin_expiry_enabled': enabled,
                'message': f"Bronze coin expiry {'enabled' if enabled else 'disabled'} successfully"
            }
        except Exception as e:
            logger.error(f"Error setting bronze coin expiry status: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to update bronze coin expiry status'
            }

    @staticmethod
    def get_bronze_coin_expiry_days() -> int:
        """Get the bronze coin expiry period in days"""
        try:
            days = CoinSystemConfig.get_config_value(
                'bronze_coin_expiry_days',
                WalletService.BRONZE_COIN_EXPIRY_DAYS,
                'int'
            )
            return max(days, 30)  # Minimum 30 days
        except Exception as e:
            logger.error(f"Error getting bronze coin expiry days: {str(e)}")
            return WalletService.BRONZE_COIN_EXPIRY_DAYS

    @staticmethod
    def set_bronze_coin_expiry_days(days: int, admin_user_id: int = None) -> Dict:
        """Set the bronze coin expiry period"""
        try:
            if days < 30:
                return {
                    'success': False,
                    'error': 'Expiry period must be at least 30 days'
                }

            CoinSystemConfig.set_config_value(
                key='bronze_coin_expiry_days',
                value=days,
                config_type='int',
                description='Bronze coin expiry period in days (Play Store style)',
                category='expiry',
                created_by=admin_user_id,
                updated_by=admin_user_id
            )

            logger.info(f"Bronze coin expiry set to {days} days")
            return {
                'success': True,
                'expiry_days': days,
                'message': f"Bronze coin expiry set to {days} days"
            }
        except Exception as e:
            logger.error(f"Error setting bronze coin expiry days: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to set bronze coin expiry period'
            }

    @staticmethod
    def get_user_bronze_coin_expiry_info(user_id: int) -> Dict:
        """Get detailed information about user's bronze coin expiry status"""
        try:
            user_coins = UserCoins.query.filter_by(user_id=user_id).first()
            if not user_coins:
                return {
                    'success': False,
                    'error': 'User wallet not found'
                }

            expiry_enabled = WalletService.is_bronze_coin_expiry_enabled()
            expiry_days = WalletService.get_bronze_coin_expiry_days()

            if not expiry_enabled:
                return {
                    'success': True,
                    'expiry_enabled': False,
                    'current_balance': user_coins.bronze_coins,
                    'expiring_coins': 0,
                    'next_expiry_date': None,
                    'message': 'Bronze coin expiry is disabled'
                }

            # Get expiring coins information
            expiring_info = WalletService.get_user_expiring_bronze_coins(user_id)

            # Get next expiry date (earliest expiry from unexpired records)
            next_expiry = BronzeCoinExpiry.query.filter(
                BronzeCoinExpiry.user_id == user_id,
                BronzeCoinExpiry.is_expired == False,
                BronzeCoinExpiry.coins_remaining > 0
            ).order_by(BronzeCoinExpiry.expires_at.asc()).first()

            next_expiry_date = next_expiry.expires_at.isoformat() if next_expiry else None

            return {
                'success': True,
                'expiry_enabled': True,
                'expiry_days': expiry_days,
                'current_balance': user_coins.bronze_coins,
                'expiring_coins': expiring_info.get('total_expiring', 0),
                'expiring_within_7_days': expiring_info.get('expiring_within_7_days', 0),
                'expiring_within_30_days': expiring_info.get('expiring_within_30_days', 0),
                'next_expiry_date': next_expiry_date,
                'expiring_records': expiring_info.get('expiring_coins', []),
                'message': f'{expiring_info.get("total_expiring", 0)} bronze coins expiring soon'
            }

        except Exception as e:
            logger.error(f"Error getting bronze coin expiry info for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to get bronze coin expiry information'
            }


    @staticmethod
    def expire_old_bronze_coins(user_id: int = None, batch_size: int = 1000) -> Dict:
        """Expire old bronze coins that have passed the expiry period"""
        try:
            if not WalletService.is_bronze_coin_expiry_enabled():
                return {
                    'success': False,
                    'error': 'Bronze coin expiry is disabled'
                }

            current_time = datetime.now(timezone.utc)
            batch_id = f"expiry_{int(current_time.timestamp())}"

            # Find expired bronze coin records
            query = BronzeCoinExpiry.query.filter(
                BronzeCoinExpiry.is_expired == False,
                BronzeCoinExpiry.expires_at <= current_time,
                BronzeCoinExpiry.coins_remaining > 0
            )

            if user_id:
                query = query.filter(BronzeCoinExpiry.user_id == user_id)

            expired_records = query.limit(batch_size).all()

            total_expired = 0
            processed_users = set()

            for record in expired_records:
                try:
                    coins_to_expire = record.coins_remaining

                    if coins_to_expire > 0:
                        # Mark the record as expired
                        record.mark_expired(batch_id)

                        # Update user's coin balance
                        user_coins = UserCoins.query.filter_by(user_id=record.user_id).first()
                        if user_coins:
                            user_coins.bronze_coins = max(0, user_coins.bronze_coins - coins_to_expire)
                            user_coins.total_bronze_coins_spent += coins_to_expire
                            user_coins.updated_at = current_time

                        # Log the expiry transaction
                        WalletService.log_transaction(
                            user_id=record.user_id,
                            coin_type='bronze',
                            coins_change=-coins_to_expire,
                            source='expiry',
                            description=f'Bronze coins expired after expiry period',
                            context_data={
                                'expiry_record_id': record.id,
                                'batch_id': batch_id,
                                'earned_at': record.earned_at.isoformat(),
                                'expired_at': current_time.isoformat()
                            }
                        )

                        total_expired += coins_to_expire
                        processed_users.add(record.user_id)

                        logger.info(f"Expired {coins_to_expire} bronze coins for user {record.user_id} (record {record.id})")

                except Exception as e:
                    logger.error(f"Error expiring coins for record {record.id}: {str(e)}")
                    continue

            db.session.commit()

            return {
                'success': True,
                'processed_records': len(expired_records),
                'processed_users': len(processed_users),
                'total_coins_expired': total_expired,
                'batch_id': batch_id,
                'message': f'Expired {total_expired} bronze coins across {len(processed_users)} users'
            }

        except Exception as e:
            logger.error(f"Error expiring old bronze coins: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': 'Failed to expire bronze coins'
            }

    # ===== ROBUSTNESS ENHANCEMENTS =====

    @staticmethod
    def _get_rate_limit_key(user_id: int, action: str) -> str:
        """Generate rate limit cache key"""
        today = datetime.now(timezone.utc).date()
        return f"wallet_ratelimit:{user_id}:{action}:{today.isoformat()}"

    @staticmethod
    def check_rate_limit(user_id: int, action: str) -> bool:
        """Check if user has exceeded rate limit for an action"""
        try:
            # Use Redis for rate limiting if available
            if hasattr(current_app, 'redis') and current_app.redis:
                key = WalletService._get_rate_limit_key(user_id, action)
                current_count = current_app.redis.incr(key)

                if current_count == 1:
                    # Set expiry on first request
                    current_app.redis.expire(key, WalletService.RATE_LIMIT_WINDOW)

                return current_count <= WalletService.RATE_LIMIT_REQUESTS
            else:
                # Fallback to in-memory rate limiting (less reliable)
                return True

        except Exception as e:
            logger.error(f"Error checking rate limit for user {user_id}, action {action}: {str(e)}")
            return True  # Allow on error

    @staticmethod
    def validate_coin_operation(user_id: int, coins: int, coin_type: str, operation: str) -> Dict:
        """Validate coin operation parameters and business rules"""
        try:
            # Basic validation
            if not isinstance(coins, int) or coins <= 0:
                return {
                    'valid': False,
                    'error': 'Invalid coin amount. Must be a positive integer.'
                }

            if coin_type not in ['achievement', 'bronze', 'topup', 'gold', 'bonus', 'refund', 'admin_grant']:
                return {
                    'valid': False,
                    'error': f'Invalid coin type: {coin_type}'
                }

            # Check bronze coin system status
            if coin_type in ['achievement', 'bronze']:
                if not WalletService.is_bronze_coin_system_enabled():
                    return {
                        'valid': False,
                        'error': 'Bronze coin system is currently disabled'
                    }

            # Check rate limiting
            if not WalletService.check_rate_limit(user_id, operation):
                return {
                    'valid': False,
                    'error': f'Rate limit exceeded for {operation}. Please try again later.'
                }

            # Check user exists and has wallet
            user = User.query.get(user_id)
            if not user:
                return {
                    'valid': False,
                    'error': 'User not found'
                }

            user_coins = UserCoins.query.filter_by(user_id=user_id).first()
            if not user_coins:
                return {
                    'valid': False,
                    'error': 'User wallet not found'
                }

            # Validate spending operations
            if operation == 'spend' and coin_type in ['achievement', 'bronze']:
                if user_coins.bronze_coins < coins:
                    return {
                        'valid': False,
                        'error': f'Insufficient bronze coins. Available: {user_coins.bronze_coins}, Required: {coins}'
                    }

            elif operation == 'spend' and coin_type in ['topup', 'gold']:
                if user_coins.gold_coins < coins:
                    return {
                        'valid': False,
                        'error': f'Insufficient gold coins. Available: {user_coins.gold_coins}, Required: {coins}'
                    }

            # Validate coin limits
            max_daily_earn = CoinSystemConfig.get_config_value('max_daily_bronze_earn', 100, 'int')
            if operation == 'add' and coin_type in ['bronze', 'achievement'] and coins > max_daily_earn:
                return {
                    'valid': False,
                    'error': f'Cannot earn more than {max_daily_earn} bronze coins per day'
                }

            max_daily_gold_earn = CoinSystemConfig.get_config_value('max_daily_gold_earn', 500, 'int')
            if operation == 'add' and coin_type in ['gold', 'topup'] and coins > max_daily_gold_earn:
                return {
                    'valid': False,
                    'error': f'Cannot earn more than {max_daily_gold_earn} gold coins per day'
                }

            return {'valid': True}

        except Exception as e:
            logger.error(f"Error validating coin operation for user {user_id}: {str(e)}")
            return {
                'valid': False,
                'error': 'Validation failed due to system error'
            }

    @staticmethod
    def audit_wallet_operation(user_id: int, operation: str, coin_type: str, coins: int,
                             old_balance: int, new_balance: int, context: Dict = None) -> None:
        """Create audit trail for wallet operations"""
        try:
            audit_data = {
                'user_id': user_id,
                'operation': operation,
                'coin_type': coin_type,
                'coins': coins,
                'old_balance': old_balance,
                'new_balance': new_balance,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'context': context or {}
            }

            # Store in audit log (could be database table or external service)
            audit_key = f"wallet_audit:{user_id}:{int(time.time())}"
            audit_json = json.dumps(audit_data, default=str)

            # Use Redis for audit storage if available
            if hasattr(current_app, 'redis') and current_app.redis:
                current_app.redis.setex(audit_key, 86400 * 30, audit_json)  # Keep for 30 days

            logger.info(f"Wallet audit: {audit_json}")

        except Exception as e:
            logger.error(f"Error creating wallet audit for user {user_id}: {str(e)}")

    # ===== ENHANCED WALLET METHODS =====

    @staticmethod
    def get_enhanced_user_wallet(user_id: int) -> Dict:
        """Get enhanced user wallet information with expiry and management info"""
        try:
            base_wallet = WalletService.get_user_wallet(user_id)
            if not base_wallet['success']:
                return base_wallet

            # Add bronze coin management information
            bronze_info = WalletService.get_user_bronze_coin_expiry_info(user_id)
            system_status = {
                'bronze_coins_enabled': WalletService.is_bronze_coin_system_enabled(),
                'bronze_coin_expiry_enabled': WalletService.is_bronze_coin_expiry_enabled(),
                'bronze_coin_expiry_days': WalletService.get_bronze_coin_expiry_days()
            }

            # Add rate limiting status
            rate_status = {
                'can_add_coins': WalletService.check_rate_limit(user_id, 'add_coins'),
                'can_spend_coins': WalletService.check_rate_limit(user_id, 'spend_coins')
            }

            enhanced_wallet = base_wallet
            enhanced_wallet['wallet'].update({
                'bronze_coin_info': bronze_info.get('bronze_coin_info', {}),
                'system_status': system_status,
                'rate_limiting': rate_status
            })

            return enhanced_wallet

        except Exception as e:
            logger.error(f"Error getting enhanced wallet for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to retrieve enhanced wallet information'
            }

    @staticmethod
    def add_coins_secure(user_id: int, coins: int, coin_type: str, source: str,
                        description: str = None, context_data: Dict = None,
                        payment_provider: str = None, payment_id: str = None,
                        amount_paid: Decimal = None, currency: str = 'IDR') -> Dict:
        """Secure version of add_coins with validation and audit"""
        try:
            # Validate operation
            validation = WalletService.validate_coin_operation(user_id, coins, coin_type, 'add')
            if not validation['valid']:
                return validation

            # Get old balance for audit
            user_coins = UserCoins.query.filter_by(user_id=user_id).first()
            old_balance = user_coins.get_total_coins()

            # Perform operation
            result = WalletService.add_coins(
                user_id=user_id,
                coins=coins,
                coin_type=coin_type,
                source=source,
                description=description,
                context_data=context_data,
                payment_provider=payment_provider,
                payment_id=payment_id,
                amount_paid=amount_paid,
                currency=currency
            )

            if result['success']:
                # Record expiry information for bronze coins
                if coin_type in ['bronze', 'achievement'] and WalletService.is_bronze_coin_expiry_enabled():
                    try:
                        expiry_record = BronzeCoinExpiry(
                            user_id=user_id,
                            earned_at=datetime.now(timezone.utc),
                            coins_amount=coins,
                            coins_remaining=coins,
                            source=source,
                            context_data=context_data
                        )
                        db.session.add(expiry_record)
                        db.session.commit()
                        logger.info(f"Recorded expiry tracking for {coins} bronze coins for user {user_id}")
                    except Exception as e:
                        logger.error(f"Failed to record bronze coin expiry for user {user_id}: {str(e)}")
                        # Don't fail the operation if expiry recording fails

                # Audit the operation
                WalletService.audit_wallet_operation(
                    user_id=user_id,
                    operation='add_coins',
                    coin_type=coin_type,
                    coins=coins,
                    old_balance=old_balance,
                    new_balance=result['new_balance'],
                    context=context_data
                )

            return result

        except Exception as e:
            logger.error(f"Error in secure add_coins for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Secure coin addition failed'
            }

    @staticmethod
    def spend_coins_secure(user_id: int, coins: int, coin_type: str, source: str,
                          description: str = None, context_data: Dict = None) -> Dict:
        """Secure version of spend_coins with validation and audit"""
        try:
            # Validate operation
            validation = WalletService.validate_coin_operation(user_id, coins, coin_type, 'spend')
            if not validation['valid']:
                return validation

            # Get old balance for audit
            user_coins = UserCoins.query.filter_by(user_id=user_id).first()
            old_balance = user_coins.get_total_coins()

            # Perform operation
            result = WalletService.spend_coins(
                user_id=user_id,
                coins=coins,
                coin_type=coin_type,
                source=source,
                description=description,
                context_data=context_data
            )

            if result['success']:
                # Update expiry tracking for bronze coins (spend from oldest first)
                if coin_type in ['bronze', 'achievement']:
                    try:
                        WalletService._update_bronze_coin_expiry_on_spend(user_id, coins)
                    except Exception as e:
                        logger.error(f"Failed to update bronze coin expiry on spend for user {user_id}: {str(e)}")
                        # Don't fail the operation if expiry update fails

                # Audit the operation
                WalletService.audit_wallet_operation(
                    user_id=user_id,
                    operation='spend_coins',
                    coin_type=coin_type,
                    coins=coins,
                    old_balance=old_balance,
                    new_balance=result['new_balance'],
                    context=context_data
                )

            return result

        except Exception as e:
            logger.error(f"Error in secure spend_coins for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Secure coin spending failed'
            }

    # ===== BRONZE COIN EXPIRY HELPER METHODS =====

    @staticmethod
    def _update_bronze_coin_expiry_on_spend(user_id: int, coins_spent: int) -> None:
        """Update bronze coin expiry records when coins are spent (FIFO - first earned, first spent)"""
        try:
            # Get unexpired bronze coin records ordered by earned date (oldest first)
            expiry_records = BronzeCoinExpiry.query.filter(
                BronzeCoinExpiry.user_id == user_id,
                BronzeCoinExpiry.is_expired == False,
                BronzeCoinExpiry.coins_remaining > 0
            ).order_by(BronzeCoinExpiry.earned_at.asc()).all()

            remaining_to_spend = coins_spent

            for record in expiry_records:
                if remaining_to_spend <= 0:
                    break

                available_coins = record.coins_remaining
                spend_from_this_record = min(available_coins, remaining_to_spend)

                record.coins_remaining -= spend_from_this_record
                record.updated_at = datetime.now(timezone.utc)
                remaining_to_spend -= spend_from_this_record

                logger.debug(f"Spent {spend_from_this_record} coins from expiry record {record.id} for user {user_id}")

            db.session.commit()

        except Exception as e:
            logger.error(f"Error updating bronze coin expiry on spend for user {user_id}: {str(e)}")
            db.session.rollback()

    @staticmethod
    def get_user_expiring_bronze_coins(user_id: int) -> Dict:
        """Get detailed information about user's expiring bronze coins"""
        try:
            if not WalletService.is_bronze_coin_expiry_enabled():
                return {
                    'success': True,
                    'expiry_enabled': False,
                    'expiring_coins': [],
                    'total_expiring': 0
                }

            # Get expiring coins (expiring within 30 days)
            thirty_days_from_now = datetime.now(timezone.utc) + timedelta(days=30)

            expiring_records = BronzeCoinExpiry.query.filter(
                BronzeCoinExpiry.user_id == user_id,
                BronzeCoinExpiry.is_expired == False,
                BronzeCoinExpiry.expires_at <= thirty_days_from_now,
                BronzeCoinExpiry.coins_remaining > 0
            ).order_by(BronzeCoinExpiry.expires_at.asc()).all()

            total_expiring = sum(record.coins_remaining for record in expiring_records)

            return {
                'success': True,
                'expiry_enabled': True,
                'expiring_coins': [record.to_dict() for record in expiring_records],
                'total_expiring': total_expiring,
                'expiring_within_7_days': sum(r.coins_remaining for r in expiring_records if r.days_until_expiry <= 7),
                'expiring_within_30_days': total_expiring
            }

        except Exception as e:
            logger.error(f"Error getting expiring bronze coins for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to get expiring coin information'
            }
