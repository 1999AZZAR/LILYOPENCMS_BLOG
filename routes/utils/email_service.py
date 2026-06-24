"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Email Service for LilyOpenCMS
Handles SMTP configuration, email sending, and rate limiting
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from flask import current_app

if TYPE_CHECKING:
    from models import EmailType
from flask_mail import Mail, Message
import redis
import json
from .template_loader import email_template_loader
try:
    from celery_app.circuit_breaker import get_email_circuit_breaker, CircuitBreakerOpenException
except ImportError:
    class CircuitBreakerOpenException(Exception):
        pass

    class MockCircuitBreaker:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

        def __call__(self, f):
            return f

    def get_email_circuit_breaker():
        return MockCircuitBreaker()

from routes.utils.database_utils import retry_on_db_lock
from models import db

# Celery tasks will be imported lazily to avoid circular imports
CELERY_AVAILABLE = False
send_email_async = None
send_bulk_emails_async = None

class EmailService:
    """Email service with SMTP configuration and rate limiting"""

    def __init__(self, app=None):
        self.mail = None
        self.redis_client = None
        self.config = {}
        self.rate_limits = {}
        self._app = None
        self._initialized = False

        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize email service with Flask app"""
        self._app = app
        # Initialize template loader
        email_template_loader.init_app(app)
        # Store app reference but defer full initialization until needed
        # This prevents app context issues during Flask startup

    def _ensure_initialized(self):
        """Ensure email service is fully initialized with app context"""
        if self._initialized:
            return

        # Try to get current app if not set
        if not self._app:
            try:
                from flask import current_app
                self._app = current_app
            except RuntimeError:
                # No app context available
                return

        if not self._app:
            return

        try:
            # Load SMTP configuration with app context
            self.config = self._load_smtp_config(self._app)

            # Initialize Flask-Mail
            self._app.config.update(self._get_flask_mail_config())
            self.mail = Mail(self._app)

            # Initialize Redis for rate limiting
            self._init_redis()

            # Initialize rate limits
            self.rate_limits = {
                'per_hour': self.config.get('email_rate_limit_per_hour', 10),
                'per_day': self.config.get('email_rate_limit_per_day', 50)
            }

            self._app.logger.info("✅ Email service initialized successfully")
            self._initialized = True

        except Exception as e:
            self._app.logger.error(f"❌ Failed to initialize email service: {e}")
            # Fallback to logging mode
            self.mail = None
            self._initialized = True  # Mark as initialized to prevent retry loops
    
    def _load_smtp_config(self, app=None) -> Dict[str, Any]:
        """Load SMTP configuration from config file and environment variables"""
        config_file = "config/smtp_config.txt"
        config = self._get_default_config()

        # Load from file if exists
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            if value.lower() in ('true', 'false'):
                                config[key] = value.lower() == 'true'
                            elif value.isdigit():
                                config[key] = int(value)
                            elif value == '':
                                config[key] = None
                            else:
                                config[key] = value
            elif app:
                app.logger.info("ℹ️ SMTP config file not found, checking environment/defaults")
        except Exception as e:
            if app:
                app.logger.error(f"❌ Error reading SMTP config file: {e}")

        # Override/supplement with environment variables
        env_mappings = {
            'smtp_server': 'SMTP_SERVER',
            'smtp_port': 'SMTP_PORT',
            'smtp_username': 'SMTP_USERNAME',
            'smtp_password': 'SMTP_PASSWORD',
            'mail_default_sender': 'EMAIL_FROM',
            'mail_reply_to': 'EMAIL_FROM'
        }
        
        for config_key, env_key in env_mappings.items():
            val = os.getenv(env_key)
            if val is not None:
                if config_key == 'smtp_port' and val.isdigit():
                    config[config_key] = int(val)
                else:
                    config[config_key] = val

        # Handle boolean env vars
        suppress_send = os.getenv('MAIL_SUPPRESS_SEND')
        if suppress_send is not None:
            config['smtp_suppress_send'] = suppress_send.lower() == 'true'

        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default SMTP configuration"""
        return {
            'smtp_server': 'localhost',
            'smtp_port': 587,
            'smtp_use_tls': True,
            'smtp_use_ssl': False,
            'smtp_username': None,
            'smtp_password': None,
            'mail_default_sender': 'noreply@lilyopencms.com',
            'mail_sender_name': 'LilyOpenCMS',
            'mail_reply_to': 'noreply@lilyopencms.com',
            'email_rate_limit_per_hour': 10,
            'email_rate_limit_per_day': 50,
            'smtp_verify_ssl': True,
            'smtp_timeout': 30,
            'smtp_debug': False,
            'smtp_suppress_send': False
        }
    
    def _get_flask_mail_config(self) -> Dict[str, Any]:
        """Convert SMTP config to Flask-Mail format"""
        # Get brand info for sender name
        brand_info = self._get_brand_info()

        return {
            'MAIL_SERVER': self.config.get('smtp_server', 'localhost'),
            'MAIL_PORT': self.config.get('smtp_port', 587),
            'MAIL_USE_TLS': self.config.get('smtp_use_tls', True),
            'MAIL_USE_SSL': self.config.get('smtp_use_ssl', False),
            'MAIL_USERNAME': self.config.get('smtp_username'),
            'MAIL_PASSWORD': self.config.get('smtp_password'),
            'MAIL_DEFAULT_SENDER': self.config.get('mail_default_sender', 'noreply@hystory.id'),
            'MAIL_SUPPRESS_SEND': self.config.get('smtp_suppress_send', False),
            'MAIL_DEBUG': self.config.get('smtp_debug', False)
        }
    
    def _init_redis(self):
        """Initialize Redis client for rate limiting"""
        try:
            # Try to get Redis config from existing config reader
            from routes.utils.config_reader import get_redis_config
            redis_config = get_redis_config()
            
            if redis_config.get('connection_type') == 'socket':
                self.redis_client = redis.Redis(
                    unix_socket_path=redis_config.get('socket_path'),
                    socket_connect_timeout=redis_config.get('socket_connect_timeout', 1),
                    socket_timeout=redis_config.get('socket_timeout', 1)
                )
            else:
                self.redis_client = redis.Redis(
                    host=redis_config.get('host', 'localhost'),
                    port=redis_config.get('port', 6379),
                    password=redis_config.get('password'),
                    socket_connect_timeout=redis_config.get('tcp_connect_timeout', 2),
                    socket_timeout=redis_config.get('tcp_timeout', 2)
                )
            
            # Test connection
            self.redis_client.ping()
            import logging; logging.getLogger(__name__).info("✅ Redis connected for email rate limiting")
            
        except Exception as e:
            import logging; logging.getLogger(__name__).warning(f"⚠️ Redis not available for email rate limiting: {e}")
            self.redis_client = None
    
    def _check_rate_limit(self, recipient: str) -> bool:
        """Check if recipient is within rate limits"""
        if not self.redis_client:
            return True  # No rate limiting if Redis unavailable
        
        try:
            now = datetime.now()
            hour_key = f"email_rate:{recipient}:{now.strftime('%Y%m%d%H')}"
            day_key = f"email_rate:{recipient}:{now.strftime('%Y%m%d')}"
            
            # Check hourly limit
            hour_count = self.redis_client.get(hour_key)
            if hour_count and int(hour_count) >= self.rate_limits['per_hour']:
                return False
            
            # Check daily limit
            day_count = self.redis_client.get(day_key)
            if day_count and int(day_count) >= self.rate_limits['per_day']:
                return False
            
            return True
            
        except Exception as e:
            import logging; logging.getLogger(__name__).warning(f"⚠️ Rate limit check failed: {e}")
            return True  # Allow sending if rate limit check fails
    
    def _increment_rate_limit(self, recipient: str):
        """Increment rate limit counters"""
        if not self.redis_client:
            return
        
        try:
            now = datetime.now()
            hour_key = f"email_rate:{recipient}:{now.strftime('%Y%m%d%H')}"
            day_key = f"email_rate:{recipient}:{now.strftime('%Y%m%d')}"
            
            # Increment counters with expiration
            self.redis_client.incr(hour_key)
            self.redis_client.expire(hour_key, 3600)  # 1 hour
            
            self.redis_client.incr(day_key)
            self.redis_client.expire(day_key, 86400)  # 24 hours
            
        except Exception as e:
            import logging; logging.getLogger(__name__).warning(f"⚠️ Rate limit increment failed: {e}")
    
    @retry_on_db_lock(max_retries=3, delay=0.1)
    def send_email(self,
                   to: str,
                   subject: str,
                   body: str,
                   html_body: Optional[str] = None,
                   attachments: Optional[List[Dict]] = None,
                   async_send: bool = False,
                   email_type: 'EmailType' = None,
                   user_id: int = None,
                   template_name: str = None,
                   **context_kwargs) -> bool:
        """Send email with rate limiting and error handling"""

        # Ensure service is initialized
        self._ensure_initialized()

        # Import tracking models
        from models import EmailLog, EmailType, EmailStatus

        # Set default email type if not provided
        if email_type is None:
            email_type = EmailType.CUSTOM

        # Create email log entry
        email_log = EmailLog(
            recipient=to,
            sender=self.config.get('mail_default_sender', 'noreply@lilyopencms.com'),
            subject=subject,
            email_type=email_type,
            user_id=user_id,
            template_name=template_name,
            status=EmailStatus.QUEUED
        )

        # Check rate limits and log if hit
        rate_limit_exceeded = not self._check_rate_limit(to)
        if rate_limit_exceeded:
            email_log.rate_limit_hit = True
            email_log.rate_limit_reason = "Rate limit exceeded"
            email_log.status = EmailStatus.FAILED
            email_log.error_message = "Rate limit exceeded"
            db.session.add(email_log)
            db.session.commit()
            logging.getLogger(__name__).warning(f"⚠️ Rate limit exceeded for {to}")
            return False

        # Add log to database
        db.session.add(email_log)
        db.session.commit()

        # If template_name is provided, render the template
        if template_name:
            try:
                # Get brand info for context
                brand_info = self._get_brand_info()

                # Build context with user info if user_id provided
                context = {
                    'brand_name': brand_info.brand_name,
                    'tagline': brand_info.tagline,
                }

                # Add user info if user_id is provided
                if user_id:
                    from models import User
                    user = User.query.get(user_id)
                    if user:
                        context['user'] = user

                # Add any additional context data passed as kwargs
                context.update(context_kwargs)

                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Rendering email template: {template_name}")
                logger.info(f"Template context keys: {list(context.keys())}")
                logger.info(f"Template context kwargs: {list(context_kwargs.keys())}")

                # Get base URL dynamically
                base_url = self._get_base_url()

                # Only add demo fallbacks in development/debug mode
                # In production, emails should provide complete real data
                from flask import current_app
                is_debug = current_app.config.get('DEBUG', False) or current_app.config.get('TESTING', False)

                if is_debug or template_name is None:
                    # Add demo values for testing/development only
                    context.setdefault('verify_url', f'{base_url}/verify/demo-token')
                    context.setdefault('reset_url', f'{base_url}/reset/demo-token')
                    context.setdefault('changes', ['Profile updated for testing'])
                    context.setdefault('approval_date', '2025-11-17')
                    context.setdefault('admin_name', 'Admin User')
                    context.setdefault('rejection_reason', 'Demo rejection reason')
                    context.setdefault('appeal_url', f'{base_url}/appeal')
                    context.setdefault('suspension_reason', 'Demo suspension reason')
                    context.setdefault('suspension_duration', '7 days')
                    context.setdefault('content_title', 'Demo Content Title')
                    context.setdefault('content_type_id', 'article')
                    context.setdefault('reason', 'Demo rejection reason')
                    context.setdefault('feedback', 'Demo feedback message')
                    context.setdefault('resubmit_url', f'{base_url}/resubmit')
                    context.setdefault('published_url', f'{base_url}/demo-content')
                    context.setdefault('review_date', '2025-11-17')
                    context.setdefault('deletion_reason', 'Demo deletion reason')
                    context.setdefault('deletion_date', '2025-11-20')
                    context.setdefault('original_title', 'Demo Original Title')
                    context.setdefault('edit_summary', 'Demo edit summary')
                    context.setdefault('request_date', '2025-11-17')
                    context.setdefault('cancel_url', f'{base_url}/cancel')
                    context.setdefault('reactivation_info', 'Contact support to reactivate')
                # In production, require complete context - no fallbacks

                # Render template
                html_body, body = email_template_loader.get_html_and_text(template_name, context)

                # Override the provided body and html_body with rendered template
                body = body
                html_body = html_body

            except Exception as e:
                import logging; logging.getLogger(__name__).error(f"❌ Failed to render email template '{template_name}': {e}")
                # Continue with original body/html_body if template rendering fails

        # If async sending is requested and Celery is available
        if async_send:
            try:
                from .email_tasks import send_email_async as async_task
                if async_task:
                    # Queue email for async sending
                    task = async_task.delay(
                        to=to,
                        subject=subject,
                        body=body,
                        html_body=html_body,
                        attachments=attachments,
                        email_type=email_type,
                        user_id=user_id,
                        template_name=template_name
                    )
                    import logging; logging.getLogger(__name__).info(f"📧 Email queued for async sending to {to}: {subject} (task: {task.id})")
                    return True
            except Exception as e:
                import logging; logging.getLogger(__name__).warning(f"⚠️ Failed to queue email async, falling back to sync: {e}")
                # Fall back to synchronous sending

        if not self.mail:
            logger = logging.getLogger(__name__)
            logger.info(f"📧 Email service not available (SMTP disabled): To: {to}, Subject: {subject}")
            logger.info(f"📧 EMAIL DETAILS: From: {self.config.get('mail_default_sender')}, Server: {self.config.get('smtp_server')}")
            logger.info(f"📧 EMAIL BODY:\n{body}")
            for line in body.splitlines():
                if 'http' in line:
                    logger.info(f"🔗 Link: {line.strip()}")
            return True

        # Check rate limits
        if not self._check_rate_limit(to):
            logging.getLogger(__name__).warning(f"⚠️ Rate limit exceeded for {to}")
            return False
        
        try:
            # Get brand info for sender name
            brand_info = self._get_brand_info()

            # Create message
            msg = Message(
                subject=subject,
                recipients=[to],
                body=body,
                html=html_body,
                sender=f"{brand_info.brand_name} <{self.config.get('mail_default_sender', 'noreply@hystory.id')}>"
            )
            
            # Add reply-to header
            if self.config.get('mail_reply_to'):
                msg.reply_to = self.config.get('mail_reply_to')
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    with open(attachment['file_path'], 'rb') as f:
                        msg.attach(
                            filename=attachment['filename'],
                            content_type=attachment.get('content_type', 'application/octet-stream'),
                            data=f.read()
                        )
            
            # Send email with circuit breaker protection
            import logging
            logger = logging.getLogger(__name__)

            # Get circuit breaker for email service
            circuit_breaker = get_email_circuit_breaker()

            def _send_email_via_smtp():
                """Send email via SMTP - wrapped for circuit breaker."""
                logger.info(f"Sending email via SMTP to {to} with subject: {subject}")
                self.mail.send(msg)
                logger.info(f"SMTP send completed for {to}")
                return True

            # Send email through circuit breaker
            try:
                circuit_breaker.call(_send_email_via_smtp)
            except CircuitBreakerOpenException as e:
                logger.error(f"❌ Email circuit breaker is OPEN, cannot send email to {to}: {e}")
                raise Exception(f"Email service temporarily unavailable: {e}")
            except Exception as e:
                # Re-raise other exceptions (they will be caught by the outer try block)
                raise

            # Update email log status to sent
            email_log.update_status(EmailStatus.SENT)

            # Increment rate limit
            self._increment_rate_limit(to)

            logger.info(f"✅ Email sent successfully to {to}: {subject}")
            logger.info(f"✅ SMTP Config used: Server={self.config.get('smtp_server')}, Port={self.config.get('smtp_port')}, TLS={self.config.get('smtp_use_tls')}")
            return True
            
        except Exception as e:
            # Update email log status to failed
            email_log.update_status(EmailStatus.FAILED, str(e))
            logger.error(f"❌ Failed to send email to {to}: {e}")
            return False
    
    def send_verification_email(self, user, token: str) -> bool:
        """Send email verification email"""
        # Get brand information from database
        brand_info = self._get_brand_info()

        base_url = self._get_base_url()
        verify_url = f"{base_url}/verify-email?token={token}"
        subject = f"Verifikasi Email Anda - {brand_info.brand_name}"

        # Import for email type
        from models import EmailType

        return self.send_email(
            to=user.email,
            subject=subject,
            body="",  # Will be filled by template
            html_body="",  # Will be filled by template
            email_type=EmailType.VERIFICATION,
            user_id=user.id,
            template_name='verification_email',
            # Pass additional context data
            verify_url=verify_url
        )

    def send_account_verified_email(self, user) -> bool:
        """Send account verified confirmation email"""
        # Get brand information from database
        brand_info = self._get_brand_info()

        base_url = self._get_base_url()
        login_url = f"{base_url}/login"
        subject = f"Akun Anda Telah Diverifikasi - {brand_info.brand_name}"

        return self.send_email(
            to=user.email,
            subject=subject,
            body="",  # Will be filled by template
            html_body="",  # Will be filled by template
            template_name='account_verified',
            user_id=user.id,
            login_url=login_url
        )

    def send_password_reset_email(self, user, token: str) -> bool:
        """Send password reset email"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Sending password reset email to {user.email} for user {user.username}")

        # Get brand information from database
        brand_info = self._get_brand_info()

        base_url = self._get_base_url()
        reset_url = f"{base_url}/reset-password?token={token}"
        subject = f"Reset Kata Sandi Anda - {brand_info.brand_name}"

        logger.info(f"Password reset URL: {reset_url}")

        result = self.send_email(
            to=user.email,
            subject=subject,
            body="",  # Will be filled by template
            html_body="",  # Will be filled by template
            template_name='password_reset_email',
            user_id=user.id,
            reset_url=reset_url
        )

        if result:
            logger.info(f"Password reset email sent successfully to {user.email}")
        else:
            logger.error(f"Failed to send password reset email to {user.email}")

        return result

    def send_suspension_notification(self, user, reason: str = None, duration_days: int = None) -> bool:
        """Send account suspension notification email"""
        # Ensure service is initialized
        self._ensure_initialized()

        import logging
        logger = logging.getLogger(__name__)

        if not user.email:
            logger.info(f"Skipping suspension email for {user.username} - no email address")
            return False

        logger.info(f"Sending suspension email to {user.email} for user {user.username}")

        # Get brand information from database
        brand_info = self._get_brand_info()

        subject = f"Akun Anda Ditangguhkan - {brand_info.brand_name}"

        result = self.send_email(
            to=user.email,
            subject=subject,
            body="",  # Will be filled by template
            html_body="",  # Will be filled by template
            template_name='suspension_notification',
            user_id=user.id,
            reason=reason,
            duration_days=duration_days
        )

        if result:
            logger.info(f"Suspension email sent successfully to {user.email}")
        else:
            logger.error(f"Failed to send suspension email to {user.email}")

        return result

    def send_write_access_approved_notification(self, user) -> bool:
        """Send write access approved notification email"""
        # Ensure service is initialized
        self._ensure_initialized()

        if not user.email:
            return False

        # Get brand information from database
        brand_info = self._get_brand_info()

        subject = f"Permintaan Akses Tulis Disetujui - {brand_info.brand_name}"

        base_url = self._get_base_url()

        return self.send_email(
            to=user.email,
            subject=subject,
            body="",  # Will be filled by template
            html_body="",  # Will be filled by template
            template_name='write_access_approved',
            user_id=user.id,
            login_url=f"{base_url}/login"
        )

    def send_write_access_rejected_notification(self, user, reason: str = None) -> bool:
        """Send write access rejected notification email"""
        # Ensure service is initialized
        self._ensure_initialized()

        if not user.email:
            return False

        # Get brand information from database
        brand_info = self._get_brand_info()

        subject = f"Permintaan Akses Tulis Ditolak - {brand_info.brand_name}"

        return self.send_email(
            to=user.email,
            subject=subject,
            body="",  # Will be filled by template
            html_body="",  # Will be filled by template
            template_name='write_access_rejected',
            user_id=user.id,
            reason=reason
        )

    def send_account_deletion_request_notification(self, user) -> bool:
        """Send account deletion request notification email"""
        # Ensure service is initialized
        self._ensure_initialized()

        if not user.email:
            return False

        # Get brand information from database
        brand_info = self._get_brand_info()

        subject = f"Permintaan Hapus Akun - {brand_info.brand_name}"

        return self.send_email(
            to=user.email,
            subject=subject,
            body="",  # Will be filled by template
            html_body="",  # Will be filled by template
            template_name='account_deletion_request',
            user_id=user.id
        )

    def send_account_deletion_confirmation(self, user) -> bool:
        """Send account deletion confirmation email"""
        # Ensure service is initialized
        self._ensure_initialized()

        if not user.email:
            return False

        # Get brand information from database
        brand_info = self._get_brand_info()

        subject = f"Akun Berhasil Dihapus - {brand_info.brand_name}"

        return self.send_email(
            to=user.email,
            subject=subject,
            body="",  # Will be filled by template
            html_body="",  # Will be filled by template
            template_name='account_deletion_confirmation',
            user_id=user.id
        )

    def send_content_deletion_notification(self, user, content_type: str, content_title: str) -> bool:
        """Send content deletion notification email"""
        # Ensure service is initialized
        self._ensure_initialized()

        if not user.email:
            return False

        # Get brand information from database
        brand_info = self._get_brand_info()

        subject = f"Konten Dihapus - {brand_info.brand_name}"

        content_type_id = {
            'news': 'artikel',
            'album': 'album',
            'image': 'gambar',
            'video': 'video'
        }.get(content_type.lower(), 'konten')

        return self.send_email(
            to=user.email,
            subject=subject,
            body="",  # Will be filled by template
            html_body="",  # Will be filled by template
            template_name='content_deletion_notification',
            user_id=user.id,
            content_type_id=content_type_id,
            content_title=content_title,
            deletion_date=datetime.now().strftime('%d %B %Y')
        )

    def send_content_approved_notification(self, user, content_type: str, content_title: str) -> bool:
        """Send content approved notification email"""
        if not user.email:
            return False

        # Get brand information from database
        brand_info = self._get_brand_info()

        subject = f"Konten Disetujui - {brand_info.brand_name}"

        content_type_id = {
            'news': 'artikel',
            'album': 'album',
            'image': 'gambar',
            'video': 'video'
        }.get(content_type.lower(), 'konten')

        return self.send_email(
            to=user.email,
            subject=subject,
            body="",  # Will be filled by template
            html_body="",  # Will be filled by template
            template_name='content_approved_notification',
            user_id=user.id,
            content_type_id=content_type_id,
            content_title=content_title,
            approval_date=datetime.now().strftime('%d %B %Y')
        )

    def send_content_rejected_notification(self, user, content_type: str, content_title: str, reason: str = None) -> bool:
        """Send content rejected notification email"""
        if not user.email:
            return False

        # Get brand information from database
        brand_info = self._get_brand_info()

        subject = f"Konten Ditolak - {brand_info.brand_name}"

        content_type_id = {
            'news': 'artikel',
            'album': 'album',
            'image': 'gambar',
            'video': 'video'
        }.get(content_type.lower(), 'konten')

        return self.send_email(
            to=user.email,
            subject=subject,
            body="",  # Will be filled by template
            html_body="",  # Will be filled by template
            template_name='content_rejected_notification',
            user_id=user.id,
            content_type_id=content_type_id,
            content_title=content_title,
            rejection_date=datetime.now().strftime('%d %B %Y'),
            reason=reason
        )

    def send_profile_update_confirmation(self, user, updated_fields: list) -> bool:
        """Send profile update confirmation email"""
        if not user.email:
            return False

        # Get brand information from database
        brand_info = self._get_brand_info()

        subject = f"Profil Diperbarui - {brand_info.brand_name}"

        return self.send_email(
            to=user.email,
            subject=subject,
            body="",  # Will be filled by template
            html_body="",  # Will be filled by template
            template_name='profile_update_confirmation',
            user_id=user.id,
            updated_fields=updated_fields
        )

    def send_edit_request_approved_notification(self, user, content_type: str, content_title: str) -> bool:
        """Send edit request approved notification email"""
        if not user.email:
            return False

        # Get brand information from database
        brand_info = self._get_brand_info()

        subject = f"Permintaan Edit Disetujui - {brand_info.brand_name}"

        content_type_id = {
            'news': 'artikel',
            'album': 'album'
        }.get(content_type.lower(), 'konten')

        base_url = self._get_base_url()

        return self.send_email(
            to=user.email,
            subject=subject,
            body="",  # Will be filled by template
            html_body="",  # Will be filled by template
            template_name='edit_request_approved',
            user_id=user.id,
            content_type_id=content_type_id,
            content_title=content_title,
            approval_date=datetime.now().strftime('%d %B %Y'),
            edit_url=f"{base_url}/user/{user.username}/editor-requests"
        )

    def send_edit_request_rejected_notification(self, user, content_type: str, content_title: str, reason: str = None) -> bool:
        """Send edit request rejected notification email"""
        if not user.email:
            return False

        # Get brand information from database
        brand_info = self._get_brand_info()

        subject = f"Permintaan Edit Ditolak - {brand_info.brand_name}"

        content_type_id = {
            'news': 'artikel',
            'album': 'album'
        }.get(content_type.lower(), 'konten')

        return self.send_email(
            to=user.email,
            subject=subject,
            body="",  # Will be filled by template
            html_body="",  # Will be filled by template
            template_name='edit_request_rejected',
            user_id=user.id,
            content_type_id=content_type_id,
            content_title=content_title,
            review_date=datetime.now().strftime('%d %B %Y'),
            rejection_reason=reason
        )

    def send_album_edit_request_submitted_notification(self, requester, album_title: str, reason: str) -> bool:
        """Send notification to admins when user submits album edit request."""
        subject = f"Permintaan Edit Album: {album_title}"

        # Import for email type
        from models import EmailType

        # Get brand info
        brand_info = self._get_brand_info()
        base_url = self._get_base_url()

        # Send to all admin users
        from models import User, UserRole
        admin_users = User.query.filter(
            (User.role.in_([UserRole.ADMIN, UserRole.SUPERUSER])) |
            (User.custom_role.has(UserRole.name.in_(['admin', 'superuser'])))
        ).all()

        success_count = 0
        for admin in admin_users:
            try:
                self.send_email(
                    to=admin.email,
                    subject=subject,
                    body="",  # Will be filled by template
                    html_body="",  # Will be filled by template
                    email_type=EmailType.ALBUM_EDIT_REQUEST_SUBMITTED,
                    template_name='album_edit_request_submitted',
                    requester_username=requester.username,
                    album_title=album_title,
                    reason=reason,
                    admin_url=f"{base_url}/admin/settings/content-edit-requests",
                    brand_info=brand_info
                )
                success_count += 1
            except Exception as e:
                current_app.logger.warning(f"Failed to send album edit request notification to {admin.email}: {e}")

        return success_count > 0

    def send_editor_edit_request_notification(self, edit_request) -> bool:
        """Send notification to author when editor sends edit request"""
        try:
            author = edit_request.news.author
            editor = edit_request.editor

            if not author.email:
                return False

            # Import for email type
            from models import EmailType

            # Get brand information from database
            brand_info = self._get_brand_info()

            urgency_text = " (URGENT)" if edit_request.is_urgent else ""
            subject = f"Permintaan Edit dari Editor - {brand_info.brand_name}{urgency_text}"

            content_type = "Chapter in Album" if edit_request.news.album_chapters else "Article"
            base_url = self._get_base_url()

            return self.send_email(
                to=author.email,
                subject=subject,
                body="",  # Will be filled by template
                html_body="",  # Will be filled by template
                email_type=EmailType.EDITOR_EDIT_REQUEST_NOTIFICATION,
                user_id=author.id,
                template_name='editor_edit_request_notification',
                author_full_name=author.get_full_name() or author.username,
                editor_username=editor.username,
                content_title=edit_request.news.title,
                content_type=content_type,
                request_date=edit_request.created_at.strftime('%d %B %Y, %H:%M'),
                is_urgent=edit_request.is_urgent,
                editor_message=edit_request.message,
                editor_requests_url=f"{base_url}/user/{author.username}/editor-requests",
                brand_info=brand_info
            )
        except Exception as e:
            current_app.logger.error(f"Error sending editor edit request notification: {e}")
            return False

    def send_chapter_published_notification(self, chapter, album, recipient_user) -> bool:
        """Send notification when a chapter is published"""
        if not recipient_user.email:
            return False

        # Check user notification preferences
        user_prefs = recipient_user.email_notifications or {}
        if not user_prefs.get('chapter_published', True):
            return False  # User has opted out of chapter published notifications

        # Get brand information from database
        brand_info = self._get_brand_info()

        subject = f"Chapter Baru: {chapter.chapter_title} - {brand_info.brand_name}"

        base_url = self._get_base_url()
        chapter_url = f"{base_url}/album/{album.id}/chapter/{chapter.id}"
        album_url = f"{base_url}/album/{album.id}"

        # Format publish date
        publish_date = chapter.updated_at.strftime('%d %B %Y, %H:%M') if chapter.updated_at else datetime.now().strftime('%d %B %Y, %H:%M')

        # Import for email type
        from models import EmailType

        return self.send_email(
            to=recipient_user.email,
            subject=subject,
            body="",  # Will be filled by template
            html_body="",  # Will be filled by template
            email_type=EmailType.CHAPTER_PUBLISHED,
            user_id=recipient_user.id,
            template_name='chapter_published',
            album_title=album.title,
            chapter_number=chapter.chapter_number,
            chapter_title=chapter.chapter_title,
            album_author=album.author,
            publish_date=publish_date,
            chapter_url=chapter_url,
            album_url=album_url
        )

    def send_scheduled_content_published_notification(self, content_type: str, content_title: str,
                                                    content_location: str, scheduled_date: datetime,
                                                    actual_publish_date: datetime, author_user,
                                                    content_url: str) -> bool:
        """Send notification when scheduled content is published"""
        if not author_user.email:
            return False

        # Check user notification preferences
        user_prefs = author_user.email_notifications or {}
        if not user_prefs.get('scheduled_content_published', True):
            return False  # User has opted out of scheduled content published notifications

        # Get brand information from database
        brand_info = self._get_brand_info()

        subject = f"Konten Terjadwal Diterbitkan: {content_title} - {brand_info.brand_name}"

        # Format dates
        scheduled_date_str = scheduled_date.strftime('%d %B %Y, %H:%M') if scheduled_date else 'Tidak diketahui'
        actual_publish_date_str = actual_publish_date.strftime('%d %B %Y, %H:%M') if actual_publish_date else datetime.now().strftime('%d %B %Y, %H:%M')

        # Import for email type
        from models import EmailType

        return self.send_email(
            to=author_user.email,
            subject=subject,
            body="",  # Will be filled by template
            html_body="",  # Will be filled by template
            email_type=EmailType.SCHEDULED_CONTENT_PUBLISHED,
            user_id=author_user.id,
            template_name='scheduled_content_published',
            content_type=content_type,
            content_title=content_title,
            content_location=content_location,
            scheduled_date=scheduled_date_str,
            actual_publish_date=actual_publish_date_str,
            content_url=content_url
        )

    def test_smtp_connection(self) -> Dict[str, Any]:
        """Test SMTP connection and return status"""
        # Ensure service is initialized
        self._ensure_initialized()

        result = {
            'success': False,
            'message': '',
            'config': self.config
        }

        try:
            if self.config.get('smtp_suppress_send', False):
                result['success'] = True
                result['message'] = 'SMTP is configured but suppressed (testing mode)'
                return result
            
            # Test connection
            server = smtplib.SMTP(
                self.config.get('smtp_server', 'localhost'),
                self.config.get('smtp_port', 587),
                timeout=self.config.get('smtp_timeout', 30)
            )
            
            if self.config.get('smtp_use_tls', True):
                server.starttls()
            
            if self.config.get('smtp_username') and self.config.get('smtp_password'):
                server.login(
                    self.config.get('smtp_username'),
                    self.config.get('smtp_password')
                )
            
            server.quit()
            
            result['success'] = True
            result['message'] = 'SMTP connection successful'
            
        except Exception as e:
            result['message'] = f'SMTP connection failed: {str(e)}'
        
        return result

    def _get_brand_info(self):
        """Get brand information from database"""
        try:
            from models import BrandIdentity
            from flask import current_app

            # Get brand info from database
            brand_info = BrandIdentity.query.first()

            if brand_info:
                return brand_info
            else:
                # Return default values if no brand info found
                return type('BrandInfo', (), {
                    'brand_name': 'LilyOpenCMS',
                    'tagline': 'Sistem manajemen konten modern untuk era digital',
                    'brand_description': 'LilyOpenCMS is a modern, open-source content management system designed for the digital age.'
                })()

        except Exception as e:
            logging.getLogger(__name__).warning(f"Could not load brand info for email: {e}")
            # Return default values on error
            return type('BrandInfo', (), {
                'brand_name': 'LilyOpenCMS',
                'tagline': 'Sistem manajemen konten modern untuk era digital',
                'brand_description': 'LilyOpenCMS is a modern, open-source content management system designed for the digital age.'
            })()

    def _get_base_url(self):
        """Get the base URL for the application"""
        try:
            from flask import current_app, request

            # Try to get from request context first (most reliable)
            try:
                if request:
                    scheme = request.scheme
                    server_name = request.host
                    return f"{scheme}://{server_name}"
            except RuntimeError:
                # Outside request context
                pass

            # Fall back to app config
            if hasattr(current_app, 'config'):
                server_name = current_app.config.get('SERVER_NAME')
                if server_name:
                    scheme = current_app.config.get('PREFERRED_URL_SCHEME', 'https')
                    return f"{scheme}://{server_name}"

            # Final fallback - use hystory.id with HTTPS for production
            return "https://hystory.id"

        except Exception as e:
            logging.getLogger(__name__).warning(f"Could not determine base URL for email: {e}")
            return "https://hystory.id"

    def send_bulk_emails(self, email_data_list: List[Dict], async_send: bool = True) -> Dict[str, Any]:
        """Send multiple emails efficiently"""
        if not email_data_list:
            return {'success': True, 'total': 0, 'results': []}

        # If async sending is requested and available
        if async_send:
            try:
                from .email_tasks import send_bulk_emails_async as bulk_task
                if bulk_task:
                    task = bulk_task.delay(email_data_list)
                    import logging; logging.getLogger(__name__).info(f"📧 Bulk email task queued: {len(email_data_list)} emails (task: {task.id})")
                    return {
                        'success': True,
                        'total': len(email_data_list),
                        'task_id': task.id,
                        'async': True,
                        'results': []
                    }
            except Exception as e:
                logging.getLogger(__name__).warning(f"⚠️ Failed to queue bulk emails async, falling back to sync: {e}")

        # Synchronous bulk sending
        results = []
        success_count = 0

        for email_data in email_data_list:
            try:
                success = self.send_email(**email_data)
                results.append({
                    'to': email_data.get('to'),
                    'subject': email_data.get('subject'),
                    'success': success
                })
                if success:
                    success_count += 1

                # Small delay to respect rate limits
                import time
                time.sleep(0.1)

            except Exception as e:
                logging.getLogger(__name__).error(f"Failed to send bulk email to {email_data.get('to')}: {e}")
                results.append({
                    'to': email_data.get('to'),
                    'subject': email_data.get('subject'),
                    'success': False,
                    'error': str(e)
                })

        return {
            'success': True,
            'total': len(email_data_list),
            'successful': success_count,
            'failed': len(email_data_list) - success_count,
            'async': False,
            'results': results
        }

    def queue_verification_email(self, user, token: str) -> bool:
        """Queue verification email for async sending"""
        try:
            from .email_tasks import send_verification_email_async
            if send_verification_email_async:
                task = send_verification_email_async.delay(user.id, token)
                import logging; logging.getLogger(__name__).info(f"📧 Verification email queued for user {user.id} (task: {task.id})")
                return True
        except ImportError:
            pass
        except Exception as e:
            import logging; logging.getLogger(__name__).warning(f"⚠️ Failed to queue verification email, falling back to sync: {e}")

        # Fall back to sync sending
        return self.send_verification_email(user, token)

    def queue_password_reset_email(self, user, token: str) -> bool:
        """Queue password reset email for async sending"""
        try:
            from .email_tasks import send_password_reset_email_async
            if send_password_reset_email_async:
                task = send_password_reset_email_async.delay(user.id, token)
                import logging; logging.getLogger(__name__).info(f"📧 Password reset email queued for user {user.id} (task: {task.id})")
                return True
        except ImportError:
            pass
        except Exception as e:
            import logging; logging.getLogger(__name__).warning(f"⚠️ Failed to queue password reset email, falling back to sync: {e}")

        # Fall back to sync sending
        return self.send_password_reset_email(user, token)

    def queue_chapter_published_notification(self, chapter, album, recipient_user) -> bool:
        """Queue chapter published notification for async sending"""
        try:
            from .email_tasks import send_chapter_published_notification_async
            if send_chapter_published_notification_async:
                task = send_chapter_published_notification_async.delay(chapter.id, album.id, recipient_user.id)
                import logging; logging.getLogger(__name__).info(f"📧 Chapter published notification queued for user {recipient_user.id} (chapter: {chapter.id}, task: {task.id})")
                return True
        except ImportError:
            pass
        except Exception as e:
            import logging; logging.getLogger(__name__).warning(f"⚠️ Failed to queue chapter published notification, falling back to sync: {e}")

        # Fall back to sync sending
        return self.send_chapter_published_notification(chapter, album, recipient_user)

    def queue_scheduled_content_published_notification(self, content_type: str, content_title: str,
                                                     content_location: str, scheduled_date,
                                                     actual_publish_date, author_user, content_url: str) -> bool:
        """Queue scheduled content published notification for async sending"""
        try:
            from .email_tasks import send_scheduled_content_published_notification_async
            if send_scheduled_content_published_notification_async:
                # Format dates for serialization
                scheduled_date_str = scheduled_date.isoformat() if scheduled_date else 'Tidak diketahui'
                actual_publish_date_str = actual_publish_date.isoformat()

                task = send_scheduled_content_published_notification_async.delay(
                    content_type=content_type,
                    content_title=content_title,
                    content_location=content_location,
                    scheduled_date_str=scheduled_date_str,
                    actual_publish_date_str=actual_publish_date_str,
                    author_user_id=author_user.id,
                    content_url=content_url
                )
                import logging; logging.getLogger(__name__).info(f"📧 Scheduled content published notification queued for user {author_user.id} (content: {content_title}, task: {task.id})")
                return True
        except ImportError:
            pass
        except Exception as e:
            import logging; logging.getLogger(__name__).warning(f"⚠️ Failed to queue scheduled content published notification, falling back to sync: {e}")

        # Fall back to sync sending
        return self.send_scheduled_content_published_notification(
            content_type, content_title, content_location, scheduled_date, actual_publish_date, author_user, content_url
        )

# Global email service instance
email_service = EmailService()
