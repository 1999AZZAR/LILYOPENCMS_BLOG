"""Add tag, page, comment tables

Revision ID: b7c8d9e0f1a2
Revises: 3f8c7a6b5d4e
Create Date: 2026-07-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'b7c8d9e0f1a2'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # tags table
    op.create_table(
        'tag',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=120), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug'),
    )

    # news_tags junction table
    op.create_table(
        'news_tags',
        sa.Column('news_id', sa.Integer(), sa.ForeignKey('news.id'), primary_key=True),
        sa.Column('tag_id', sa.Integer(), sa.ForeignKey('tag.id'), primary_key=True),
    )

    # pages table
    op.create_table(
        'page',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=250), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('excerpt', sa.Text(), nullable=True),
        sa.Column('template', sa.String(length=50), server_default='default'),
        sa.Column('is_published', sa.Boolean(), server_default=sa.text('false')),
        sa.Column('show_in_menu', sa.Boolean(), server_default=sa.text('false')),
        sa.Column('menu_order', sa.Integer(), server_default=sa.text('0')),
        sa.Column('meta_title', sa.String(length=200), nullable=True),
        sa.Column('meta_description', sa.Text(), nullable=True),
        sa.Column('og_title', sa.String(length=200), nullable=True),
        sa.Column('og_description', sa.Text(), nullable=True),
        sa.Column('og_image', sa.String(length=500), nullable=True),
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
    )

    # comments table
    op.create_table(
        'comment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='pending'),
        sa.Column('author_name', sa.String(length=100), nullable=False),
        sa.Column('author_email', sa.String(length=200), nullable=False),
        sa.Column('author_ip', sa.String(length=45), nullable=True),
        sa.Column('news_id', sa.Integer(), sa.ForeignKey('news.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=True),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('comment.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_comment_news_id', 'comment', ['news_id'])
    op.create_index('ix_comment_status', 'comment', ['status'])
    op.create_index('ix_comment_parent_id', 'comment', ['parent_id'])


def downgrade():
    op.drop_table('comment')
    op.drop_table('page')
    op.drop_table('news_tags')
    op.drop_table('tag')
