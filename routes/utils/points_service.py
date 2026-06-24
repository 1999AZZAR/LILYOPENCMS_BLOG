"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Points Service - Handles user activity points/XP system
This is separate from the Coin system and is used for tracking user progress/levels
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from models import db, User, UserPoints, PointTransaction, UserStreak, Achievement, UserAchievement
from routes.utils.achievement_service import AchievementService

logger = logging.getLogger(__name__)

class PointsService:
    """Service for managing user activity points/XP system"""
    
    # Points rates for different activities
    POINTS_RATES = {
        'daily_login': 10,
        'article_read': 5,
        'comment_posted': 3,
        'rating_given': 2,
        'content_shared': 4,
        'achievement_earned': 20,
        'streak_milestone': 50,
        'level_up': 100,
        'first_content': 25,
        'community_contribution': 15
    }
    
    # Daily limits to prevent abuse
    DAILY_LIMITS = {
        'article_read': 50,  # Max 50 points per day from reading
        'comment_posted': 30,  # Max 30 points per day from comments
        'rating_given': 20,  # Max 20 points per day from ratings
        'content_shared': 20,  # Max 20 points per day from sharing
    }
    
    @staticmethod
    def get_or_create_user_points(user_id: int) -> UserPoints:
        """Get or create user points record"""
        try:
            user_points = UserPoints.query.filter_by(user_id=user_id).first()
            if not user_points:
                user_points = UserPoints(user_id=user_id)
                db.session.add(user_points)
                db.session.commit()
                logger.info(f"Created new UserPoints record for user {user_id}")
            return user_points
        except Exception as e:
            logger.error(f"Error getting/creating user points for user {user_id}: {str(e)}")
            db.session.rollback()
            raise
    
    @staticmethod
    def add_activity_points(user_id: int, activity_type: str, amount: int = None, 
                          description: str = None, context_data: Dict = None) -> Dict:
        """Add points for user activity"""
        try:
            if amount is None:
                amount = PointsService.POINTS_RATES.get(activity_type, 0)
            
            if amount <= 0:
                return {'success': False, 'message': 'No points to award'}
            
            # Check daily limits
            if activity_type in PointsService.DAILY_LIMITS:
                daily_points = PointsService.get_daily_points(user_id, activity_type)
                if daily_points >= PointsService.DAILY_LIMITS[activity_type]:
                    return {'success': False, 'message': f'Daily limit reached for {activity_type}'}
            
            # Get user points record
            user_points = PointsService.get_or_create_user_points(user_id)
            
            # Add points and check for level up
            leveled_up = user_points.add_points(
                points=amount,
                source=activity_type,
                description=description,
                context_data=context_data
            )
            
            db.session.commit()
            
            result = {
                'success': True,
                'points_awarded': amount,
                'total_points': user_points.total_points,
                'current_level': user_points.current_level,
                'leveled_up': leveled_up,
                'points_to_next_level': user_points.points_to_next_level
            }
            
            # If user leveled up, award bonus points
            if leveled_up:
                bonus_points = PointsService.POINTS_RATES.get('level_up', 0)
                if bonus_points > 0:
                    user_points.add_points(
                        points=bonus_points,
                        source='level_up',
                        description=f'Level {user_points.current_level} bonus',
                        context_data={'level': user_points.current_level}
                    )
                    db.session.commit()
                    result['level_up_bonus'] = bonus_points
            
            logger.info(f"Awarded {amount} points to user {user_id} for {activity_type}")
            return result
            
        except Exception as e:
            logger.error(f"Error adding activity points for user {user_id}: {str(e)}")
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_daily_points(user_id: int, activity_type: str, date: datetime = None) -> int:
        """Get points earned today for a specific activity type"""
        try:
            if date is None:
                date = datetime.now(timezone.utc).date()
            
            start_of_day = datetime.combine(date, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_of_day = datetime.combine(date, datetime.max.time()).replace(tzinfo=timezone.utc)
            
            total_points = db.session.query(db.func.sum(PointTransaction.points_change))\
                .join(UserPoints, PointTransaction.user_points_id == UserPoints.id)\
                .filter(UserPoints.user_id == user_id)\
                .filter(PointTransaction.source == activity_type)\
                .filter(PointTransaction.created_at >= start_of_day)\
                .filter(PointTransaction.created_at <= end_of_day)\
                .scalar() or 0
            
            return total_points
            
        except Exception as e:
            logger.error(f"Error getting daily points for user {user_id}: {str(e)}")
            return 0
    
    @staticmethod
    def get_user_points_summary(user_id: int) -> Dict:
        """Get comprehensive user points summary"""
        try:
            user_points = PointsService.get_or_create_user_points(user_id)
            
            # Get recent transactions
            recent_transactions = db.session.query(PointTransaction)\
                .join(UserPoints, PointTransaction.user_points_id == UserPoints.id)\
                .filter(UserPoints.user_id == user_id)\
                .order_by(PointTransaction.created_at.desc())\
                .limit(10)\
                .all()
            
            # Get daily points breakdown
            today = datetime.now(timezone.utc).date()
            daily_breakdown = {}
            for activity_type in PointsService.POINTS_RATES.keys():
                daily_breakdown[activity_type] = PointsService.get_daily_points(user_id, activity_type, today)
            
            return {
                'user_points': user_points.to_dict(),
                'recent_transactions': [tx.to_dict() for tx in recent_transactions],
                'daily_breakdown': daily_breakdown,
                'points_rates': PointsService.POINTS_RATES,
                'daily_limits': PointsService.DAILY_LIMITS
            }
            
        except Exception as e:
            logger.error(f"Error getting user points summary for user {user_id}: {str(e)}")
            return {}
    
    @staticmethod
    def award_daily_login_points(user_id: int) -> Dict:
        """Award points for daily login"""
        try:
            # Check if already awarded today
            today = datetime.now(timezone.utc).date()
            daily_points = PointsService.get_daily_points(user_id, 'daily_login', today)
            
            if daily_points > 0:
                return {'success': False, 'message': 'Daily login points already awarded'}
            
            # Award daily login points
            result = PointsService.add_activity_points(
                user_id=user_id,
                activity_type='daily_login',
                description='Daily login bonus'
            )
            
            # Update login streak
            try:
                from routes.utils.achievement_service import AchievementService
                AchievementService.check_and_award_achievements(user_id, 'daily_login')
            except Exception as e:
                logger.warning(f"Error checking daily login achievements: {str(e)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error awarding daily login points for user {user_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def award_article_read_points(user_id: int, article_id: int = None, context_data: Dict = None) -> Dict:
        """Award points for reading articles"""
        try:
            # Check if points were already awarded for this specific article (ever, not just today)
            if article_id:
                from models import PointTransaction, UserPoints
                existing_transaction = db.session.query(PointTransaction)\
                    .join(UserPoints, PointTransaction.user_points_id == UserPoints.id)\
                    .filter(
                        UserPoints.user_id == user_id,
                        PointTransaction.source == 'article_read',
                        PointTransaction.points_change > 0,
                        PointTransaction.context_data.op('->>')('article_id') == str(article_id)
                    ).first()
                
                if existing_transaction:
                    return {'success': False, 'message': 'Points already awarded for this article'}
            
            # Check if already read today (to prevent abuse)
            today = datetime.now(timezone.utc).date()
            daily_points = PointsService.get_daily_points(user_id, 'article_read', today)
            
            if daily_points >= PointsService.DAILY_LIMITS['article_read']:
                return {'success': False, 'message': 'Daily reading limit reached'}
            
            # Award points
            result = PointsService.add_activity_points(
                user_id=user_id,
                activity_type='article_read',
                description=f'Read article {article_id}' if article_id else 'Read article',
                context_data=context_data or {'article_id': article_id}
            )
            
            # Check achievements
            try:
                from routes.utils.achievement_service import AchievementService
                AchievementService.check_and_award_achievements(user_id, 'article_read', context_data)
            except Exception as e:
                logger.warning(f"Error checking article read achievements: {str(e)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error awarding article read points for user {user_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def award_comment_points(user_id: int, comment_id: int = None, context_data: Dict = None) -> Dict:
        """Award points for posting comments"""
        try:
            # Check if points were already awarded for this specific comment (ever, not just today)
            if comment_id:
                from models import PointTransaction, UserPoints
                existing_transaction = db.session.query(PointTransaction)\
                    .join(UserPoints, PointTransaction.user_points_id == UserPoints.id)\
                    .filter(
                        UserPoints.user_id == user_id,
                        PointTransaction.source == 'comment_posted',
                        PointTransaction.points_change > 0,
                        PointTransaction.context_data.op('->>')('comment_id') == str(comment_id)
                    ).first()
                
                if existing_transaction:
                    return {'success': False, 'message': 'Points already awarded for this comment'}
            
            # Check daily limit
            today = datetime.now(timezone.utc).date()
            daily_points = PointsService.get_daily_points(user_id, 'comment_posted', today)
            
            if daily_points >= PointsService.DAILY_LIMITS['comment_posted']:
                return {'success': False, 'message': 'Daily comment limit reached'}
            
            # Award points
            result = PointsService.add_activity_points(
                user_id=user_id,
                activity_type='comment_posted',
                description=f'Posted comment {comment_id}' if comment_id else 'Posted comment',
                context_data=context_data or {'comment_id': comment_id}
            )
            
            # Check achievements
            try:
                from routes.utils.achievement_service import AchievementService
                AchievementService.check_and_award_achievements(user_id, 'comment_posted', context_data)
            except Exception as e:
                logger.warning(f"Error checking comment achievements: {str(e)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error awarding comment points for user {user_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def award_rating_points(user_id: int, rating_id: int = None, context_data: Dict = None) -> Dict:
        """Award points for giving ratings"""
        try:
            # Check daily limit
            today = datetime.now(timezone.utc).date()
            daily_points = PointsService.get_daily_points(user_id, 'rating_given', today)
            
            if daily_points >= PointsService.DAILY_LIMITS['rating_given']:
                return {'success': False, 'message': 'Daily rating limit reached'}
            
            # Award points
            result = PointsService.add_activity_points(
                user_id=user_id,
                activity_type='rating_given',
                description=f'Gave rating {rating_id}' if rating_id else 'Gave rating',
                context_data=context_data or {'rating_id': rating_id}
            )
            
            # Check achievements
            try:
                from routes.utils.achievement_service import AchievementService
                AchievementService.check_and_award_achievements(user_id, 'rating_given', context_data)
            except Exception as e:
                logger.warning(f"Error checking rating achievements: {str(e)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error awarding rating points for user {user_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def award_achievement_points(user_id: int, achievement_id: int, context_data: Dict = None) -> Dict:
        """Award points for earning achievements"""
        try:
            # Award achievement points
            result = PointsService.add_activity_points(
                user_id=user_id,
                activity_type='achievement_earned',
                description=f'Earned achievement {achievement_id}',
                context_data=context_data or {'achievement_id': achievement_id}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error awarding achievement points for user {user_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_leaderboard(limit: int = 50, period: str = 'all') -> List[Dict]:
        """Get points leaderboard"""
        try:
            query = db.session.query(
                UserPoints.user_id,
                User.username,
                UserPoints.total_points,
                UserPoints.current_level,
                UserPoints.highest_level_reached
            ).join(User, UserPoints.user_id == User.id)\
            .filter(User.is_active == True)
            
            # Apply time filter if needed (this would require more complex queries)
            # For now, we'll just return all-time leaderboard
            
            leaderboard = query.order_by(UserPoints.total_points.desc())\
                .limit(limit)\
                .all()
            
            return [{
                'user_id': row.user_id,
                'username': row.username,
                'total_points': row.total_points,
                'current_level': row.current_level,
                'highest_level_reached': row.highest_level_reached
            } for row in leaderboard]
            
        except Exception as e:
            logger.error(f"Error getting points leaderboard: {str(e)}")
            return []
