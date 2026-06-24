"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Image utility functions for safe handling of album cover images and other images.
Provides fallback to placeholder images when cover images are missing.
"""

from flask import url_for


def get_album_cover_image_url(album, thumbnail=False):
    """
    Safely get album cover image URL with fallback to placeholder.
    
    Args:
        album: Album object
        thumbnail (bool): Whether to return thumbnail URL (if available)
    
    Returns:
        dict: Contains 'url' and 'has_image' keys
    """
    if not album or not album.cover_image:
        return {
            'url': url_for('static', filename='pic/placeholder.png'),
            'has_image': False
        }
    
    try:
        # Try to get the image URL safely
        if hasattr(album.cover_image, 'to_dict'):
            image_dict = album.cover_image.to_dict()
            image_url = image_dict.get('file_url') or image_dict.get('url')
        else:
            image_url = getattr(album.cover_image, 'url', None)
        
        if image_url:
            # If thumbnail is requested and we have a filepath, try to construct thumbnail URL
            if thumbnail and hasattr(album.cover_image, 'filepath') and album.cover_image.filepath:
                try:
                    # Extract base path and extension
                    filepath = album.cover_image.filepath
                    if 'static/' in filepath:
                        path_without_static = filepath.split('static/', 1)[1]
                        last_dot_index = path_without_static.rfind('.')
                        if last_dot_index != -1:
                            base_path = path_without_static[:last_dot_index]
                            # Strip '_cover' suffix if present to get the actual base name
                            if base_path.endswith('_cover'):
                                base_path = base_path[:-6]
                            extension = path_without_static[last_dot_index:]
                            thumbnail_url = url_for('static', filename=f"{base_path}_thumb_square{extension}")
                            return {
                                'url': thumbnail_url,
                                'has_image': True
                            }
                except Exception:
                    # If thumbnail construction fails, fall back to original image
                    pass
            
            return {
                'url': image_url,
                'has_image': True
            }
    except Exception:
        # If any error occurs, fall back to placeholder
        pass
    
    return {
        'url': url_for('static', filename='pic/placeholder.png'),
        'has_image': False
    }


def get_image_url_safe(image_obj, thumbnail=False):
    """
    Safely get image URL with fallback to placeholder.
    
    Args:
        image_obj: Image object
        thumbnail (bool): Whether to return thumbnail URL (if available)
    
    Returns:
        str: Image URL or placeholder URL
    """
    if not image_obj:
        return url_for('static', filename='pic/placeholder.png')
    
    try:
        if hasattr(image_obj, 'to_dict'):
            image_dict = image_obj.to_dict()
            image_url = image_dict.get('file_url') or image_dict.get('url')
        else:
            image_url = getattr(image_obj, 'url', None)
        
        if image_url:
            # If thumbnail is requested and we have a filepath, try to construct thumbnail URL
            if thumbnail and hasattr(image_obj, 'filepath') and image_obj.filepath:
                try:
                    filepath = image_obj.filepath
                    if 'static/' in filepath:
                        path_without_static = filepath.split('static/', 1)[1]
                        last_dot_index = path_without_static.rfind('.')
                        if last_dot_index != -1:
                            base_path = path_without_static[:last_dot_index]
                            # Strip '_cover' suffix if present to get the actual base name
                            if base_path.endswith('_cover'):
                                base_path = base_path[:-6]
                            extension = path_without_static[last_dot_index:]
                            return url_for('static', filename=f"{base_path}_thumb_square{extension}")
                except Exception:
                    pass
            
            return image_url
    except Exception:
        pass
    
    return url_for('static', filename='pic/placeholder.png')


def get_album_cover_image_data(album):
    """
    Get comprehensive album cover image data for API responses.
    
    Args:
        album: Album object
    
    Returns:
        dict: Contains cover image data or None if no image
    """
    if not album or not album.cover_image:
        return None
    
    try:
        cover_image = album.cover_image
        image_data = {
            'id': cover_image.id,
            'url': get_image_url_safe(cover_image),
            'thumbnail_url': get_image_url_safe(cover_image, thumbnail=True),
            'description': getattr(cover_image, 'description', None),
            'filepath': getattr(cover_image, 'filepath', None)
        }
        
        # Add additional data if available
        if hasattr(cover_image, 'to_dict'):
            image_dict = cover_image.to_dict()
            image_data.update({
                'file_url': image_dict.get('file_url'),
                'filename': image_dict.get('filename'),
                'is_visible': image_dict.get('is_visible', False)
            })
        
        return image_data
    except Exception:
        return None
