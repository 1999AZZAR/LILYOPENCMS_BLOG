#!/bin/bash

: <<'OFF'
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
OFF

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "=== LilyOpenCMS Test Data Generator ==="
echo "Project root: $PROJECT_ROOT"

# Check for required Python packages
echo ""
echo "=== Checking Dependencies ==="
python -c "
try:
    import requests, faker
    from PIL import Image
    print('✅ All required packages are available')
except ImportError as e:
    print(f'❌ Missing package: {e}')
    print('Please install with: pip install -r helper/requirements-helper.txt')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "Please install missing dependencies and try again."
    exit 1
fi

# Ensure database schema is up to date
echo ""
echo "=== Setting up Database Schema ==="
python -c "
from models import db
from main import app
app.app_context().push()
db.create_all()
print('✅ Database schema created successfully')
"

if [ $? -ne 0 ]; then
    echo "❌ Failed to create database schema"
    exit 1
fi

# Initialize permissions first
echo ""
echo "=== Initializing Permissions ==="
python helper/init_permissions.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to initialize permissions"
    exit 1
fi

# Generate users
echo ""
echo "=== Generating Users ==="
python helper/generate_user.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to generate users"
    exit 1
fi

# Generate categories
echo ""
echo "=== Generating Categories ==="
python helper/add_chategories.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to generate categories"
    exit 1
fi

# Generate images
echo ""
echo "=== Generating Images ==="
python helper/add_fake_images.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to generate images"
    exit 1
fi

# Generate news articles
echo ""
echo "=== Generating News Articles ==="
python helper/add_fake_news.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to generate news articles"
    exit 1
fi

# Generate albums
echo ""
echo "=== Generating Albums ==="
python helper/add_test_albums.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to generate albums"
    exit 1
fi

# Add videos
echo ""
echo "=== Adding Videos ==="
python helper/add_videos.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to add videos"
    exit 1
fi

# Initialize footer data
echo ""
echo "=== Initializing Footer Data ==="
python helper/init_footer_data.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to initialize footer data"
    exit 1
fi

echo ""
echo "=== Test Data Generation Complete ==="
echo "✅ Database has been populated with test data"
echo "✅ Users, categories, images, news, and videos have been created"
echo "✅ Permissions have been initialized"
echo ""
echo "You can now start the application with: python main.py"
