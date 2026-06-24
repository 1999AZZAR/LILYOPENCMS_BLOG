"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Firebase Authentication Service for LilyOpenCMS

This module provides Firebase Authentication integration for social login
while maintaining the existing sophisticated session management system.
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone

try:
    import firebase_admin
    from firebase_admin import credentials, auth as firebase_auth
    from firebase_admin.exceptions import FirebaseError
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    firebase_admin = None
    firebase_auth = None

from flask import current_app
from models import db, User, UserRole

logger = logging.getLogger(__name__)

class FirebaseAuthService:
    """Service for handling Firebase Authentication integration."""
    
    def __init__(self):
        self._app = None
        self._initialized = False
        
    def initialize(self):
        """Initialize Firebase Admin SDK."""
        if not FIREBASE_AVAILABLE:
            logger.warning("Firebase Admin SDK not available. Install firebase-admin to enable Firebase Auth.")
            return False

        try:
            # Check if Firebase is already initialized
            if firebase_admin._apps:
                self._app = firebase_admin.get_app()
                self._initialized = True
                logger.info("Firebase Admin SDK already initialized")
                return True

            # Get Firebase configuration
            firebase_config = self._get_firebase_config()
            if not firebase_config:
                logger.warning("Firebase configuration not found. Firebase Auth disabled.")
                return False

            # Initialize Firebase Admin SDK with proper credential handling
            cred = None

            if firebase_config.get('service_account_path') and os.path.exists(firebase_config['service_account_path']):
                # Use service account file
                try:
                    cred = credentials.Certificate(firebase_config['service_account_path'])
                    logger.info("Using Firebase service account file")
                except Exception as e:
                    logger.error(f"Failed to load service account file: {e}")
                    return False
            elif firebase_config.get('service_account_json'):
                # Use service account JSON
                try:
                    cred = credentials.Certificate(firebase_config['service_account_json'])
                    logger.info("Using Firebase service account JSON")
                except Exception as e:
                    logger.error(f"Failed to load service account JSON: {e}")
                    return False
            else:
                # Try default credentials for Google Cloud environments
                try:
                    cred = credentials.ApplicationDefault()
                    logger.info("Using Firebase Application Default Credentials")
                except Exception as e:
                    logger.warning(f"Application Default Credentials not available: {e}")
                    logger.warning("Firebase authentication will be unavailable - no valid credentials found")
                    return False

            self._app = firebase_admin.initialize_app(cred, {
                'projectId': firebase_config['project_id']
            })

            self._initialized = True
            logger.info("Firebase Admin SDK initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
            return False
    
    def _get_firebase_config(self) -> Optional[Dict[str, Any]]:
        """Get Firebase configuration from environment variables."""
        config = {}
        
        # Project ID (required)
        config['project_id'] = os.getenv('FIREBASE_PROJECT_ID')
        if not config['project_id']:
            return None
        
        # Service account configuration
        service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
        service_account_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
        
        if service_account_path and os.path.exists(service_account_path):
            # Validate that this is actually a service account file, not google-services.json
            try:
                with open(service_account_path, 'r', encoding='utf-8') as f:
                    sa_data = json.load(f)

                if sa_data.get('type') == 'service_account':
                    config['service_account_path'] = service_account_path
                    logger.info("Valid service account file found")
                else:
                    logger.warning(f"File at {service_account_path} is not a service account file (type: {sa_data.get('type')}). Firebase Admin SDK will not be initialized.")
                    return None
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error reading service account file: {e}")
                return None
        elif service_account_json:
            try:
                sa_data = json.loads(service_account_json)
                if sa_data.get('type') == 'service_account':
                    config['service_account_json'] = sa_data
                    logger.info("Valid service account JSON found")
                else:
                    logger.warning("Service account JSON is not a valid service account. Firebase Admin SDK will not be initialized.")
                    return None
            except json.JSONDecodeError:
                logger.error("Invalid FIREBASE_SERVICE_ACCOUNT_JSON format")
                return None
        
        return config
    
    def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """Verify Firebase ID token and return decoded token data."""
        if not self._initialized:
            logger.error("Firebase Auth service not initialized")
            return None

        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
            return decoded_token
        except firebase_auth.InvalidIdTokenError as e:
            logger.warning(f"Invalid Firebase ID token: {e}")
            return None
        except firebase_auth.ExpiredIdTokenError as e:
            logger.warning(f"Expired Firebase ID token: {e}")
            return None
        except firebase_auth.RevokedIdTokenError as e:
            logger.warning(f"Revoked Firebase ID token: {e}")
            return None
        except FirebaseError as e:
            logger.error(f"Firebase token verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {e}")
            # Don't return the full error details to avoid exposing internal configuration
            return None
    
    def get_user_by_firebase_uid(self, firebase_uid: str) -> Optional[User]:
        """Get user by Firebase UID."""
        return User.query.filter_by(firebase_uid=firebase_uid).first()
    
    def create_user_from_firebase(self, firebase_user_data: Dict[str, Any]) -> Optional[User]:
        """Create a new user from Firebase authentication data."""
        try:
            firebase_uid = firebase_user_data.get('uid')
            email = firebase_user_data.get('email')
            display_name = firebase_user_data.get('name', '')
            photo_url = firebase_user_data.get('picture')
            
            if not firebase_uid:
                logger.error("Firebase UID is required")
                return None
            
            # Check if user already exists
            existing_user = self.get_user_by_firebase_uid(firebase_uid)
            if existing_user:
                logger.info(f"User with Firebase UID {firebase_uid} already exists")
                return existing_user
            
            # Check if user exists with same email
            if email:
                existing_email_user = User.query.filter_by(email=email).first()
                if existing_email_user:
                    # Link Firebase account to existing user
                    existing_email_user.firebase_uid = firebase_uid
                    existing_email_user.auth_provider = self._get_provider_from_firebase_data(firebase_user_data)
                    existing_email_user.provider_data = {
                        'display_name': display_name,
                        'photo_url': photo_url,
                        'firebase_data': firebase_user_data
                    }
                    existing_email_user.verified = True  # Firebase users are pre-verified
                    existing_email_user.email_verified_at = datetime.now(timezone.utc)
                    
                    db.session.commit()
                    logger.info(f"Linked Firebase account to existing user {existing_email_user.username}")
                    return existing_email_user
            
            # Create new user
            username = self._generate_username_from_firebase(firebase_user_data)
            
            user = User(
                username=username,
                email=email,
                firebase_uid=firebase_uid,
                auth_provider=self._get_provider_from_firebase_data(firebase_user_data),
                provider_data={
                    'display_name': display_name,
                    'photo_url': photo_url,
                    'firebase_data': firebase_user_data
                },
                verified=True,  # Firebase users are pre-verified
                email_verified_at=datetime.now(timezone.utc) if email else None,
                role=UserRole.GENERAL,
                is_active=True
            )
            
            # Set a dummy password hash (Firebase users don't use local passwords)
            user.password_hash = "firebase_user_no_password"
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"Created new Firebase user: {username} ({email})")
            return user
            
        except Exception as e:
            logger.error(f"Failed to create user from Firebase data: {e}")
            db.session.rollback()
            return None
    
    def _get_provider_from_firebase_data(self, firebase_data: Dict[str, Any]) -> str:
        """Determine the authentication provider from Firebase data."""
        firebase_info = firebase_data.get('firebase', {})
        sign_in_provider = firebase_info.get('sign_in_provider', 'firebase')
        
        # Map Firebase provider names to our internal names
        provider_mapping = {
            'google.com': 'google',
            'facebook.com': 'facebook',
            'twitter.com': 'twitter',
            'github.com': 'github',
            'password': 'firebase',
            'email': 'firebase'
        }
        
        return provider_mapping.get(sign_in_provider, 'firebase')
    
    def _generate_username_from_firebase(self, firebase_data: Dict[str, Any]) -> str:
        """Generate a unique username from Firebase data."""
        base_username = None
        
        # Try to use display name first
        display_name = firebase_data.get('name', '')
        if display_name:
            base_username = display_name.lower().replace(' ', '_')
        
        # Fall back to email
        if not base_username:
            email = firebase_data.get('email', '')
            if email:
                base_username = email.split('@')[0]
        
        # Fall back to Firebase UID
        if not base_username:
            base_username = f"user_{firebase_data.get('uid', '')[:8]}"
        
        # Ensure username is unique
        username = base_username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}_{counter}"
            counter += 1
        
        return username
    
    def authenticate_user(self, id_token: str) -> Optional[User]:
        """Authenticate user with Firebase ID token and create session."""
        if not self._initialized:
            logger.error("Firebase Auth service not initialized")
            return None
        
        # Verify the ID token
        firebase_user_data = self.verify_id_token(id_token)
        if not firebase_user_data:
            return None
        
        firebase_uid = firebase_user_data.get('uid')
        if not firebase_uid:
            return None
        
        # Get or create user
        user = self.get_user_by_firebase_uid(firebase_uid)
        if not user:
            user = self.create_user_from_firebase(firebase_user_data)
        
        if not user:
            return None
        
        # Update user login information
        user.last_login = datetime.now(timezone.utc)
        user.login_count += 1
        db.session.commit()
        
        # Create JWT tokens using simple JWT manager
        from routes.utils.simple_jwt_session import get_simple_jwt_manager
        jwt_manager = get_simple_jwt_manager()

        # Create tokens
        access_token = jwt_manager.create_access_token(user)
        refresh_token = jwt_manager.create_refresh_token(user)

        if access_token and refresh_token:
            logger.info(f"Firebase authentication successful for user {user.username}")
            return user
        else:
            logger.error(f"Failed to create JWT tokens for Firebase user {user.username}")
            return None
    
    def authenticate_user_with_tokens(self, id_token: str) -> Optional[dict]:
        """Authenticate user with Firebase ID token and return both session and JWT tokens."""
        user = self.authenticate_user(id_token)
        if not user:
            return None
        
        # Use unified authentication system to get JWT tokens
        try:
            from routes.utils.auth_helpers import get_auth_helper
            auth_helper = get_auth_helper()
            auth_result = auth_helper.authenticate_user(user, "firebase")

            if not auth_result["success"]:
                logger.error(f"Unified authentication failed for Firebase user {user.username}")
                return None

            # The auth_result already contains the JWT tokens directly
            jwt_tokens = auth_result.copy()

            # Add session information
            jwt_tokens['session_created'] = True
            # Update user info with additional fields
            jwt_tokens['user'] = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "is_premium": user.is_premium,
                "auth_provider": user.auth_provider,
                "profile_picture": user.profile_picture or user.parsed_provider_data.get('photo_url') if user.provider_data else None
            }

            return jwt_tokens
            
        except Exception as e:
            logger.error(f"Failed to issue JWT tokens for Firebase user {user.username}: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if Firebase Auth service is available and initialized."""
        return FIREBASE_AVAILABLE and self._initialized

# Global instance
firebase_auth_service = FirebaseAuthService()

def init_firebase_auth():
    """Initialize Firebase Auth service."""
    return firebase_auth_service.initialize()

def get_firebase_auth_service():
    """Get the Firebase Auth service instance."""
    return firebase_auth_service
