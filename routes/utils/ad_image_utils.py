"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Utility functions for handling ad image uploads and management.
"""

import os
import uuid
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app, request
import hashlib


# Allowed image extensions and MIME types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_MIME_TYPES = {
    'image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'
}

# Maximum file size (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

# Image dimensions limits
MAX_WIDTH = 2000
MAX_HEIGHT = 2000
MIN_WIDTH = 100
MIN_HEIGHT = 100


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_mime_type(mime_type):
    """Check if the MIME type is allowed."""
    return mime_type in ALLOWED_MIME_TYPES


def validate_image_file(file):
    """Validate the uploaded image file."""
    errors = []
    
    # Check if file exists
    if not file or not file.filename:
        errors.append("No file selected")
        return False, errors
    
    # Check file extension
    if not allowed_file(file.filename):
        errors.append(f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")
    
    # Check MIME type
    if hasattr(file, 'content_type') and file.content_type:
        if not allowed_mime_type(file.content_type):
            errors.append(f"MIME type not allowed: {file.content_type}")
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        errors.append(f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024:.1f}MB")
    
    if file_size == 0:
        errors.append("File is empty")
    
    return len(errors) == 0, errors


def generate_unique_filename(original_filename):
    """Generate a unique filename for the uploaded image."""
    # Get file extension
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
    
    # Generate unique filename using UUID
    unique_id = str(uuid.uuid4())
    secure_name = secure_filename(original_filename.rsplit('.', 1)[0])
    
    # Create filename with timestamp and unique ID
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return f"ad_{timestamp}_{unique_id[:8]}_{secure_name[:20]}.{ext}"


def get_upload_path():
    """Get the upload path for ad images."""
    return os.path.join(current_app.static_folder, 'uploads', 'ads')


def save_ad_image(file, ad_id=None):
    """Save the uploaded image file and return image information."""
    try:
        # Validate the file
        is_valid, errors = validate_image_file(file)
        if not is_valid:
            return None, errors
        
        # Generate unique filename
        filename = generate_unique_filename(file.filename)
        
        # Create upload directory if it doesn't exist
        upload_path = get_upload_path()
        os.makedirs(upload_path, exist_ok=True)
        
        # Full file path
        file_path = os.path.join(upload_path, filename)
        
        # Save the file
        file.save(file_path)
        
        # Get image information
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                
                # Validate dimensions
                if width < MIN_WIDTH or height < MIN_HEIGHT:
                    os.remove(file_path)
                    return None, [f"Image too small. Minimum size: {MIN_WIDTH}x{MIN_HEIGHT}"]
                
                if width > MAX_WIDTH or height > MAX_HEIGHT:
                    # Resize if too large
                    img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.Resampling.LANCZOS)
                    img.save(file_path, optimize=True, quality=85)
                    width, height = img.size
                
                # Get file size
                file_size = os.path.getsize(file_path)
                
        except Exception as e:
            # Remove the file if we can't process it
            if os.path.exists(file_path):
                os.remove(file_path)
            return None, [f"Invalid image file: {str(e)}"]
        
        # Create relative path for database storage
        relative_path = f"/static/uploads/ads/{filename}"
        
        # Return image information
        image_info = {
            'filename': filename,
            'upload_path': relative_path,
            'width': width,
            'height': height,
            'file_size': file_size,
            'full_path': file_path
        }
        
        return image_info, []
        
    except Exception as e:
        return None, [f"Error saving image: {str(e)}"]


def delete_ad_image(image_path):
    """Delete an ad image file."""
    try:
        if not image_path:
            return True, []
        
        # Convert relative path to full path
        if image_path.startswith('/static/'):
            full_path = os.path.join(current_app.static_folder, image_path[8:])  # Remove '/static/'
        else:
            full_path = image_path
        
        # Check if file exists and delete
        if os.path.exists(full_path):
            os.remove(full_path)
            return True, []
        else:
            return False, ["File not found"]
            
    except Exception as e:
        return False, [f"Error deleting image: {str(e)}"]


def get_image_url(image_path):
    """Get the full URL for an image path."""
    if not image_path:
        return None
    
    # If it's already a full URL, return as is
    if image_path.startswith('http'):
        return image_path
    
    # If it's a relative path, make it absolute
    if image_path.startswith('/static/'):
        return image_path
    
    # Otherwise, assume it's a relative path and add /static/
    return f"/static/uploads/ads/{image_path}"


def resize_image_for_thumbnail(image_path, max_size=(300, 300)):
    """Create a thumbnail version of the image."""
    try:
        if not image_path or not os.path.exists(image_path):
            return None
        
        with Image.open(image_path) as img:
            # Create thumbnail
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Generate thumbnail filename
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            ext = os.path.splitext(os.path.basename(image_path))[1]
            thumbnail_name = f"{base_name}_thumb{ext}"
            thumbnail_path = os.path.join(os.path.dirname(image_path), thumbnail_name)
            
            # Save thumbnail
            img.save(thumbnail_path, optimize=True, quality=80)
            
            return thumbnail_path
            
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return None


def get_image_info(image_path):
    """Get information about an image file."""
    try:
        if not image_path or not os.path.exists(image_path):
            return None
        
        with Image.open(image_path) as img:
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
                'file_size': os.path.getsize(image_path)
            }
            
    except Exception as e:
        print(f"Error getting image info: {e}")
        return None
