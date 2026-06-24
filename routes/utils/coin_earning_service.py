"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Coin Earning Service
Comprehensive coin earning mechanisms beyond purchases and achievements
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from models import db, User, UserCoins, CoinTransaction, News, Comment, Rating, UserAchievement, Achievement, CoinManager
from routes.utils.wallet_service import WalletService
from routes.utils.achievement_service import AchievementService
import json

logger = logging.getLogger(__name__)

class CoinEarningService:
    """Service for managing various coin earning mechanisms"""
    
    # Coin earning rates and limits
    COIN_RATES = {
        'daily_login': 5,           # 5 coins per day for logging in
        'article_read': 2,          # 2 coins per article read
        'comment_posted': 3,        # 3 coins per comment
        'rating_given': 1,          # 1 coin per rating given
        'share_content': 5,         # 5 coins per share
        'referral_signup': 50,      # 50 coins per successful referral
        'content_contribution': 20, # 20 coins for contributing content
        'streak_bonus': 10,         # 10 coins for maintaining streaks
        'weekly_challenge': 100,    # 100 coins for weekly challenges
        'special_event': 25         # 25 coins for special events
    }
    
    DAILY_LIMITS = {
        'article_read': 50,         # Max 50 coins per day from reading
        'comment_posted': 30,       # Max 30 coins per day from comments
        'rating_given': 20,         # Max 20 coins per day from ratings
        'share_content': 25,        # Max 25 coins per day from sharing
        'daily_login': 5            # Max 5 coins per day from login
    }
    
    @staticmethod
    def award_daily_login_coins(user_id: int) -> Dict:
        """Award coins for daily login"""
        try:
            from models import PricingConfig
            from routes.utils.wallet_service import WalletService

            # Check if achievements and bronze coins are enabled
            achievements_enabled = PricingConfig.get_config_value('achievements_enabled', True)
            bronze_enabled = WalletService.is_bronze_coin_system_enabled()

            if not achievements_enabled:
                return {
                    'success': False,
                    'error': 'Achievement system is disabled',
                    'coins_awarded': 0
                }

            if not bronze_enabled:
                return {
                    'success': False,
                    'error': 'Bronze coin system is disabled',
                    'coins_awarded': 0
                }

            today = datetime.now(timezone.utc).date()

            # Check if user already received login coins today
            existing_transaction = CoinTransaction.query.filter(
                CoinTransaction.user_id == user_id,
                CoinTransaction.source == 'daily_login',
                db.func.date(CoinTransaction.created_at) == today
            ).first()
            
            if existing_transaction:
                return {
                    'success': False,
                    'error': 'Daily login coins already awarded today',
                    'coins_awarded': 0
                }
            
            # Award login coins (bronze coins if achievements enabled)
            coins = CoinEarningService.COIN_RATES['daily_login']
            success, error = CoinManager.add_bronze_coins(
                user_id=user_id,
                coins=coins,
                source='daily_login',
                description='Daily login bonus',
                context_data={'date': today.isoformat()}
            )

            if success:
                # Check for login streak achievements
                AchievementService.check_and_award_achievements(
                    user_id=user_id,
                    activity_type='login_streak',
                    context_data={'daily_login': True}
                )

                return {
                    'success': True,
                    'coins_awarded': coins,
                    'message': f'Daily login bonus: +{coins} coins'
                }
            else:
                return {
                    'success': False,
                    'error': error or 'Failed to award daily login coins'
                }
                
        except Exception as e:
            logger.error(f"Error awarding daily login coins to user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to award daily login coins'
            }
    
    @staticmethod
    def award_article_read_coins(user_id: int, article_id: int) -> Dict:
        """Award coins for reading an article"""
        try:
            from models import PricingConfig
            from routes.utils.wallet_service import WalletService

            # Check if achievements and bronze coins are enabled
            achievements_enabled = PricingConfig.get_config_value('achievements_enabled', True)
            bronze_enabled = WalletService.is_bronze_coin_system_enabled()

            if not achievements_enabled:
                return {
                    'success': False,
                    'error': 'Achievement system is disabled',
                    'coins_awarded': 0
                }

            if not bronze_enabled:
                return {
                    'success': False,
                    'error': 'Bronze coin system is disabled',
                    'coins_awarded': 0
                }

            today = datetime.now(timezone.utc).date()

            # Check if user already received coins for this article (ever, not just today)
            existing_transaction = CoinTransaction.query.filter(
                CoinTransaction.user_id == user_id,
                CoinTransaction.source == 'article_read',
                CoinTransaction.context_data.op('->>')('article_id') == str(article_id),
                CoinTransaction.coins_change > 0
            ).first()
            
            if existing_transaction:
                return {
                    'success': False,
                    'error': 'Coins already awarded for this article',
                    'coins_awarded': 0
                }
            
            # Check daily limit
            daily_earned = CoinEarningService.get_daily_earnings(user_id, 'article_read')
            if daily_earned >= CoinEarningService.DAILY_LIMITS['article_read']:
                return {
                    'success': False,
                    'error': 'Daily article reading limit reached',
                    'coins_awarded': 0
                }
            
            # Award reading coins (bronze coins if achievements enabled)
            coins = CoinEarningService.COIN_RATES['article_read']
            result = WalletService.add_coins_secure(
                user_id=user_id,
                coins=coins,
                coin_type='bronze',
                source='article_read',
                description='Article reading reward',
                context_data={
                    'article_id': article_id,
                    'date': today.isoformat()
                }
            )
            
            if result['success']:
                # Check for achievements
                achievement_result = AchievementService.check_and_award_achievements(
                    user_id, 'article_read', {'article_id': article_id}
                )

                total_coins = coins
                achievement_coins = 0
                if achievement_result['success']:
                    # AchievementService returns points, not coins
                    # We need to convert points to coins or handle separately
                    achievement_coins = achievement_result.get('total_points_earned', 0)

                return {
                    'success': True,
                    'coins_awarded': total_coins,
                    'base_coins': coins,
                    'achievement_coins': achievement_coins,
                    'achievements_awarded': achievement_result.get('awarded_achievements', [])
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error awarding article read coins for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to award article read coins',
                'coins_awarded': 0
            }
    
    @staticmethod
    def award_comment_coins(user_id: int, comment_id: int, article_id: int = None) -> Dict:
        """Award coins for posting a comment"""
        try:
            today = datetime.now(timezone.utc).date()
            
            # Check if user already received coins for this comment (ever, not just today)
            existing_transaction = CoinTransaction.query.filter(
                CoinTransaction.user_id == user_id,
                CoinTransaction.source == 'comment_posted',
                CoinTransaction.context_data.op('->>')('comment_id') == str(comment_id),
                CoinTransaction.coins_change > 0
            ).first()
            
            if existing_transaction:
                return {
                    'success': False,
                    'error': 'Coins already awarded for this comment',
                    'coins_awarded': 0
                }
            
            # Check daily limit
            daily_earned = CoinEarningService.get_daily_earnings(user_id, 'comment_posted')
            if daily_earned >= CoinEarningService.DAILY_LIMITS['comment_posted']:
                return {
                    'success': False,
                    'error': 'Daily comment limit reached',
                    'coins_awarded': 0
                }
            
            # Award comment coins
            coins = CoinEarningService.COIN_RATES['comment_posted']
            result = WalletService.add_coins_secure(
                user_id=user_id,
                coins=coins,
                coin_type='bronze',
                source='comment_posted',
                description='Comment posting reward',
                context_data={
                    'comment_id': comment_id,
                    'article_id': article_id,
                    'date': today.isoformat()
                }
            )
            
            if result['success']:
                # Check for achievements
                achievement_result = AchievementService.check_and_award_achievements(
                    user_id, 'comment_posted', {'comment_id': comment_id, 'article_id': article_id}
                )

                total_coins = coins
                if achievement_result['success']:
                    total_coins += achievement_result['total_points_earned']

                return {
                    'success': True,
                    'coins_awarded': total_coins,
                    'base_coins': coins,
                    'achievement_coins': achievement_result['total_points_earned'],
                    'achievements_awarded': achievement_result['awarded_achievements']
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error awarding comment coins for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to award comment coins',
                'coins_awarded': 0
            }
    
    @staticmethod
    def award_rating_coins(user_id: int, rating_id: int, article_id: int = None) -> Dict:
        """Award coins for rating content"""
        try:
            from models import PricingConfig
            from routes.utils.wallet_service import WalletService

            # Check if achievements and bronze coins are enabled
            achievements_enabled = PricingConfig.get_config_value('achievements_enabled', True)
            bronze_enabled = WalletService.is_bronze_coin_system_enabled()

            if not achievements_enabled:
                return {
                    'success': False,
                    'error': 'Achievement system is disabled',
                    'coins_awarded': 0
                }

            if not bronze_enabled:
                return {
                    'success': False,
                    'error': 'Bronze coin system is disabled',
                    'coins_awarded': 0
                }

            today = datetime.now(timezone.utc).date()

            # Check daily limit
            daily_earned = CoinEarningService.get_daily_earnings(user_id, 'rating_given')
            if daily_earned >= CoinEarningService.DAILY_LIMITS['rating_given']:
                return {
                    'success': False,
                    'error': 'Daily rating limit reached',
                    'coins_awarded': 0
                }
            
            # Award rating coins
            coins = CoinEarningService.COIN_RATES['rating_given']
            result = WalletService.add_coins_secure(
                user_id=user_id,
                coins=coins,
                coin_type='bronze',
                source='rating_given',
                description='Rating reward',
                context_data={
                    'rating_id': rating_id,
                    'article_id': article_id,
                    'date': today.isoformat()
                }
            )
            
            if result['success']:
                # Check for achievements
                achievement_result = AchievementService.check_and_award_achievements(
                    user_id, 'rating_given', {'rating_id': rating_id, 'article_id': article_id}
                )
                
                total_coins = coins
                if achievement_result['success']:
                    total_coins += achievement_result['total_points_earned']
                
                return {
                    'success': True,
                    'coins_awarded': total_coins,
                    'base_coins': coins,
                    'achievement_coins': achievement_result['total_points_earned'],
                    'achievements_awarded': achievement_result['awarded_achievements']
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error awarding rating coins for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to award rating coins',
                'coins_awarded': 0
            }
    
    @staticmethod
    def get_daily_earnings(user_id: int, earning_type: str) -> int:
        """Get user's daily earnings for a specific type"""
        try:
            today = datetime.now(timezone.utc).date()
            
            total = db.session.query(db.func.sum(CoinTransaction.coins_change))\
                .filter(
                    CoinTransaction.user_id == user_id,
                    CoinTransaction.source == earning_type,
                    db.func.date(CoinTransaction.created_at) == today,
                    CoinTransaction.coins_change > 0
                ).scalar() or 0
            
            return int(total)
            
        except Exception as e:
            logger.error(f"Error getting daily earnings for user {user_id}, type {earning_type}: {str(e)}")
            return 0
    
    @staticmethod
    def get_daily_earnings_summary(user_id: int) -> Dict:
        """Get summary of daily earnings for all types"""
        try:
            today = datetime.now(timezone.utc).date()
            
            earnings = {}
            for earning_type in CoinEarningService.COIN_RATES.keys():
                daily_earned = CoinEarningService.get_daily_earnings(user_id, earning_type)
                daily_limit = CoinEarningService.DAILY_LIMITS.get(earning_type, 0)
                
                earnings[earning_type] = {
                    'earned_today': daily_earned,
                    'daily_limit': daily_limit,
                    'remaining': max(0, daily_limit - daily_earned),
                    'can_earn_more': daily_earned < daily_limit
                }
            
            return {
                'success': True,
                'earnings': earnings,
                'total_earned_today': sum(e['earned_today'] for e in earnings.values())
            }
            
        except Exception as e:
            logger.error(f"Error getting daily earnings summary for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to get daily earnings summary'
            }
    
    @staticmethod
    def get_earning_statistics(user_id: int) -> Dict:
        """Get comprehensive earning statistics"""
        try:
            # Get total earnings by type
            earning_stats = db.session.query(
                CoinTransaction.source,
                db.func.count(CoinTransaction.id).label('count'),
                db.func.sum(CoinTransaction.coins_change).label('total_coins')
            ).filter(
                CoinTransaction.user_id == user_id,
                CoinTransaction.coins_change > 0
            ).group_by(CoinTransaction.source).all()
            
            # Get monthly earnings
            monthly_earnings = db.session.query(
                db.func.date_trunc('month', CoinTransaction.created_at).label('month'),
                db.func.sum(CoinTransaction.coins_change).label('total_coins')
            ).filter(
                CoinTransaction.user_id == user_id,
                CoinTransaction.coins_change > 0
            ).group_by(db.func.date_trunc('month', CoinTransaction.created_at))\
            .order_by(db.func.date_trunc('month', CoinTransaction.created_at).desc())\
            .limit(12).all()
            
            return {
                'success': True,
                'earning_by_type': [
                    {
                        'type': stat.source,
                        'count': stat.count,
                        'total_coins': int(stat.total_coins) if stat.total_coins else 0
                    }
                    for stat in earning_stats
                ],
                'monthly_earnings': [
                    {
                        'month': stat.month.strftime('%Y-%m') if stat.month else None,
                        'total_coins': int(stat.total_coins) if stat.total_coins else 0
                    }
                    for stat in monthly_earnings
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting earning statistics for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to get earning statistics'
            }
    
    @staticmethod
    def award_comment_coins(user_id: int, comment_id: int, article_id: int = None) -> Dict:
        """Award coins for posting a comment"""
        try:
            today = datetime.now(timezone.utc).date()
            
            # Check if user already received coins for this comment (ever, not just today)
            existing_transaction = CoinTransaction.query.filter(
                CoinTransaction.user_id == user_id,
                CoinTransaction.source == 'comment_posted',
                CoinTransaction.context_data.op('->>')('comment_id') == str(comment_id),
                CoinTransaction.coins_change > 0
            ).first()
            
            if existing_transaction:
                return {
                    'success': False,
                    'error': 'Coins already awarded for this comment',
                    'coins_awarded': 0
                }
            
            # Check daily limit
            daily_earned = CoinEarningService.get_daily_earnings(user_id, 'comment_posted')
            if daily_earned >= CoinEarningService.DAILY_LIMITS['comment_posted']:
                return {
                    'success': False,
                    'error': 'Daily comment limit reached',
                    'coins_awarded': 0
                }
            
            # Award comment coins
            coins = CoinEarningService.COIN_RATES['comment_posted']
            result = WalletService.add_coins_secure(
                user_id=user_id,
                coins=coins,
                coin_type='bronze',
                source='comment_posted',
                description='Comment posting reward',
                context_data={
                    'comment_id': comment_id,
                    'article_id': article_id,
                    'date': today.isoformat()
                }
            )
            
            if result['success']:
                # Check for comment achievements
                AchievementService.check_and_award_achievements(
                    user_id=user_id,
                    activity_type='total_comments',
                    context_data={'comment_id': comment_id, 'comment_bonus': True}
                )
                
                return {
                    'success': True,
                    'coins_awarded': coins,
                    'message': f'Comment reward: +{coins} coins'
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error awarding comment coins to user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to award comment coins'
            }
    
    @staticmethod
    def award_rating_coins(user_id: int, rating_id: int, article_id: int = None) -> Dict:
        """Award coins for giving a rating"""
        try:
            today = datetime.now(timezone.utc).date()
            
            # Check daily limit
            daily_earned = CoinEarningService.get_daily_earnings(user_id, 'rating_given')
            if daily_earned >= CoinEarningService.DAILY_LIMITS['rating_given']:
                return {
                    'success': False,
                    'error': 'Daily rating limit reached',
                    'coins_awarded': 0
                }
            
            # Award rating coins
            coins = CoinEarningService.COIN_RATES['rating_given']
            result = WalletService.add_coins_secure(
                user_id=user_id,
                coins=coins,
                coin_type='bronze',
                source='rating_given',
                description='Rating reward',
                context_data={
                    'rating_id': rating_id,
                    'article_id': article_id,
                    'date': today.isoformat()
                }
            )
            
            if result['success']:
                return {
                    'success': True,
                    'coins_awarded': coins,
                    'message': f'Rating reward: +{coins} coins'
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error awarding rating coins to user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to award rating coins'
            }
    
    @staticmethod
    def award_share_coins(user_id: int, content_type: str, content_id: int, platform: str = None) -> Dict:
        """Award coins for sharing content"""
        try:
            from models import PricingConfig
            from routes.utils.wallet_service import WalletService

            # Check if achievements and bronze coins are enabled
            achievements_enabled = PricingConfig.get_config_value('achievements_enabled', True)
            bronze_enabled = WalletService.is_bronze_coin_system_enabled()

            if not achievements_enabled:
                return {
                    'success': False,
                    'error': 'Achievement system is disabled',
                    'coins_awarded': 0
                }

            if not bronze_enabled:
                return {
                    'success': False,
                    'error': 'Bronze coin system is disabled',
                    'coins_awarded': 0
                }

            today = datetime.now(timezone.utc).date()

            # Check daily limit
            daily_earned = CoinEarningService.get_daily_earnings(user_id, 'share_content')
            if daily_earned >= CoinEarningService.DAILY_LIMITS['share_content']:
                return {
                    'success': False,
                    'error': 'Daily sharing limit reached',
                    'coins_awarded': 0
                }
            
            # Award share coins
            coins = CoinEarningService.COIN_RATES['share_content']
            result = WalletService.add_coins_secure(
                user_id=user_id,
                coins=coins,
                coin_type='bronze',
                source='share_content',
                description='Content sharing reward',
                context_data={
                    'content_type': content_type,
                    'content_id': content_id,
                    'platform': platform,
                    'date': today.isoformat()
                }
            )
            
            if result['success']:
                return {
                    'success': True,
                    'coins_awarded': coins,
                    'message': f'Sharing reward: +{coins} coins'
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error awarding share coins to user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to award share coins'
            }
    
    @staticmethod
    def award_referral_coins(user_id: int, referred_user_id: int) -> Dict:
        """Award coins for successful referral"""
        try:
            from models import PricingConfig
            from routes.utils.wallet_service import WalletService

            # Check if achievements and bronze coins are enabled
            achievements_enabled = PricingConfig.get_config_value('achievements_enabled', True)
            bronze_enabled = WalletService.is_bronze_coin_system_enabled()

            if not achievements_enabled:
                return {
                    'success': False,
                    'error': 'Achievement system is disabled',
                    'coins_awarded': 0
                }

            if not bronze_enabled:
                return {
                    'success': False,
                    'error': 'Bronze coin system is disabled',
                    'coins_awarded': 0
                }

            # Check if user already received coins for this referral
            existing_transaction = CoinTransaction.query.filter(
                CoinTransaction.user_id == user_id,
                CoinTransaction.source == 'referral_signup',
                CoinTransaction.context_data.op('->>')('referred_user_id') == str(referred_user_id)
            ).first()
            
            if existing_transaction:
                return {
                    'success': False,
                    'error': 'Referral coins already awarded',
                    'coins_awarded': 0
                }
            
            # Award referral coins
            coins = CoinEarningService.COIN_RATES['referral_signup']
            result = WalletService.add_coins_secure(
                user_id=user_id,
                coins=coins,
                coin_type='bronze',
                source='referral_signup',
                description='Referral signup reward',
                context_data={
                    'referred_user_id': referred_user_id,
                    'date': datetime.now(timezone.utc).isoformat()
                }
            )
            
            if result['success']:
                return {
                    'success': True,
                    'coins_awarded': coins,
                    'message': f'Referral reward: +{coins} coins'
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error awarding referral coins to user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to award referral coins'
            }
    
    @staticmethod
    def award_streak_bonus_coins(user_id: int, streak_type: str, streak_days: int) -> Dict:
        """Award bonus coins for maintaining streaks"""
        try:
            from models import PricingConfig
            from routes.utils.wallet_service import WalletService

            # Check if achievements and bronze coins are enabled
            achievements_enabled = PricingConfig.get_config_value('achievements_enabled', True)
            bronze_enabled = WalletService.is_bronze_coin_system_enabled()

            if not achievements_enabled:
                return {
                    'success': False,
                    'error': 'Achievement system is disabled',
                    'coins_awarded': 0
                }

            if not bronze_enabled:
                return {
                    'success': False,
                    'error': 'Bronze coin system is disabled',
                    'coins_awarded': 0
                }

            # Calculate bonus based on streak length
            if streak_days < 7:
                bonus_multiplier = 1
            elif streak_days < 30:
                bonus_multiplier = 2
            elif streak_days < 100:
                bonus_multiplier = 3
            else:
                bonus_multiplier = 5
            
            coins = CoinEarningService.COIN_RATES['streak_bonus'] * bonus_multiplier
            
            result = WalletService.add_coins_secure(
                user_id=user_id,
                coins=coins,
                coin_type='bronze',
                source='streak_bonus',
                description=f'{streak_type.replace("_", " ").title()} streak bonus',
                context_data={
                    'streak_type': streak_type,
                    'streak_days': streak_days,
                    'bonus_multiplier': bonus_multiplier
                }
            )
            
            if result['success']:
                return {
                    'success': True,
                    'coins_awarded': coins,
                    'message': f'Streak bonus: +{coins} coins ({streak_days} days)'
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error awarding streak bonus coins to user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to award streak bonus coins'
            }
    
    @staticmethod
    def get_daily_earnings(user_id: int, source: str) -> int:
        """Get user's daily earnings for a specific source"""
        try:
            today = datetime.now(timezone.utc).date()
            
            total_earned = db.session.query(db.func.sum(CoinTransaction.coins_change))\
                .filter(
                    CoinTransaction.user_id == user_id,
                    CoinTransaction.source == source,
                    db.func.date(CoinTransaction.created_at) == today,
                    CoinTransaction.coins_change > 0
                ).scalar()
            
            return int(total_earned) if total_earned else 0
            
        except Exception as e:
            logger.error(f"Error getting daily earnings for user {user_id}, source {source}: {str(e)}")
            return 0
    
    @staticmethod
    def get_daily_earning_summary(user_id: int) -> Dict:
        """Get user's daily earning summary"""
        try:
            today = datetime.now(timezone.utc).date()
            
            # Get all earnings for today
            earnings = db.session.query(
                CoinTransaction.source,
                db.func.sum(CoinTransaction.coins_change).label('total_coins')
            ).filter(
                CoinTransaction.user_id == user_id,
                db.func.date(CoinTransaction.created_at) == today,
                CoinTransaction.coins_change > 0
            ).group_by(CoinTransaction.source).all()
            
            summary = {
                'date': today.isoformat(),
                'total_earned': 0,
                'by_source': {},
                'limits_reached': []
            }
            
            for source, total_coins in earnings:
                summary['by_source'][source] = int(total_coins)
                summary['total_earned'] += int(total_coins)
                
                # Check if limit is reached
                if source in CoinEarningService.DAILY_LIMITS:
                    limit = CoinEarningService.DAILY_LIMITS[source]
                    if int(total_coins) >= limit:
                        summary['limits_reached'].append(source)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting daily earning summary for user {user_id}: {str(e)}")
            return {
                'date': datetime.now(timezone.utc).date().isoformat(),
                'total_earned': 0,
                'by_source': {},
                'limits_reached': []
            }
    
    @staticmethod
    def get_weekly_earning_summary(user_id: int) -> Dict:
        """Get user's weekly earning summary"""
        try:
            week_start = datetime.now(timezone.utc).date() - timedelta(days=7)
            
            # Get all earnings for the past week
            earnings = db.session.query(
                db.func.date(CoinTransaction.created_at).label('date'),
                CoinTransaction.source,
                db.func.sum(CoinTransaction.coins_change).label('total_coins')
            ).filter(
                CoinTransaction.user_id == user_id,
                db.func.date(CoinTransaction.created_at) >= week_start,
                CoinTransaction.coins_change > 0
            ).group_by(
                db.func.date(CoinTransaction.created_at),
                CoinTransaction.source
            ).all()
            
            summary = {
                'week_start': week_start.isoformat(),
                'total_earned': 0,
                'daily_breakdown': {},
                'by_source': {}
            }
            
            for date, source, total_coins in earnings:
                date_str = date.isoformat()
                coins = int(total_coins)
                
                if date_str not in summary['daily_breakdown']:
                    summary['daily_breakdown'][date_str] = {}
                
                summary['daily_breakdown'][date_str][source] = coins
                summary['total_earned'] += coins
                
                if source not in summary['by_source']:
                    summary['by_source'][source] = 0
                summary['by_source'][source] += coins
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting weekly earning summary for user {user_id}: {str(e)}")
            return {
                'week_start': (datetime.now(timezone.utc).date() - timedelta(days=7)).isoformat(),
                'total_earned': 0,
                'daily_breakdown': {},
                'by_source': {}
            }
    
    @staticmethod
    def get_earning_opportunities(user_id: int) -> Dict:
        """Get available earning opportunities for user"""
        try:
            today = datetime.now(timezone.utc).date()
            opportunities = []
            
            # Check daily login
            login_transaction = CoinTransaction.query.filter(
                CoinTransaction.user_id == user_id,
                CoinTransaction.source == 'daily_login',
                db.func.date(CoinTransaction.created_at) == today
            ).first()
            
            if not login_transaction:
                opportunities.append({
                    'type': 'daily_login',
                    'coins': CoinEarningService.COIN_RATES['daily_login'],
                    'description': 'Log in daily to earn bonus coins',
                    'available': True,
                    'limit_info': None
                })
            
            # Check other opportunities based on daily limits
            for source, limit in CoinEarningService.DAILY_LIMITS.items():
                if source == 'daily_login':
                    continue
                
                daily_earned = CoinEarningService.get_daily_earnings(user_id, source)
                remaining = limit - daily_earned
                
                if remaining > 0:
                    opportunities.append({
                        'type': source,
                        'coins': CoinEarningService.COIN_RATES.get(source, 0),
                        'description': f'Earn coins by {source.replace("_", " ")}',
                        'available': True,
                        'limit_info': {
                            'daily_limit': limit,
                            'earned_today': daily_earned,
                            'remaining': remaining
                        }
                    })
            
            return {
                'success': True,
                'opportunities': opportunities,
                'total_available': sum(opp['coins'] * (opp['limit_info']['remaining'] if opp['limit_info'] else 1) for opp in opportunities)
            }
            
        except Exception as e:
            logger.error(f"Error getting earning opportunities for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to get earning opportunities'
            }
