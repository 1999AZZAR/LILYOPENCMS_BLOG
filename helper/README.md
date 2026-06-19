# LilyOpenCMS Test Data Generator

This directory contains helper scripts to generate test data for your LilyOpenCMS website.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r helper/requirements-helper.txt
   ```

2. **Run the automated script:**
   ```bash
   ./generate_test_data.sh
   ```

This will automatically:
- Create users (admin, general)
- Generate categories (~25)
- Create placeholder images (~20)
- Generate news articles (~500) with **full SEO optimization**
- Generate albums (~10) with chapters from existing news articles
- Add YouTube videos (~150)
- Initialize footer content

## Individual Scripts

You can also run scripts individually:

### 1. User Generation
```bash
python helper/generate_user.py
```
Creates admin and general users with default passwords:
- **Superuser:** `suladang` / `suladang`
- **Admin:** `admin0-4` / `admin_password`
- **General:** `general0-4` / `general_password`

### 2. Categories
```bash
python helper/add_chategories.py --num-cat 25
```

### 3. Images (requires server running)
```bash
python helper/add_fake_images.py
```
Automatically generates placeholder images if none exist.

### 4. News Articles (with SEO optimization)
```bash
python helper/add_fake_news.py --num-news 500 --image-prob 0.8 --link-prob 0.6
```

**New SEO Features:**
- **Meta descriptions** and **keywords** automatically generated
- **Open Graph tags** for social media sharing
- **Twitter Cards** with optimized titles and descriptions
- **Schema markup (JSON-LD)** for search engines
- **SEO scores** calculated based on content completeness
- **Canonical URLs** and **SEO-friendly slugs**
- **Meta author**, **language**, and **robots** tags

### 6. Albums (with chapters from existing news)
```bash
python helper/add_test_albums.py
```
Creates realistic albums using existing news articles as chapters:
- **Dynamic album creation** based on news categories
- **Realistic titles and descriptions** using Faker
- **Chapter management** with proper numbering
- **Cover image assignment** from existing images
- **Status tracking** (completed, hiatus, premium)
- **Requires existing news and images** (minimum 10 news, 5 images)

### 7. Videos
```bash
python helper/add_videos.py --num-vids 150
```

### 8. Footer Content
```bash
python helper/init_footer_data.py
```

## Features

- **Smart Image Generation:** Automatically creates colorful placeholder images using PIL
- **Golden Orange Theme:** Compatible with your new color scheme
- **Content Type Badges:** Generates both "Cerita" and "Kanal Info" content
- **Album Management:** Creates albums with chapters from existing news articles
- **Proper Error Handling:** Each script provides detailed feedback
- **Non-destructive:** Scripts add to existing data rather than replacing it
- **SEO-Optimized Content:** All news articles include comprehensive SEO metadata

## SEO Features Generated

The `add_fake_news.py` script now generates:

### Basic SEO
- **Meta Description:** Auto-generated from content (max 160 chars)
- **Meta Keywords:** Extracted from title and content
- **SEO Slug:** URL-friendly version of title
- **Canonical URL:** Proper URL structure

### Social Media SEO
- **Open Graph Title:** Optimized for social sharing
- **Open Graph Description:** Engaging social media descriptions
- **Open Graph Image:** Links to article images
- **Twitter Card Type:** Summary or summary_large_image
- **Twitter Title:** Optimized for Twitter (max 70 chars)
- **Twitter Description:** Twitter-specific descriptions
- **Twitter Image:** Social media optimized images

### Advanced SEO
- **Schema Markup:** JSON-LD structured data for search engines
- **Meta Author:** Article author information
- **Meta Language:** Content language (Indonesian)
- **Meta Robots:** Search engine crawling instructions
- **Structured Data Type:** NewsArticle schema type
- **SEO Score:** Calculated score (0-100) based on completeness
- **Last SEO Audit:** Timestamp of SEO optimization

## Requirements

- Python 3.7+
- Flask application
- PIL/Pillow (for image generation)
- Faker (for realistic fake data)
- Requests (for API calls)

## Troubleshooting

**Image upload fails:** Make sure your Flask server is running and you can login as `suladang` with password `suladang`.

**PIL not available:** Scripts will create text placeholders instead of images if PIL isn't installed.

**Database errors:** Ensure your database is properly initialized with `python -c "from main import app, db; app.app_context().push(); db.create_all()"`

**SEO fields missing:** The updated scripts automatically generate all SEO fields. If you see missing SEO data, ensure you're using the latest version of `add_fake_news.py`.

**Album generation fails:** Ensure you have at least 10 news articles and 5 images in your database. The script will check for minimum requirements and provide detailed feedback.

**Album chapters not showing:** Make sure the news articles used for chapters are visible (`is_visible = True`) and not archived. 