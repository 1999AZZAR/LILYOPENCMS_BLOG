"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Email Tasks for Celery
Asynchronous email sending tasks
"""

import logging
from datetime import datetime
from celery_app.celery_app import celery_app
from .email_service import email_service

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_async(self, to: str, subject: str, body: str, html_body: str = None, attachments: list = None,
                     email_type=None, user_id=None, template_name=None):
    """Asynchronous email sending task"""
    try:
        success = email_service.send_email(
            to=to,
            subject=subject,
            body=body,
            html_body=html_body,
            attachments=attachments,
            email_type=email_type,
            user_id=user_id,
            template_name=template_name
        )

        if not success:
            logger.error(f"Failed to send email to {to}: {subject}")
            # Retry if failed
            if self.request.retries < self.max_retries:
                raise self.retry(countdown=60 * (self.request.retries + 1))
            else:
                logger.error(f"Max retries exceeded for email to {to}")
                return False

        logger.info(f"Successfully sent email to {to}: {subject}")
        return True

    except Exception as exc:
        logger.error(f"Exception sending email to {to}: {exc}")
        # Retry on exception
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1), exc=exc)
        else:
            logger.error(f"Max retries exceeded for email to {to}: {exc}")
            return False

@celery_app.task(bind=True)
def send_bulk_emails_async(self, email_data_list: list):
    """Send multiple emails asynchronously"""
    results = []

    for email_data in email_data_list:
        try:
            success = email_service.send_email(**email_data)
            results.append({
                'to': email_data.get('to'),
                'subject': email_data.get('subject'),
                'success': success,
                'timestamp': datetime.now().isoformat()
            })

            # Small delay between emails to respect rate limits
            import time
            time.sleep(0.1)

        except Exception as exc:
            logger.error(f"Failed to send bulk email to {email_data.get('to')}: {exc}")
            results.append({
                'to': email_data.get('to'),
                'subject': email_data.get('subject'),
                'success': False,
                'error': str(exc),
                'timestamp': datetime.now().isoformat()
            })

    return results

@celery_app.task(bind=True, max_retries=5, default_retry_delay=300)
def send_verification_email_async(self, user_id: int, token: str):
    """Send verification email asynchronously"""
    try:
        from models import User
        from flask import current_app

        user = User.query.get(user_id)
        if not user:
            logger.error(f"User {user_id} not found for verification email")
            return False

        success = email_service.send_verification_email(user, token)

        if success:
            logger.info(f"Verification email sent to user {user_id}")
        else:
            logger.error(f"Failed to send verification email to user {user_id}")
            # Retry with longer delay
            if self.request.retries < self.max_retries:
                raise self.retry(countdown=300 * (self.request.retries + 1))

        return success

    except Exception as exc:
        logger.error(f"Exception sending verification email to user {user_id}: {exc}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=300 * (self.request.retries + 1), exc=exc)
        return False

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email_async(self, user_id: int, token: str):
    """Send password reset email asynchronously"""
    try:
        from models import User

        user = User.query.get(user_id)
        if not user:
            logger.error(f"User {user_id} not found for password reset email")
            return False

        success = email_service.send_password_reset_email(user, token)

        if success:
            logger.info(f"Password reset email sent to user {user_id}")
        else:
            logger.error(f"Failed to send password reset email to user {user_id}")
            if self.request.retries < self.max_retries:
                raise self.retry(countdown=60 * (self.request.retries + 1))

        return success

    except Exception as exc:
        logger.error(f"Exception sending password reset email to user {user_id}: {exc}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1), exc=exc)
        return False

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_chapter_published_notification_async(self, chapter_id: int, album_id: int, recipient_user_id: int):
    """Send chapter published notification asynchronously"""
    try:
        from models import AlbumChapter, Album, User

        chapter = AlbumChapter.query.get(chapter_id)
        album = Album.query.get(album_id)
        recipient_user = User.query.get(recipient_user_id)

        if not all([chapter, album, recipient_user]):
            logger.error(f"Chapter {chapter_id}, album {album_id}, or user {recipient_user_id} not found for chapter published notification")
            return False

        success = email_service.send_chapter_published_notification(chapter, album, recipient_user)

        if success:
            logger.info(f"Chapter published notification sent to user {recipient_user_id} for chapter {chapter_id}")
        else:
            logger.error(f"Failed to send chapter published notification to user {recipient_user_id} for chapter {chapter_id}")
            if self.request.retries < self.max_retries:
                raise self.retry(countdown=60 * (self.request.retries + 1))

        return success

    except Exception as exc:
        logger.error(f"Exception sending chapter published notification for chapter {chapter_id}: {exc}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1), exc=exc)
        return False

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_scheduled_content_published_notification_async(self, content_type: str, content_title: str,
                                                       content_location: str, scheduled_date_str: str,
                                                       actual_publish_date_str: str, author_user_id: int,
                                                       content_url: str):
    """Send scheduled content published notification asynchronously"""
    try:
        from models import User
        from datetime import datetime

        author_user = User.query.get(author_user_id)
        if not author_user:
            logger.error(f"User {author_user_id} not found for scheduled content published notification")
            return False

        # Parse dates
        scheduled_date = datetime.fromisoformat(scheduled_date_str) if scheduled_date_str != 'Tidak diketahui' else None
        actual_publish_date = datetime.fromisoformat(actual_publish_date_str)

        success = email_service.send_scheduled_content_published_notification(
            content_type=content_type,
            content_title=content_title,
            content_location=content_location,
            scheduled_date=scheduled_date,
            actual_publish_date=actual_publish_date,
            author_user=author_user,
            content_url=content_url
        )

        if success:
            logger.info(f"Scheduled content published notification sent to user {author_user_id} for content: {content_title}")
        else:
            logger.error(f"Failed to send scheduled content published notification to user {author_user_id} for content: {content_title}")
            if self.request.retries < self.max_retries:
                raise self.retry(countdown=60 * (self.request.retries + 1))

        return success

    except Exception as exc:
        logger.error(f"Exception sending scheduled content published notification for content '{content_title}': {exc}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1), exc=exc)
        return False
