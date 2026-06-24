"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Content deletion helper utilities.
Ensures proper cleanup of related data when content is deleted.
"""

from flask import current_app
from sqlalchemy import text
from models import (
    db,
    Comment,
    Rating,
    CommentLike,
    CommentReport,
    ReadingHistory,
    UserLibrary,
    User,
    UserActivity,
    UserAchievement,
    UserStreak,
    UserPoints,
    UserCoins,
    CoinTransaction,
    PaymentSession,
    UserProfile,
    UserStats,
    News,
    Album,
    Image,
    YouTubeVideo,
    SocialMedia,
    WriteAccessRequest,
    ContentEditRequest,
    AlbumEditRequest,
    EditorEditRequest,
    UserSubscription,
    CoinPackage,
    EmailLog,
    EmailTemplate,
)


def delete_content_with_related_data(content_type, content_id, content_title=None):
    """
    Delete content and all its related data to prevent orphaned records.
    
    Args:
        content_type (str): 'news' or 'album'
        content_id (int): ID of the content to delete
        content_title (str): Title for logging purposes
    
    Returns:
        dict: Statistics about what was deleted
    """
    deletion_stats = {
        'comments': 0,
        'comment_likes': 0,
        'comment_reports': 0,
        'ratings': 0,
        'reading_history': 0,
        'user_library': 0,
        'share_logs': 0,
        'edit_requests': 0
    }
    
    try:
        current_app.logger.info(f"Starting comprehensive deletion of {content_type} ID {content_id}")
        
        # 1. Delete comment-related data first (due to foreign key constraints)
        # Delete comment likes for comments on this content
        try:
            comment_likes_deleted = db.session.execute(text("""
                DELETE FROM comment_like
                WHERE comment_id IN (
                    SELECT id FROM comment
                    WHERE content_type = :content_type AND content_id = :content_id
                )
            """), {"content_type": content_type, "content_id": content_id})
            deletion_stats['comment_likes'] = comment_likes_deleted.rowcount
            current_app.logger.info(f"Deleted {deletion_stats['comment_likes']} comment likes")
        except Exception as e:
            current_app.logger.warning(f"Could not delete comment likes for {content_type} {content_id}: {e}")
            deletion_stats['comment_likes'] = 0

        # Delete comment reports for comments on this content
        try:
            comment_reports_deleted = db.session.execute(text("""
                DELETE FROM comment_report
                WHERE comment_id IN (
                    SELECT id FROM comment
                    WHERE content_type = :content_type AND content_id = :content_id
                )
            """), {"content_type": content_type, "content_id": content_id})
            deletion_stats['comment_reports'] = comment_reports_deleted.rowcount
            current_app.logger.info(f"Deleted {deletion_stats['comment_reports']} comment reports")
        except Exception as e:
            current_app.logger.warning(f"Could not delete comment reports for {content_type} {content_id}: {e}")
            deletion_stats['comment_reports'] = 0

        # Delete comments on this content
        try:
            comments_deleted = db.session.execute(text("""
                DELETE FROM comment
                WHERE content_type = :content_type AND content_id = :content_id
            """), {"content_type": content_type, "content_id": content_id})
            deletion_stats['comments'] = comments_deleted.rowcount
            current_app.logger.info(f"Deleted {deletion_stats['comments']} comments")
        except Exception as e:
            current_app.logger.warning(f"Could not delete comments for {content_type} {content_id}: {e}")
            deletion_stats['comments'] = 0
        
        # 2. Delete ratings for this content
        try:
            ratings_deleted = db.session.execute(text("""
                DELETE FROM rating
                WHERE content_type = :content_type AND content_id = :content_id
            """), {"content_type": content_type, "content_id": content_id})
            deletion_stats['ratings'] = ratings_deleted.rowcount
            current_app.logger.info(f"Deleted {deletion_stats['ratings']} ratings")
        except Exception as e:
            current_app.logger.warning(f"Could not delete ratings for {content_type} {content_id}: {e}")
            deletion_stats['ratings'] = 0

        # 3. Delete reading history for this content
        try:
            reading_history_deleted = db.session.execute(text("""
                DELETE FROM reading_history
                WHERE content_type = :content_type AND content_id = :content_id
            """), {"content_type": content_type, "content_id": content_id})
            deletion_stats['reading_history'] = reading_history_deleted.rowcount
            current_app.logger.info(f"Deleted {deletion_stats['reading_history']} reading history records")
        except Exception as e:
            current_app.logger.warning(f"Could not delete reading history for {content_type} {content_id}: {e}")
            deletion_stats['reading_history'] = 0

        # 4. Delete user library entries for this content
        try:
            user_library_deleted = db.session.execute(text("""
                DELETE FROM user_library
                WHERE content_type = :content_type AND content_id = :content_id
            """), {"content_type": content_type, "content_id": content_id})
            deletion_stats['user_library'] = user_library_deleted.rowcount
            current_app.logger.info(f"Deleted {deletion_stats['user_library']} user library entries")
        except Exception as e:
            current_app.logger.warning(f"Could not delete user library entries for {content_type} {content_id}: {e}")
            deletion_stats['user_library'] = 0

        # 5. Delete share_log entries for this news content (only for news)
        if content_type == 'news':
            try:
                share_logs_deleted = db.session.execute(text("""
                    DELETE FROM share_log
                    WHERE news_id = :content_id
                """), {"content_id": content_id})
                deletion_stats['share_logs'] = share_logs_deleted.rowcount
                current_app.logger.info(f"Deleted {deletion_stats['share_logs']} share log entries")
            except Exception as e:
                current_app.logger.warning(f"Could not delete share log entries: {e}")
                deletion_stats['share_logs'] = 0

        # 6. Delete content edit requests for this content (only for news)
        if content_type == 'news':
            try:
                edit_requests_deleted = db.session.execute(text("""
                    DELETE FROM content_edit_requests
                    WHERE news_id = :content_id
                """), {"content_id": content_id})
                deletion_stats['edit_requests'] = edit_requests_deleted.rowcount
                current_app.logger.info(f"Deleted {deletion_stats['edit_requests']} content edit requests")
            except Exception as e:
                current_app.logger.warning(f"Could not delete content edit requests (table may not exist): {e}")
                deletion_stats['edit_requests'] = 0

            # Delete editor edit requests for this news
            try:
                editor_requests_deleted = db.session.execute(text("""
                    DELETE FROM editor_edit_requests
                    WHERE news_id = :content_id
                """), {"content_id": content_id})
                deletion_stats['editor_edit_requests'] = editor_requests_deleted.rowcount
                current_app.logger.info(f"Deleted {deletion_stats['editor_edit_requests']} editor edit requests")
            except Exception as e:
                current_app.logger.warning(f"Could not delete editor edit requests: {e}")

        # 7. For albums, delete chapters and edit requests
        if content_type == 'album':
            try:
                chapters_deleted = db.session.execute(text("""
                    DELETE FROM album_chapter
                    WHERE album_id = :content_id
                """), {"content_id": content_id})
                deletion_stats['chapters'] = chapters_deleted.rowcount
                current_app.logger.info(f"Deleted {deletion_stats['chapters']} album chapters")
            except Exception as e:
                current_app.logger.warning(f"Could not delete album chapters for album {content_id}: {e}")
                deletion_stats['chapters'] = 0

            # Delete album edit requests
            try:
                album_edits_deleted = db.session.execute(text("""
                    DELETE FROM album_edit_requests
                    WHERE album_id = :content_id
                """), {"content_id": content_id})
                deletion_stats['album_edit_requests'] = album_edits_deleted.rowcount
                current_app.logger.info(f"Deleted {deletion_stats['album_edit_requests']} album edit requests")
            except Exception as e:
                current_app.logger.warning(f"Could not delete album edit requests: {e}")

        
        # Commit all the related data deletions
        db.session.commit()
        
        total_related_deleted = sum([
            deletion_stats['comments'],
            deletion_stats['comment_likes'],
            deletion_stats['comment_reports'],
            deletion_stats['ratings'],
            deletion_stats['reading_history'],
            deletion_stats['user_library'],
            deletion_stats.get('share_logs', 0),
            deletion_stats.get('edit_requests', 0)
        ])

        if content_type == 'album':
            total_related_deleted += deletion_stats.get('chapters', 0)
        if content_type == 'news':
            total_related_deleted += deletion_stats.get('share_logs', 0)
        
        current_app.logger.info(
            f"Successfully deleted {total_related_deleted} related records for {content_type} ID {content_id}"
        )

        # Optional verification: Check for orphaned data related to this specific content
        try:
            if content_type == 'news':
                # Check if any comments, ratings, etc. still reference this news ID
                orphaned_check = {
                    'comments': db.session.execute(text("SELECT COUNT(*) FROM comment WHERE content_type = 'news' AND content_id = :cid"), {"cid": content_id}).fetchone()[0],
                    'ratings': db.session.execute(text("SELECT COUNT(*) FROM rating WHERE content_type = 'news' AND content_id = :cid"), {"cid": content_id}).fetchone()[0],
                    'reading_history': db.session.execute(text("SELECT COUNT(*) FROM reading_history WHERE content_type = 'news' AND content_id = :cid"), {"cid": content_id}).fetchone()[0],
                    'user_library': db.session.execute(text("SELECT COUNT(*) FROM user_library WHERE content_type = 'news' AND content_id = :cid"), {"cid": content_id}).fetchone()[0]
                }
            elif content_type == 'album':
                orphaned_check = {
                    'comments': db.session.execute(text("SELECT COUNT(*) FROM comment WHERE content_type = 'album' AND content_id = :cid"), {"cid": content_id}).fetchone()[0],
                    'ratings': db.session.execute(text("SELECT COUNT(*) FROM rating WHERE content_type = 'album' AND content_id = :cid"), {"cid": content_id}).fetchone()[0],
                    'reading_history': db.session.execute(text("SELECT COUNT(*) FROM reading_history WHERE content_type = 'album' AND content_id = :cid"), {"cid": content_id}).fetchone()[0],
                    'user_library': db.session.execute(text("SELECT COUNT(*) FROM user_library WHERE content_type = 'album' AND content_id = :cid"), {"cid": content_id}).fetchone()[0]
                }

            total_orphaned_for_content = sum(orphaned_check.values())
            if total_orphaned_for_content > 0:
                current_app.logger.warning(
                    f"Orphaned data still exists for {content_type} ID {content_id}: {orphaned_check}"
                )
                deletion_stats['orphaned_data_found'] = orphaned_check
            else:
                current_app.logger.debug(f"No orphaned data found for deleted {content_type} ID {content_id}")

        except Exception as verify_error:
            current_app.logger.warning(f"Could not verify orphaned data for {content_type} ID {content_id}: {verify_error}")

        # Clear relevant caches to prevent stale content being served
        try:
            from optimizations import invalidate_cache_pattern, cache_public_content, cache_frontend_critical

            if content_type == 'news':
                # Clear news-related caches
                cache_public_content.clear()
                cache_frontend_critical.clear()
                # Invalidate specific news cache patterns
                invalidate_cache_pattern("news_*")
                invalidate_cache_pattern("chapter_*")
                current_app.logger.info(f"Cleared caches for deleted news ID {content_id}")

            elif content_type == 'album':
                # Clear album-related caches
                cache_public_content.clear()
                cache_frontend_critical.clear()
                # Invalidate specific album cache patterns
                invalidate_cache_pattern("album_*")
                invalidate_cache_pattern("chapter_*")
                current_app.logger.info(f"Cleared caches for deleted album ID {content_id}")

        except Exception as cache_error:
            current_app.logger.warning(f"Could not clear caches for deleted {content_type} {content_id}: {cache_error}")
            # Don't fail the deletion if cache clearing fails

        return deletion_stats

    except Exception as e:
        current_app.logger.error(f"Error deleting related data for {content_type} ID {content_id}: {e}")
        db.session.rollback()
        raise


def delete_user_completely(user_id, transfer_user_id=None):
    """
    Completely delete a user and all their associated data.

    Args:
        user_id (int): ID of the user to delete
        transfer_user_id (int, optional): ID of user to transfer ownership to. If None, deletes everything.

    Returns:
        dict: Statistics about what was deleted
    """
    import os

    deletion_stats = {
        'user_activities': 0,
        'reading_history': 0,
        'user_library': 0,
        'comments': 0,
        'ratings': 0,
        'comment_likes': 0,
        'comment_reports': 0,
        'achievements': 0,
        'streaks': 0,
        'points': 0,
        'coins': 0,
        'coin_transactions': 0,
        'payment_sessions': 0,
        'profile': 0,
        'stats': 0,
        'news': 0,
        'albums': 0,
        'images': 0,
        'videos': 0,
        'social_media': 0,
        'files_cleaned': 0
    }

    try:
        current_app.logger.info(f"Starting complete user deletion for user ID {user_id}")

        # 1. Get user and check if they exist
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        # 2. Handle ownership transfer vs complete deletion
        if transfer_user_id:
            # Transfer ownership of content
            transfer_user = User.query.get(transfer_user_id)
            if not transfer_user:
                raise ValueError(f"Transfer user with ID {transfer_user_id} not found")

            # Transfer main content ownership
            News.query.filter_by(user_id=user_id).update({News.user_id: transfer_user_id}, synchronize_session=False)
            Album.query.filter_by(user_id=user_id).update({Album.user_id: transfer_user_id}, synchronize_session=False)
            Image.query.filter_by(user_id=user_id).update({Image.user_id: transfer_user_id}, synchronize_session=False)
            YouTubeVideo.query.filter_by(user_id=user_id).update({YouTubeVideo.user_id: transfer_user_id}, synchronize_session=False)

            # Transfer social media ownership
            SocialMedia.query.filter_by(created_by=user_id).update({SocialMedia.created_by: transfer_user_id}, synchronize_session=False)
            SocialMedia.query.filter_by(updated_by=user_id).update({SocialMedia.updated_by: transfer_user_id}, synchronize_session=False)

            deletion_stats['news_transferred'] = News.query.filter_by(user_id=transfer_user_id).count() - deletion_stats.get('news_transferred', 0)
            deletion_stats['albums_transferred'] = Album.query.filter_by(user_id=transfer_user_id).count() - deletion_stats.get('albums_transferred', 0)
            deletion_stats['images_transferred'] = Image.query.filter_by(user_id=transfer_user_id).count() - deletion_stats.get('images_transferred', 0)
            deletion_stats['videos_transferred'] = YouTubeVideo.query.filter_by(user_id=transfer_user_id).count() - deletion_stats.get('videos_transferred', 0)
        else:
            # Complete deletion - delete all user's content
            # Delete news and related data
            news_items = News.query.filter_by(user_id=user_id).all()
            for news in news_items:
                delete_content_with_related_data('news', news.id, news.title)
                deletion_stats['news'] += 1

            # Delete albums and related data
            albums = Album.query.filter_by(user_id=user_id).all()
            for album in albums:
                delete_content_with_related_data('album', album.id, album.title)
                deletion_stats['albums'] += 1

            # Delete images (files will be cleaned up by SQLAlchemy event)
            images_deleted = Image.query.filter_by(user_id=user_id).delete()
            deletion_stats['images'] = images_deleted

            # Delete videos
            videos_deleted = YouTubeVideo.query.filter_by(user_id=user_id).delete()
            deletion_stats['videos'] = videos_deleted

            # Delete social media items
            social_deleted = SocialMedia.query.filter(
                (SocialMedia.created_by == user_id) | (SocialMedia.updated_by == user_id)
            ).delete()
            deletion_stats['social_media'] = social_deleted

        # 3. Delete / clean up user-specific data (always delete these regardless of transfer)
        # Delete user activities
        activities_deleted = UserActivity.query.filter_by(user_id=user_id).delete()
        deletion_stats['user_activities'] = activities_deleted

        # Delete reading history
        reading_deleted = ReadingHistory.query.filter_by(user_id=user_id).delete()
        deletion_stats['reading_history'] = reading_deleted

        # Delete user library
        library_deleted = UserLibrary.query.filter_by(user_id=user_id).delete()
        deletion_stats['user_library'] = library_deleted

        # Delete user's comments and related data
        comments = Comment.query.filter_by(user_id=user_id).all()
        for comment in comments:
            # Delete comment likes and reports for this comment
            CommentLike.query.filter_by(comment_id=comment.id).delete()
            CommentReport.query.filter_by(comment_id=comment.id).delete()
            deletion_stats['comment_likes'] += CommentLike.query.filter_by(comment_id=comment.id).count()
            deletion_stats['comment_reports'] += CommentReport.query.filter_by(comment_id=comment.id).count()

        comments_deleted = Comment.query.filter_by(user_id=user_id).delete()
        deletion_stats['comments'] = comments_deleted

        # Delete user's ratings
        ratings_deleted = Rating.query.filter_by(user_id=user_id).delete()
        deletion_stats['ratings'] = ratings_deleted

        # Delete user's comment likes and reports (as reporter)
        comment_likes_deleted = CommentLike.query.filter_by(user_id=user_id).delete()
        comment_reports_deleted = CommentReport.query.filter_by(user_id=user_id).delete()
        deletion_stats['comment_likes'] += comment_likes_deleted
        deletion_stats['comment_reports'] += comment_reports_deleted

        # Delete achievement system data
        achievements_deleted = UserAchievement.query.filter_by(user_id=user_id).delete()
        streaks_deleted = UserStreak.query.filter_by(user_id=user_id).delete()
        points_deleted = UserPoints.query.filter_by(user_id=user_id).delete()
        deletion_stats['achievements'] = achievements_deleted
        deletion_stats['streaks'] = streaks_deleted
        deletion_stats['points'] = points_deleted

        # Delete coin system data
        coins_deleted = UserCoins.query.filter_by(user_id=user_id).delete()
        coin_transactions_deleted = CoinTransaction.query.filter_by(user_id=user_id).delete()
        deletion_stats['coins'] = coins_deleted
        deletion_stats['coin_transactions'] = coin_transactions_deleted

        # Delete payment sessions
        payments_deleted = PaymentSession.query.filter_by(user_id=user_id).delete()
        deletion_stats['payment_sessions'] = payments_deleted

        # Delete write access records
        write_access_deleted = WriteAccessRequest.query.filter_by(user_id=user_id).delete()
        deletion_stats['write_access_requests'] = write_access_deleted

        # Clear reviewer references to this user in write access requests
        WriteAccessRequest.query.filter_by(reviewed_by_id=user_id).update(
            {WriteAccessRequest.reviewed_by_id: None}, synchronize_session=False
        )

        # Delete content/album/editor edit requests involving this user
        content_edit_deleted = ContentEditRequest.query.filter(
            (ContentEditRequest.owner_id == user_id)
            | (ContentEditRequest.requester_id == user_id)
        ).delete(synchronize_session=False)
        deletion_stats['content_edit_requests'] = content_edit_deleted

        album_edit_deleted = AlbumEditRequest.query.filter(
            (AlbumEditRequest.owner_id == user_id)
            | (AlbumEditRequest.requester_id == user_id)
        ).delete(synchronize_session=False)
        deletion_stats['album_edit_requests'] = album_edit_deleted

        editor_edit_deleted = EditorEditRequest.query.filter(
            (EditorEditRequest.editor_id == user_id)
            | (EditorEditRequest.author_id == user_id)
        ).delete(synchronize_session=False)
        deletion_stats['editor_edit_requests'] = editor_edit_deleted

        # Delete subscriptions owned by this user
        subscriptions_deleted = UserSubscription.query.filter_by(user_id=user_id).delete()
        deletion_stats['subscriptions'] = subscriptions_deleted

        # Null out metadata foreign keys that should not block deletion
        CoinPackage.query.filter_by(created_by=user_id).update(
            {CoinPackage.created_by: None}, synchronize_session=False
        )
        CoinPackage.query.filter_by(updated_by=user_id).update(
            {CoinPackage.updated_by: None}, synchronize_session=False
        )

        EmailLog.query.filter_by(user_id=user_id).update(
            {EmailLog.user_id: None}, synchronize_session=False
        )

        EmailTemplate.query.filter_by(created_by=user_id).update(
            {EmailTemplate.created_by: None}, synchronize_session=False
        )

        # Delete user profile and stats
        profile_deleted = UserProfile.query.filter_by(user_id=user_id).delete()
        stats_deleted = UserStats.query.filter_by(user_id=user_id).delete()
        deletion_stats['profile'] = profile_deleted
        deletion_stats['stats'] = stats_deleted

        # 4. Clean up user files (profile picture, etc.)
        if user.profile_picture:
            try:
                # Assuming profile pictures are stored in static/uploads/ or similar
                if os.path.exists(user.profile_picture):
                    os.remove(user.profile_picture)
                    deletion_stats['files_cleaned'] += 1
                    current_app.logger.info(f"Deleted profile picture file: {user.profile_picture}")
            except (OSError, IOError) as e:
                current_app.logger.warning(f"Could not delete profile picture file {user.profile_picture}: {e}")

        # 5. Clean up following relationships
        # Remove user from followers and following
        db.session.execute(text("DELETE FROM user_follow WHERE follower_id = :uid OR following_id = :uid"), {"uid": user_id})

        # Clean up editor-writer relationships
        db.session.execute(text("DELETE FROM editor_writer WHERE editor_id = :uid OR writer_id = :uid"), {"uid": user_id})

        # 6. Finally delete the user record
        db.session.delete(user)
        db.session.commit()

        # Verify no orphaned data remains (optional, for validation)
        try:
            orphaned_data = verify_no_orphaned_data()
            total_orphaned = sum(orphaned_data.values())
            if total_orphaned > 0:
                current_app.logger.warning(
                    f"Orphaned data detected after user deletion: {orphaned_data}. "
                    f"This may indicate incomplete cleanup."
                )
                deletion_stats['orphaned_data_found'] = orphaned_data
            else:
                current_app.logger.info("No orphaned data detected after user deletion.")
        except Exception as verify_error:
            current_app.logger.warning(f"Could not verify orphaned data after user deletion: {verify_error}")

        current_app.logger.info(f"Successfully completed user deletion for user ID {user_id}. Stats: {deletion_stats}")
        return deletion_stats

    except Exception as e:
        current_app.logger.error(f"Error during complete user deletion for user ID {user_id}: {e}")
        db.session.rollback()
        raise


def verify_no_orphaned_data():
    """
    Verify that there are no orphaned comments, ratings, or other related data.

    Returns:
        dict: Count of any remaining orphaned data
    """
    orphaned_counts = {
        'comments': 0,
        'ratings': 0,
        'comment_likes': 0,
        'comment_reports': 0,
        'reading_history': 0,
        'user_library': 0
    }

    try:
        # Check for orphaned comments
        result = db.session.execute(text("""
            SELECT COUNT(*) FROM comment c
            LEFT JOIN news n ON c.content_type = 'news' AND c.content_id = n.id
            LEFT JOIN album a ON c.content_type = 'album' AND c.content_id = a.id
            WHERE n.id IS NULL AND a.id IS NULL
        """))
        orphaned_counts['comments'] = result.fetchone()[0]

        # Check for orphaned ratings
        result = db.session.execute(text("""
            SELECT COUNT(*) FROM rating r
            LEFT JOIN news n ON r.content_type = 'news' AND r.content_id = n.id
            LEFT JOIN album a ON r.content_type = 'album' AND r.content_id = a.id
            WHERE n.id IS NULL AND a.id IS NULL
        """))
        orphaned_counts['ratings'] = result.fetchone()[0]

        # Check for orphaned comment likes
        result = db.session.execute(text("""
            SELECT COUNT(*) FROM comment_like cl
            LEFT JOIN comment c ON cl.comment_id = c.id
            WHERE c.id IS NULL
        """))
        orphaned_counts['comment_likes'] = result.fetchone()[0]

        # Check for orphaned comment reports
        result = db.session.execute(text("""
            SELECT COUNT(*) FROM comment_report cr
            LEFT JOIN comment c ON cr.comment_id = c.id
            WHERE c.id IS NULL
        """))
        orphaned_counts['comment_reports'] = result.fetchone()[0]

        # Check for orphaned reading history
        result = db.session.execute(text("""
            SELECT COUNT(*) FROM reading_history rh
            LEFT JOIN news n ON rh.content_type = 'news' AND rh.content_id = n.id
            LEFT JOIN album a ON rh.content_type = 'album' AND rh.content_id = a.id
            WHERE n.id IS NULL AND a.id IS NULL
        """))
        orphaned_counts['reading_history'] = result.fetchone()[0]

        # Check for orphaned user library
        result = db.session.execute(text("""
            SELECT COUNT(*) FROM user_library ul
            LEFT JOIN news n ON ul.content_type = 'news' AND ul.content_id = n.id
            LEFT JOIN album a ON ul.content_type = 'album' AND ul.content_id = a.id
            WHERE n.id IS NULL AND a.id IS NULL
        """))
        orphaned_counts['user_library'] = result.fetchone()[0]

        return orphaned_counts

    except Exception as e:
        current_app.logger.error(f"Error verifying orphaned data: {e}")
        return orphaned_counts


def test_deletion_mechanisms():
    """
    Test function to verify deletion mechanisms are working properly.
    This can be called to validate that deletions are complete and no orphaned data remains.

    Returns:
        dict: Test results and any issues found
    """
    test_results = {
        'orphaned_data_check': {},
        'deletion_mechanism_tests': {},
        'recommendations': []
    }

    try:
        current_app.logger.info("Starting deletion mechanism tests...")

        # Test 1: Check for any existing orphaned data
        test_results['orphaned_data_check'] = verify_no_orphaned_data()
        total_orphaned = sum(test_results['orphaned_data_check'].values())

        if total_orphaned > 0:
            test_results['recommendations'].append(
                f"Found {total_orphaned} orphaned records that should be cleaned up. "
                f"Details: {test_results['orphaned_data_check']}"
            )
            current_app.logger.warning(f"Orphaned data detected: {test_results['orphaned_data_check']}")
        else:
            current_app.logger.info("No orphaned data detected - deletion mechanisms appear to be working correctly.")

        # Test 2: Validate that key deletion functions exist and are callable
        deletion_functions = [
            'delete_content_with_related_data',
            'delete_user_completely',
            'verify_no_orphaned_data'
        ]

        for func_name in deletion_functions:
            if hasattr(__import__(__name__), func_name):
                test_results['deletion_mechanism_tests'][func_name] = 'available'
            else:
                test_results['deletion_mechanism_tests'][func_name] = 'missing'
                test_results['recommendations'].append(f"Deletion function {func_name} is missing")

        # Test 3: Check database table existence for key tables
        key_tables = [
            'comment', 'rating', 'comment_like', 'comment_report',
            'reading_history', 'user_library', 'user_activity',
            'user_achievement', 'user_streak', 'user_points',
            'user_coins', 'coin_transaction', 'payment_session'
        ]

        missing_tables = []
        for table in key_tables:
            try:
                result = db.session.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
                result.fetchone()
            except Exception:
                missing_tables.append(table)

        if missing_tables:
            test_results['recommendations'].append(
                f"Some expected tables are missing: {missing_tables}. "
                "This may indicate incomplete database setup."
            )

        test_results['test_completed'] = True
        current_app.logger.info("Deletion mechanism tests completed.")

        return test_results

    except Exception as e:
        current_app.logger.error(f"Error during deletion mechanism tests: {e}")
        test_results['test_error'] = str(e)
        test_results['test_completed'] = False
        return test_results
