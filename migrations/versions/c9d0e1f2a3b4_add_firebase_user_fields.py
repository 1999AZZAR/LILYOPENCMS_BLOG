"""Add Firebase and user management fields to User model

Revision ID: c9d0e1f2a3b4
Revises: b7c8d9e0f1a2
Create Date: 2026-07-03
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'c9d0e1f2a3b4'
down_revision = 'b7c8d9e0f1a2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('email_verified_at', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('last_verification_sent_at', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('password_reset_token', sa.String(length=255), nullable=True))
    op.add_column('user', sa.Column('password_reset_expires_at', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('firebase_uid', sa.String(length=128), nullable=True))
    op.add_column('user', sa.Column('auth_provider', sa.String(length=50), nullable=True))
    op.add_column('user', sa.Column('provider_data', sa.JSON(), nullable=True))
    op.add_column('user', sa.Column('email_notifications', sa.JSON(), nullable=True))
    op.add_column('user', sa.Column('deletion_requested', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('user', sa.Column('deletion_requested_at', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('deletion_request_moderated', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('user', sa.Column('deletion_request_approved', sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('write_access', sa.Boolean(), nullable=True))
    op.create_index('ix_user_firebase_uid', 'user', ['firebase_uid'])
    op.create_index('ix_user_password_reset_token', 'user', ['password_reset_token'])
    op.create_index('ix_user_deletion_request_moderated', 'user', ['deletion_request_moderated'])


def downgrade():
    op.drop_index('ix_user_deletion_request_moderated')
    op.drop_index('ix_user_password_reset_token')
    op.drop_index('ix_user_firebase_uid')
    op.drop_column('user', 'write_access')
    op.drop_column('user', 'deletion_request_approved')
    op.drop_column('user', 'deletion_request_moderated')
    op.drop_column('user', 'deletion_requested_at')
    op.drop_column('user', 'deletion_requested')
    op.drop_column('user', 'email_notifications')
    op.drop_column('user', 'provider_data')
    op.drop_column('user', 'auth_provider')
    op.drop_column('user', 'firebase_uid')
    op.drop_column('user', 'password_reset_expires_at')
    op.drop_column('user', 'password_reset_token')
    op.drop_column('user', 'last_verification_sent_at')
    op.drop_column('user', 'email_verified_at')
