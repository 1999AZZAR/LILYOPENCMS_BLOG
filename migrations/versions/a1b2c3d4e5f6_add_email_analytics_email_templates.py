"""Add email_analytics and email_templates tables

Revision ID: a1b2c3d4e5f6
Revises: b44646030553
Create Date: 2026-07-01 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '7009cbfac1e5'
branch_labels = None
depends_on = None


def upgrade():
    # Create email_analytics table
    op.create_table(
        'email_analytics',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('date', sa.Date(), nullable=False, index=True, unique=True),
        sa.Column('emails_sent', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('emails_delivered', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('emails_failed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('emails_bounced', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('emails_complained', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('delivery_rate', sa.Float(), server_default='0.0'),
        sa.Column('bounce_rate', sa.Float(), server_default='0.0'),
        sa.Column('complaint_rate', sa.Float(), server_default='0.0'),
        sa.Column('avg_send_time', sa.Float(), server_default='0.0'),
        sa.Column('avg_delivery_time', sa.Float(), server_default='0.0'),
        sa.Column('type_breakdown', sa.JSON(), nullable=True),
        sa.Column('rate_limit_hits', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create email_templates table
    op.create_table(
        'email_templates',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('subject_template', sa.String(500), nullable=False),
        sa.Column('html_template', sa.Text(), nullable=False),
        sa.Column('text_template', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('email_type', sa.Enum('verification', 'password_reset', 'suspension',
                                         'write_access_approved', 'write_access_rejected',
                                         'account_deletion_request', 'account_deletion_confirmation',
                                         'content_approved', 'content_rejected', 'content_deletion',
                                         'profile_update', 'edit_request_approved', 'edit_request_rejected',
                                         'album_edit_request_submitted', 'editor_edit_request_notification',
                                         'chapter_published', 'scheduled_content_published', 'custom',
                                         name='emailtype'), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('user.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade():
    op.drop_table('email_templates')
    op.drop_table('email_analytics')
    op.execute("DROP TYPE IF EXISTS emailtype")
