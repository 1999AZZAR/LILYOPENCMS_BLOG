"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Premium Content Utility Functions

This module provides utilities for handling premium content filtering,
content truncation, and premium status checking.
"""

import re
from typing import Tuple, Optional
from flask import current_app
from flask_login import current_user
from datetime import datetime
from models import db, UserChapterPurchase


def is_premium_user() -> bool:
    """
    Check if the current user has active premium access.
    
    Returns:
        bool: True if user has active premium subscription, False otherwise
    """
    if not current_user.is_authenticated:
        return False
    
    return current_user.has_active_premium_subscription()


def should_show_premium_content(content_is_premium: bool) -> bool:
    """
    Determine if premium content should be shown to the current user.
    
    Args:
        content_is_premium (bool): Whether the content is marked as premium
        
    Returns:
        bool: True if content should be shown, False if it should be truncated
    """
    if not content_is_premium:
        return True  # Non-premium content is always shown
    
    return is_premium_user()


def truncate_markdown_content(content: str, max_words: int = 150) -> Tuple[str, bool]:
    """
    Truncate markdown content to a specified number of words while preserving markdown structure.
    
    Args:
        content (str): The markdown content to truncate
        max_words (int): Maximum number of words to show
        
    Returns:
        Tuple[str, bool]: (truncated_content, was_truncated)
    """
    if not content:
        return "", False
    
    # Split content into words while preserving markdown structure
    words = re.findall(r'\S+|\n+', content)
    
    if len(words) <= max_words:
        return content, False
    
    # Take first max_words words
    truncated_words = words[:max_words]
    
    # Reconstruct content
    truncated_content = ''.join(truncated_words)
    
    # Add ellipsis if content was truncated
    if truncated_content and not truncated_content.endswith('\n'):
        truncated_content += '...'
    
    return truncated_content, True


def process_premium_content(content: str, is_premium_content: bool, max_words: int = 150) -> Tuple[str, bool, bool]:
    """
    Process content based on premium status and user access.
    
    Args:
        content (str): The original content
        is_premium_content (bool): Whether the content is premium
        max_words (int): Maximum words to show for non-premium users
        
    Returns:
        Tuple[str, bool, bool]: (processed_content, is_truncated, show_premium_notice)
    """
    if not should_show_premium_content(is_premium_content):
        # User doesn't have premium access for premium content
        truncated_content, was_truncated = truncate_markdown_content(content, max_words)
        return truncated_content, was_truncated, True
    
    # User has access to full content
    return content, False, False


def get_premium_content_stats(content: str, is_premium_content: bool) -> dict:
    """
    Get statistics about premium content processing.
    
    Args:
        content (str): The original content
        is_premium_content (bool): Whether the content is premium
        
    Returns:
        dict: Statistics about the content
    """
    if not content:
        return {
            'total_words': 0,
            'total_chars': 0,
            'is_premium': is_premium_content,
            'user_has_access': should_show_premium_content(is_premium_content)
        }
    
    words = re.findall(r'\S+', content)
    chars = len(content)
    
    return {
        'total_words': len(words),
        'total_chars': chars,
        'is_premium': is_premium_content,
        'user_has_access': should_show_premium_content(is_premium_content)
    }


def generate_premium_notice_html(content_type: str = "artikel") -> str:
    """
    Generate HTML for premium content notice.
    
    Args:
        content_type (str): Type of content (artikel, bab, etc.)
        
    Returns:
        str: HTML for premium notice
    """
    return f"""
    <div class="premium-content-notice bg-gradient-to-r from-primary/10 to-secondary/10 border border-primary/20 rounded-lg p-6 my-6">
        <div class="flex items-center gap-3 mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-6 h-6 text-primary">
                <path fill-rule="evenodd" d="M5.166 2.621v.858c-1.035.148-2.059.33-3.071.543a.75.75 0 00-.584.859 6.937 6.937 0 006.222 6.222.75.75 0 00.859-.584 48.332 48.332 0 001.243-5.034 48.332 48.332 0 005.034-1.243.75.75 0 00.584-.859 6.937 6.937 0 00-6.222-6.222.75.75 0 00-.859.584 48.332 48.332 0 00-1.243 5.034zM13.5 2.25a.75.75 0 01.75.75v.75a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM13.5 6.75a.75.75 0 01.75.75v.75a.75.75 0 01-1.5 0V7.5a.75.75 0 01.75-.75zM13.5 11.25a.75.75 0 01.75.75v.75a.75.75 0 01-1.5 0V12a.75.75 0 01.75-.75z" clip-rule="evenodd" />
            </svg>
            <h3 class="text-lg font-semibold text-foreground">Konten Premium</h3>
        </div>
        <p class="text-muted-foreground mb-4">Untuk membaca {content_type} ini secara lengkap, Anda memerlukan langganan premium.</p>
        <div class="flex flex-wrap gap-3">
            <a href="/premium" class="button button-primary">
                Berlangganan Premium
            </a>
            <a href="/login" class="button button-outline">
                Login
            </a>
        </div>
    </div>
    """


def create_content_mask_html(content_id: str, content_type: str = "artikel") -> str:
    """
    Create HTML for content mask overlay.
    
    Args:
        content_id (str): Unique identifier for the content
        content_type (str): Type of content
        
    Returns:
        str: HTML for content mask
    """
    return f"""
    <div id="content-mask-{content_id}" class="content-mask-overlay">
        <div class="content-mask-backdrop"></div>
        <div class="content-mask-content">
            <div class="content-mask-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-12 h-12">
                    <path fill-rule="evenodd" d="M5.166 2.621v.858c-1.035.148-2.059.33-3.071.543a.75.75 0 00-.584.859 6.937 6.937 0 006.222 6.222.75.75 0 00.859-.584 48.332 48.332 0 001.243-5.034 48.332 48.332 0 005.034-1.243.75.75 0 00.584-.859 6.937 6.937 0 00-6.222-6.222.75.75 0 00-.859.584 48.332 48.332 0 00-1.243 5.034zM13.5 2.25a.75.75 0 01.75.75v.75a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM13.5 6.75a.75.75 0 01.75.75v.75a.75.75 0 01-1.5 0V7.5a.75.75 0 01.75-.75zM13.5 11.25a.75.75 0 01.75.75v.75a.75.75 0 01-1.5 0V12a.75.75 0 01.75-.75z" clip-rule="evenodd" />
                </svg>
            </div>
            <h3 class="text-xl font-semibold text-foreground mb-2">Konten Premium</h3>
            <p class="text-muted-foreground text-center mb-4">Untuk membaca {content_type} ini secara lengkap, Anda memerlukan langganan premium.</p>
            <div class="flex flex-col sm:flex-row gap-3 justify-center">
                <a href="/premium" class="button button-primary">
                    Berlangganan Premium
                </a>
                <a href="/login" class="button button-outline">
                    Login
                </a>
            </div>
        </div>
    </div>
    """


# Auto Pricing Functions for Album Chapters

def is_chapter_paid_access(chapter_number: int) -> bool:
    """
    Check if a chapter requires paid access based on chapter number.
    Uses configurable free chapters setting from admin UI.

    Args:
        chapter_number (int): The chapter number to check

    Returns:
        bool: True if chapter requires payment, False if free
    """
    from models import PricingConfig
    free_chapters = PricingConfig.get_config_value('chapter_free_chapters', 5, 'int')
    return chapter_number > free_chapters


def get_chapter_price(chapter_number: int, album_id: int = None, word_count: int = None, is_premium: bool = False) -> int:
    """
    Get the coin price for accessing a chapter using the dynamic pricing system.

    Args:
        chapter_number (int): The chapter number
        album_id (int, optional): Album ID for performance calculation
        word_count (int, optional): Word count for pricing bonus
        is_premium (bool, optional): Whether this is premium content

    Returns:
        int: Number of coins required (0 for free chapters)
    """
    # Import pricing calculator
    from routes.routes_pricing import ChapterPricingCalculator

    calculator = ChapterPricingCalculator()

    # Use album_id if provided, otherwise use a default for basic calculation
    pricing = calculator.get_pricing_with_equivalents(
        album_id=album_id or 1,  # Default album ID if not provided
        chapter_number=chapter_number,
        word_count=word_count,
        is_premium=is_premium
    )

    return pricing['total_coins']


def can_user_access_chapter(user_id: int, chapter_id: int, chapter_number: int) -> bool:
    """
    Check if a user can access a specific chapter.
    Premium users, admins, and content owners bypass the coin system entirely.

    Args:
        user_id (int): The user ID
        chapter_id (int): The chapter ID
        chapter_number (int): The chapter number

    Returns:
        bool: True if user can access, False if payment required
    """
    if not is_chapter_paid_access(chapter_number):
        return True  # Free access for chapters 1-5

    # Check if user is premium or admin - they bypass coin requirements
    if user_id:
        from models import User, AlbumChapter
        user = User.query.get(user_id)
        if user and (user.is_premium or user.role in ['SUPERUSER', 'ADMIN']):
            return True  # Admin/premium users have unlimited access
        
        # Check if user owns this content - owners get free access
        chapter = AlbumChapter.query.get(chapter_id)
        if chapter and chapter.album and chapter.album.user_id == user_id:
            return True  # Content owners have free access

    # For paid chapters, check if user has already purchased access
    from models import UserChapterPurchase
    purchase = UserChapterPurchase.query.filter_by(
        user_id=user_id,
        chapter_id=chapter_id
    ).first()

    return purchase is not None


def purchase_chapter_access(user_id: int, chapter_id: int, chapter_number: int, coin_priority: str = 'gold') -> dict:
    """
    Purchase access to a chapter using coins.

    Args:
        user_id (int): The user ID
        chapter_id (int): The chapter ID
        chapter_number (int): The chapter number
        coin_priority (str): For hybrid chapters, which coin to prioritize ('gold' or 'bronze')
                           - 'gold': Use gold first, then bronze (default, supports writers more)
                           - 'bronze': Use bronze first, then gold (saves gold for gold-only chapters)

    Returns:
        dict: Purchase result with success status and details
    """
    if not is_chapter_paid_access(chapter_number):
        return {
            "success": True,
            "coins_spent": 0,
            "message": "Chapter is free to access"
        }

    # Check if already purchased
    if can_user_access_chapter(user_id, chapter_id, chapter_number):
        return {
            "success": True,
            "coins_spent": 0,
            "message": "Already have access to this chapter"
        }

    # Get chapter details for pricing calculation
    from models import AlbumChapter
    chapter = AlbumChapter.query.get(chapter_id)
    if not chapter:
        return {
            "success": False,
            "error": "Chapter not found"
        }

    # Get word count from news content if available
    word_count = None
    is_premium = False
    if chapter.news and hasattr(chapter.news, 'content'):
        word_count = len(chapter.news.content.split()) if chapter.news.content else None
        is_premium = chapter.news.is_premium if hasattr(chapter.news, 'is_premium') else False

    # Get price and validate purchase eligibility
    price = get_chapter_price(chapter_number, chapter.album_id, word_count, is_premium)
    from models import CoinManager

    # Use comprehensive validation
    validation = CoinManager.validate_purchase_eligibility(user_id, 'chapter', chapter_id, price)
    if not validation['valid']:
        if validation.get('bypass'):
            # User bypasses coin requirement
            return {
                "success": True,
                "coins_spent": 0,
                "message": f"Access granted: {validation['reason']}"
            }
        else:
            # Cannot afford or other validation error
            return {
                "success": False,
                "error": validation.get('error', 'Purchase validation failed')
            }

    # Make the purchase using the dedicated chapter purchase method
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Calling CoinManager.purchase_chapter: user={user_id}, chapter={chapter_id}, price={price}, priority={coin_priority}")
    
    purchase_result = CoinManager.purchase_chapter(
        user_id, chapter_id, price, 'any', 'chapter_purchase', coin_priority=coin_priority
    )
    
    logger.info(f"CoinManager.purchase_chapter result: {purchase_result}")

    if purchase_result['success']:
        return {
            "success": True,
            "coins_spent": price,
            "gold_coins_spent": purchase_result.get('gold_coins_spent', 0),
            "bronze_coins_spent": purchase_result.get('bronze_coins_spent', 0),
            "message": f"Successfully purchased chapter access for {price} coins",
            "coin_type_used": purchase_result.get('coin_type_used', 'any')
        }

    return purchase_result


def bulk_purchase_chapter_access(user_id: int, chapter_ids: list, chapter_numbers: list) -> dict:
    """
    Bulk purchase access to multiple chapters using coins.

    Args:
        user_id (int): The user ID
        chapter_ids (list): List of chapter IDs to purchase
        chapter_numbers (list): List of chapter numbers corresponding to chapter_ids

    Returns:
        dict: Bulk purchase result with success status and details
    """
    if len(chapter_ids) != len(chapter_numbers):
        return {
            "success": False,
            "error": "Chapter IDs and numbers lists must have the same length"
        }

    if not chapter_ids:
        return {
            "success": False,
            "error": "No chapters provided"
        }

    # Get all chapter details
    from models import AlbumChapter
    chapters = []
    total_cost = 0
    valid_chapters = []

    for i, chapter_id in enumerate(chapter_ids):
        chapter = AlbumChapter.query.get(chapter_id)
        if not chapter:
            continue

        chapter_number = chapter_numbers[i]

        # Skip if already purchased or free
        if not is_chapter_paid_access(chapter_number) or can_user_access_chapter(user_id, chapter_id, chapter_number):
            continue

        # Get word count from news content if available
        word_count = None
        is_premium = False
        if chapter.news and hasattr(chapter.news, 'content'):
            word_count = len(chapter.news.content.split()) if chapter.news.content else None
            is_premium = chapter.news.is_premium if hasattr(chapter.news, 'is_premium') else False

        # Get price
        price = get_chapter_price(chapter_number, chapter.album_id, word_count, is_premium)

        valid_chapters.append({
            'chapter': chapter,
            'price': price
        })
        total_cost += price

    if not valid_chapters:
        return {
            "success": False,
            "error": "No valid chapters to purchase"
        }

    # Check if user can afford all chapters combined
    from models import CoinManager
    validation = CoinManager.validate_purchase_eligibility(user_id, 'bulk_chapter', chapter_ids[0], total_cost)
    if not validation['valid']:
        if validation.get('bypass'):
            # User bypasses coin requirement
            return {
                "success": True,
                "coins_spent": 0,
                "chapters_purchased": len(valid_chapters),
                "message": f"Bulk access granted: {validation['reason']}"
            }
        else:
            return {
                "success": False,
                "error": validation.get('error', 'Bulk purchase validation failed')
            }

    # Get user coins for spending
    user_coins = CoinManager.get_or_create_user_coins(user_id)

    # Spend coins using gold priority (same logic as CoinManager.purchase_chapter)
    spend_result = CoinManager._spend_coins_gold_priority(
        user_coins, total_cost, 'bulk_chapter_purchase',
        f"Bulk purchased {len(valid_chapters)} chapters", {"chapter_ids": chapter_ids}
    )

    if spend_result['success']:
        # Grant access to all chapters by creating purchase records
        for chapter_data in valid_chapters:
            chapter = chapter_data['chapter']
            # Check if purchase record already exists (prevent duplicates)
            existing_purchase = UserChapterPurchase.query.filter_by(
                user_id=user_id,
                chapter_id=chapter.id
            ).first()

            if not existing_purchase:
                # Create purchase record for each chapter
                purchase_record = UserChapterPurchase(
                    user_id=user_id,
                    chapter_id=chapter.id,
                    coins_spent=chapter_data['price'],
                    coin_type=spend_result.get('coin_type_used', 'any')
                )
                db.session.add(purchase_record)

        db.session.commit()

        return {
            "success": True,
            "coins_spent": total_cost,
            "chapters_purchased": len(valid_chapters),
            "message": f"Successfully purchased {len(valid_chapters)} chapters for {total_cost} coins",
            "coin_type_used": spend_result.get('coin_type_used', 'any')
        }

    return {
        "success": False,
        "error": spend_result.get('error', 'Bulk purchase failed')
    }
