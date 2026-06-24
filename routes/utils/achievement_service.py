"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Enhanced Achievement Service
Comprehensive achievement system with coin rewards and progress tracking
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from models import db, User, UserAchievement, Achievement, AchievementCategory, UserPoints, PointTransaction
from flask import current_app
import json

logger = logging.getLogger(__name__)

class AchievementService:
    """Enhanced achievement service with coin rewards and progress tracking"""
    
    @staticmethod
    def check_and_award_achievements(user_id: int, activity_type: str, 
                                   context_data: Dict = None) -> Dict:
        """Check and award achievements based on user activity"""
        try:
            awarded_achievements = []
            total_points_earned = 0
            
            # Get user's current stats
            user_stats = AchievementService.get_user_activity_stats(user_id, activity_type, context_data)
            
            # Get all active achievements for this activity type
            achievements = Achievement.query.filter(
                Achievement.is_active == True,
                Achievement.criteria_type == activity_type
            ).all()
            
            for achievement in achievements:
                # Check if user already has this achievement
                existing = UserAchievement.query.filter_by(
                    user_id=user_id,
                    achievement_id=achievement.id
                ).first()
                
                if existing:
                    continue
                
                # Check if achievement criteria is met
                if AchievementService.check_achievement_criteria(user_id, achievement, user_stats, context_data):
                    # Award the achievement
                    award_result = AchievementService.award_achievement(user_id, achievement)
                    if award_result['success']:
                        awarded_achievements.append(award_result['achievement'])
                        if achievement.points_reward and achievement.points_reward > 0:
                            total_points_earned += achievement.points_reward
            
            return {
                'success': True,
                'awarded_achievements': awarded_achievements,
                'total_points_earned': total_points_earned,
                'achievements_count': len(awarded_achievements)
            }
            
        except Exception as e:
            logger.error(f"Error checking achievements for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to check achievements',
                'awarded_achievements': [],
                'total_points_earned': 0
            }
    
    @staticmethod
    def award_achievement(user_id: int, achievement: Achievement) -> Dict:
        """Award an achievement to a user with coin rewards"""
        try:
            # Check if user already has this achievement
            existing = UserAchievement.query.filter_by(
                user_id=user_id,
                achievement_id=achievement.id
            ).first()
            
            if existing:
                return {
                    'success': False,
                    'error': 'Achievement already awarded',
                    'achievement': AchievementService.format_achievement(achievement, existing)
                }
            
            # Create user achievement record
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=achievement.id,
                completed_at=datetime.now(timezone.utc),
                is_completed=True
            )
            
            db.session.add(user_achievement)
            
            # Award points if specified
            points_awarded = 0
            if achievement.points_reward and achievement.points_reward > 0:
                from routes.utils.points_service import PointsService
                points_result = PointsService.award_achievement_points(
                    user_id=user_id,
                    achievement_id=achievement.id,
                    context_data={
                        'achievement_id': achievement.id,
                        'achievement_name': achievement.name,
                        'achievement_type': achievement.achievement_type,
                        'rarity': achievement.rarity
                    }
                )
                
                if points_result['success']:
                    points_awarded = achievement.points_reward
                else:
                    logger.warning(f"Failed to award points for achievement {achievement.id}: {points_result.get('error')}")
            
            db.session.commit()
            
            logger.info(f"Awarded achievement '{achievement.name}' to user {user_id} with {points_awarded} points")
            
            return {
                'success': True,
                'achievement': AchievementService.format_achievement(achievement, user_achievement),
                'points_awarded': points_awarded
            }
            
        except Exception as e:
            logger.error(f"Error awarding achievement {achievement.id} to user {user_id}: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': 'Failed to award achievement'
            }
    
    @staticmethod
    def check_achievement_criteria(user_id: int, achievement: Achievement, 
                                 user_stats: Dict, context_data: Dict = None) -> bool:
        """Check if achievement criteria is met"""
        try:
            if achievement.criteria_type == 'login_streak':
                current_streak = user_stats.get('login_streak', 0)
                return AchievementService.evaluate_criteria(current_streak, achievement.criteria_value, achievement.criteria_operator)
            
            elif achievement.criteria_type == 'reading_streak':
                current_streak = user_stats.get('reading_streak', 0)
                return AchievementService.evaluate_criteria(current_streak, achievement.criteria_value, achievement.criteria_operator)
            
            elif achievement.criteria_type == 'total_articles_read':
                total_read = user_stats.get('total_articles_read', 0)
                return AchievementService.evaluate_criteria(total_read, achievement.criteria_value, achievement.criteria_operator)
            
            elif achievement.criteria_type == 'total_comments':
                total_comments = user_stats.get('total_comments', 0)
                return AchievementService.evaluate_criteria(total_comments, achievement.criteria_value, achievement.criteria_operator)
            
            elif achievement.criteria_type == 'total_points_earned':
                total_points = user_stats.get('total_points_earned', 0)
                return AchievementService.evaluate_criteria(total_points, achievement.criteria_value, achievement.criteria_operator)
            
            elif achievement.criteria_type == 'days_since_registration':
                days_registered = user_stats.get('days_since_registration', 0)
                return AchievementService.evaluate_criteria(days_registered, achievement.criteria_value, achievement.criteria_operator)
            
            elif achievement.criteria_type == 'special_activity':
                # Special achievements that are triggered by specific events
                return context_data and context_data.get('trigger_achievement', False)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking achievement criteria for achievement {achievement.id}: {str(e)}")
            return False
    
    @staticmethod
    def evaluate_criteria(current_value: int, target_value: int, operator: str) -> bool:
        """Evaluate achievement criteria"""
        if operator == '>=':
            return current_value >= target_value
        elif operator == '>':
            return current_value > target_value
        elif operator == '=':
            return current_value == target_value
        elif operator == '<=':
            return current_value <= target_value
        elif operator == '<':
            return current_value < target_value
        else:
            return current_value >= target_value  # Default to >=
    
    @staticmethod
    def get_user_activity_stats(user_id: int, activity_type: str, context_data: Dict = None) -> Dict:
        """Get user's current activity statistics"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {}
            
            stats = {
                'user_id': user_id,
                'registration_date': user.created_at,
                'days_since_registration': (datetime.now(timezone.utc) - (user.created_at.replace(tzinfo=timezone.utc) if user.created_at and user.created_at.tzinfo is None else user.created_at)).days if user.created_at else 0,
                'is_premium': user.is_premium,
                'total_points': user.points or 0
            }
            
            # Get points stats
            user_points = UserPoints.query.filter_by(user_id=user_id).first()
            if user_points:
                stats.update({
                    'total_points_earned': user_points.total_points,
                    'current_level': user_points.current_level,
                    'points_to_next_level': user_points.points_to_next_level
                })
            
            # Get activity-specific stats
            if activity_type == 'login_streak':
                # Get login streak from UserStreak relationship
                login_streak = None
                if hasattr(user, 'streaks'):
                    for streak in user.streaks:
                        if streak.streak_type == 'login':
                            login_streak = streak.current_streak
                            break
                stats['login_streak'] = login_streak or 0
            
            elif activity_type == 'reading_streak':
                stats['reading_streak'] = user.reading_streak or 0
            
            elif activity_type == 'total_articles_read':
                # Count total articles read (this would need to be tracked in a separate table)
                stats['total_articles_read'] = context_data.get('total_articles_read', 0) if context_data else 0
            
            elif activity_type == 'total_comments':
                # Count total comments made
                stats['total_comments'] = context_data.get('total_comments', 0) if context_data else 0
            
            elif activity_type == 'total_points_earned':
                stats['total_points_earned'] = user_points.total_points if user_points else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user activity stats for user {user_id}: {str(e)}")
            return {}
    
    @staticmethod
    def get_user_achievements(user_id: int, include_progress: bool = True) -> Dict:
        """Get user's achievements with progress information"""
        try:
            # Get user's earned achievements
            user_achievements = db.session.query(UserAchievement, Achievement)\
                .join(Achievement, UserAchievement.achievement_id == Achievement.id)\
                .filter(UserAchievement.user_id == user_id)\
                .order_by(UserAchievement.completed_at.desc())\
                .all()
            
            earned_achievements = []
            for user_achievement, achievement in user_achievements:
                earned_achievements.append(AchievementService.format_achievement(achievement, user_achievement))
            
            # Get available achievements (not yet earned)
            earned_ids = [ua.achievement_id for ua, _ in user_achievements]
            available_achievements = []
            
            if include_progress:
                available = Achievement.query.filter(
                    Achievement.is_active == True,
                    ~Achievement.id.in_(earned_ids)
                ).all()
                
                # Get user stats for progress calculation
                user_stats = AchievementService.get_user_activity_stats(user_id, 'GENERAL')
                
                for achievement in available:
                    progress_info = AchievementService.calculate_progress(user_id, achievement, user_stats)
                    if not achievement.is_hidden or progress_info['progress_percentage'] > 0:
                        achievement_dict = AchievementService.format_achievement(achievement)
                        achievement_dict.update(progress_info)
                        available_achievements.append(achievement_dict)
            
            # Calculate summary statistics
            total_achievements = Achievement.query.filter(Achievement.is_active == True).count()
            earned_count = len(earned_achievements)
            total_points_earned = sum(ach.get('points_reward', 0) for ach in earned_achievements)
            
            return {
                'success': True,
                'earned_achievements': earned_achievements,
                'available_achievements': available_achievements,
                'summary': {
                    'total_achievements': total_achievements,
                    'earned_count': earned_count,
                    'progress_percentage': round((earned_count / total_achievements * 100), 2) if total_achievements > 0 else 0,
                    'total_points_earned': total_points_earned
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user achievements for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to retrieve achievements'
            }
    
    @staticmethod
    def calculate_progress(user_id: int, achievement: Achievement, user_stats: Dict = None) -> Dict:
        """Calculate progress towards an achievement"""
        try:
            if not user_stats:
                user_stats = AchievementService.get_user_activity_stats(user_id, achievement.criteria_type)
            
            current_value = 0
            target_value = achievement.criteria_value
            
            if achievement.criteria_type == 'login_streak':
                current_value = user_stats.get('login_streak', 0)
            elif achievement.criteria_type == 'reading_streak':
                current_value = user_stats.get('reading_streak', 0)
            elif achievement.criteria_type == 'total_articles_read':
                current_value = user_stats.get('total_articles_read', 0)
            elif achievement.criteria_type == 'total_comments':
                current_value = user_stats.get('total_comments', 0)
            elif achievement.criteria_type == 'total_points_earned':
                current_value = user_stats.get('total_points_earned', 0)
            elif achievement.criteria_type == 'days_since_registration':
                current_value = user_stats.get('days_since_registration', 0)
            
            progress_percentage = min(100, round((current_value / target_value * 100), 2)) if target_value > 0 else 0
            is_completed = AchievementService.evaluate_criteria(current_value, target_value, achievement.criteria_operator)
            
            return {
                'current_value': current_value,
                'target_value': target_value,
                'progress_percentage': progress_percentage,
                'is_completed': is_completed,
                'remaining': max(0, target_value - current_value) if not is_completed else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating progress for achievement {achievement.id}: {str(e)}")
            return {
                'current_value': 0,
                'target_value': achievement.criteria_value,
                'progress_percentage': 0,
                'is_completed': False,
                'remaining': achievement.criteria_value
            }
    
    @staticmethod
    def format_achievement(achievement: Achievement, user_achievement: UserAchievement = None) -> Dict:
        """Format achievement for API response"""
        result = {
            'id': achievement.id,
            'name': achievement.name,
            'description': achievement.description,
            'achievement_type': achievement.achievement_type,
            'criteria_type': achievement.criteria_type,
            'criteria_value': achievement.criteria_value,
            'criteria_operator': achievement.criteria_operator,
            'points_reward': achievement.points_reward,
            'badge_icon': achievement.badge_icon,
            'rarity': achievement.rarity,
            'is_hidden': achievement.is_hidden,
            'category': {
                'id': achievement.category.id,
                'name': achievement.category.name,
                'description': achievement.category.description
            } if achievement.category else None,
            'is_earned': user_achievement is not None,
            'completed_at': user_achievement.completed_at.isoformat() if user_achievement and user_achievement.completed_at else None,
            'is_completed': user_achievement.is_completed if user_achievement else False
        }
        
        return result
    
    @staticmethod
    def get_achievement_categories() -> Dict:
        """Get all achievement categories"""
        try:
            categories = AchievementCategory.query.filter_by(is_active=True).all()
            
            return {
                'success': True,
                'categories': [
                    {
                        'id': category.id,
                        'name': category.name,
                        'description': category.description,
                        'icon': category.icon_class,
                        'color': category.color,
                        'achievement_count': Achievement.query.filter_by(
                            category_id=category.id,
                            is_active=True
                        ).count()
                    }
                    for category in categories
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting achievement categories: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to retrieve achievement categories'
            }
    
    @staticmethod
    def mark_achievement_notified(user_id: int, achievement_id: int) -> Dict:
        """Mark an achievement as notified"""
        try:
            user_achievement = UserAchievement.query.filter_by(
                user_id=user_id,
                achievement_id=achievement_id
            ).first()
            
            if not user_achievement:
                return {
                    'success': False,
                    'error': 'Achievement not found'
                }
            
            # Note: UserAchievement model doesn't have is_notified field
            # This could be implemented as a separate notification tracking table
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Achievement marked as notified'
            }
            
        except Exception as e:
            logger.error(f"Error marking achievement {achievement_id} as notified for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to mark achievement as notified'
            }
    
    @staticmethod
    def get_unnotified_achievements(user_id: int) -> Dict:
        """Get user's unnotified achievements"""
        try:
            unnotified = db.session.query(UserAchievement, Achievement)\
                .join(Achievement, UserAchievement.achievement_id == Achievement.id)\
                .filter(
                    UserAchievement.user_id == user_id,
                    UserAchievement.is_completed == True
                )\
                .order_by(UserAchievement.completed_at.desc())\
                .all()
            
            return {
                'success': True,
                'unnotified_achievements': [
                    AchievementService.format_achievement(achievement, user_achievement)
                    for user_achievement, achievement in unnotified
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting unnotified achievements for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to retrieve unnotified achievements'
            }
    
    @staticmethod
    def get_user_achievement_stats(user_id: int) -> Dict:
        """Get user's achievement statistics"""
        try:
            # Get total achievements earned
            total_earned = db.session.query(UserAchievement)\
                .filter_by(user_id=user_id)\
                .count()
            
            # Get total available achievements
            total_available = db.session.query(Achievement)\
                .filter_by(is_active=True)\
                .count()
            
            # Get total points earned from achievements
            total_points_earned = db.session.query(db.func.sum(Achievement.points_reward))\
                .join(UserAchievement, Achievement.id == UserAchievement.achievement_id)\
                .filter(UserAchievement.user_id == user_id)\
                .scalar() or 0
            
            # Calculate completion percentage
            completion_percentage = (total_earned / total_available * 100) if total_available > 0 else 0
            
            return {
                'total_earned': total_earned,
                'total_available': total_available,
                'total_points_earned': total_points_earned,
                'completion_percentage': round(completion_percentage, 1)
            }
            
        except Exception as e:
            logger.error(f"Error getting achievement stats for user {user_id}: {str(e)}")
            return {
                'total_earned': 0,
                'total_available': 0,
                'total_points_earned': 0,
                'completion_percentage': 0
            }

    @staticmethod
    def get_recent_achievements(user_id: int, limit: int = 10) -> Dict:
        """Get user's most recently earned achievements"""
        try:
            # Get user's recently earned achievements
            recent_achievements = db.session.query(UserAchievement, Achievement)\
                .join(Achievement, UserAchievement.achievement_id == Achievement.id)\
                .filter(UserAchievement.user_id == user_id)\
                .filter(UserAchievement.is_completed == True)\
                .order_by(UserAchievement.completed_at.desc())\
                .limit(limit)\
                .all()

            achievements = []
            for user_achievement, achievement in recent_achievements:
                achievements.append(AchievementService.format_achievement(achievement, user_achievement))

            return {
                'success': True,
                'achievements': achievements,
                'count': len(achievements),
                'limit': limit
            }

        except Exception as e:
            logger.error(f"Error getting recent achievements for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to retrieve recent achievements',
                'achievements': [],
                'count': 0,
                'limit': limit
            }
