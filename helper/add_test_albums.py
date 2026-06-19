#!/usr/bin/env python3
"""
Helper script to add test album data to the database.
This script creates sample albums with chapters using real data from the database.
Only runs if sufficient data is available.
"""

import sys
import os
import random

# Add the parent directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Now import the app
from main import app
from models import db, Album, AlbumChapter, News, Category, User, UserRole, Image
from faker import Faker

# Initialize Faker for generating fake data
fake = Faker()

def generate_album_title(category_name):
    """Generate realistic album titles based on category."""
    title_templates = {
        'Teknologi': [
            "Seri {category}: {topic}",
            "{topic} di Era Digital",
            "Panduan Lengkap {topic}",
            "Eksplorasi {topic}",
            "Seri {category}: {topic} Terkini"
        ],
        'Bisnis': [
            "Strategi {topic} untuk Bisnis",
            "Panduan {topic} di {category}",
            "Seri {category}: {topic}",
            "Masterclass {topic}",
            "Seri {category}: {topic} Sukses"
        ],
        'Lifestyle': [
            "Seri {category}: {topic}",
            "Panduan {topic} untuk Hidup Sehat",
            "Seri {category}: {topic} Terkini",
            "Eksplorasi {topic}",
            "Seri {category}: {topic} Populer"
        ],
        'Travel': [
            "Petualangan {topic}",
            "Seri {category}: {topic}",
            "Panduan Wisata {topic}",
            "Eksplorasi {topic}",
            "Seri {category}: {topic} Terbaik"
        ],
        'Kesehatan': [
            "Seri {category}: {topic}",
            "Panduan {topic} untuk Kesehatan",
            "Seri {category}: {topic} Terkini",
            "Eksplorasi {topic}",
            "Seri {category}: {topic} Sehat"
        ],
        'Pendidikan': [
            "Seri {category}: {topic}",
            "Panduan {topic} untuk Belajar",
            "Seri {category}: {topic} Terkini",
            "Eksplorasi {topic}",
            "Seri {category}: {topic} Berkualitas"
        ]
    }
    
    # Get templates for this category or use default
    templates = title_templates.get(category_name, [
        "Seri {category}: {topic}",
        "Panduan {topic}",
        "Eksplorasi {topic}",
        "Seri {category}: {topic} Terkini"
    ])
    
    # Generate topic based on category
    topics = {
        'Teknologi': ['AI dan Machine Learning', 'Blockchain', 'Cloud Computing', 'Cybersecurity', 'IoT', 'Mobile Development', 'Web Development', 'Data Science'],
        'Bisnis': ['Startup', 'Marketing Digital', 'E-commerce', 'Investasi', 'Manajemen', 'Strategi Bisnis', 'Fintech', 'Entrepreneurship'],
        'Lifestyle': ['Fashion', 'Beauty', 'Fitness', 'Wellness', 'Hobi', 'Entertainment', 'Food', 'Home Living'],
        'Travel': ['Backpacking', 'Budget Travel', 'Luxury Travel', 'Adventure', 'Cultural Tourism', 'Food Tourism', 'Eco Tourism', 'City Exploration'],
        'Kesehatan': ['Nutrisi', 'Mental Health', 'Physical Fitness', 'Preventive Care', 'Alternative Medicine', 'Wellness', 'Medical Technology'],
        'Pendidikan': ['Online Learning', 'Skill Development', 'Language Learning', 'Academic Research', 'Educational Technology', 'Teaching Methods']
    }
    
    category_topics = topics.get(category_name, ['Pembelajaran', 'Eksplorasi', 'Panduan', 'Seri'])
    topic = random.choice(category_topics)
    
    template = random.choice(templates)
    return template.format(category=category_name, topic=topic)

def generate_album_description(category_name, title):
    """Generate realistic album descriptions."""
    description_templates = [
        "Kumpulan artikel {category} yang dikurasi dengan baik untuk memberikan wawasan mendalam tentang {topic}.",
        "Seri lengkap tentang {topic} dalam kategori {category} yang disusun secara sistematis untuk memudahkan pembelajaran.",
        "Eksplorasi mendalam tentang {topic} melalui berbagai artikel {category} yang informatif dan up-to-date.",
        "Panduan komprehensif tentang {topic} yang mencakup aspek-aspek penting dalam dunia {category}.",
        "Koleksi artikel terbaik tentang {topic} yang dipilih untuk memberikan perspektif yang luas dalam {category}."
    ]
    
    # Extract topic from title
    topic = title.replace(f"Seri {category_name}: ", "").replace(f" di Era Digital", "").replace(f" untuk Bisnis", "").replace(f" untuk Hidup Sehat", "").replace(f" Terkini", "").replace(f" Populer", "").replace(f" Sukses", "").replace(f" Sehat", "").replace(f" Berkualitas", "").replace(f" Terbaik", "")
    
    template = random.choice(description_templates)
    return template.format(category=category_name, topic=topic)

def generate_chapter_title(album_title, chapter_number, category_name):
    """Generate realistic chapter titles based on album theme."""
    # Extract main topic from album title
    main_topic = album_title.replace(f"Seri {category_name}: ", "").replace(f" di Era Digital", "").replace(f" untuk Bisnis", "").replace(f" untuk Hidup Sehat", "").replace(f" Terkini", "").replace(f" Populer", "").replace(f" Sukses", "").replace(f" Sehat", "").replace(f" Berkualitas", "").replace(f" Terbaik", "")
    
    chapter_templates = {
        'Teknologi': [
            "Pengenalan {topic}",
            "Dasar-dasar {topic}",
            "Implementasi {topic}",
            "Best Practices {topic}",
            "Trend {topic} Terkini",
            "Case Study {topic}"
        ],
        'Bisnis': [
            "Strategi {topic}",
            "Analisis {topic}",
            "Implementasi {topic}",
            "Success Story {topic}",
            "Tips dan Trik {topic}",
            "Future of {topic}"
        ],
        'Lifestyle': [
            "Panduan {topic}",
            "Tips {topic}",
            "Trend {topic}",
            "Inspirasi {topic}",
            "How-to {topic}",
            "Best of {topic}"
        ],
        'Travel': [
            "Destinasi {topic}",
            "Panduan {topic}",
            "Tips {topic}",
            "Experience {topic}",
            "Hidden Gem {topic}",
            "Must-visit {topic}"
        ],
        'Kesehatan': [
            "Panduan {topic}",
            "Tips {topic}",
            "Manfaat {topic}",
            "Cara {topic}",
            "Best Practice {topic}",
            "Research {topic}"
        ],
        'Pendidikan': [
            "Pengenalan {topic}",
            "Metode {topic}",
            "Strategi {topic}",
            "Best Practice {topic}",
            "Case Study {topic}",
            "Future of {topic}"
        ]
    }
    
    templates = chapter_templates.get(category_name, [
        "Pengenalan {topic}",
        "Panduan {topic}",
        "Tips {topic}",
        "Best Practice {topic}",
        "Case Study {topic}"
    ])
    
    template = random.choice(templates)
    return template.format(topic=main_topic)

def add_test_albums():
    """Add test album data to the database using real data."""
    with app.app_context():
        print("🎵 Adding test album data using real database content...")
        
        # Get existing data
        users = User.query.filter(User.role.in_([UserRole.ADMIN, UserRole.SUPERUSER])).all()
        categories = Category.query.all()
        news_articles = News.query.filter_by(is_visible=True).all()
        images = Image.query.all()  # Get all images, visibility doesn't matter for cover images
        
        # Check minimum requirements
        if not users:
            print("❌ No admin users found. Please add users first.")
            return
        
        if not categories:
            print("❌ No categories found. Please add categories first.")
            return
        
        if len(news_articles) < 10:
            print(f"❌ Insufficient news articles ({len(news_articles)}). Need at least 10 articles.")
            return
        
        if len(images) < 5:
            print(f"❌ Insufficient images ({len(images)}). Need at least 5 images.")
            print(f"   Available images: {[img.filename for img in images[:3]]}...")
            return
        
        print(f"✅ Found {len(users)} admin users, {len(categories)} categories, {len(news_articles)} news articles, {len(images)} images")
        
        # Debug image information
        visible_images = Image.query.filter_by(is_visible=True).count()
        print(f"   - Total images: {len(images)}")
        print(f"   - Visible images: {visible_images}")
        print(f"   - Hidden images: {len(images) - visible_images}")
        print(f"   - Using all images for album covers (visibility status ignored)")
        
        # Create albums based on real news content
        albums_data = []
        
        # Group news by category to create themed albums
        news_by_category = {}
        for news in news_articles:
            if news.category:
                cat_name = news.category.name
                if cat_name not in news_by_category:
                    news_by_category[cat_name] = []
                news_by_category[cat_name].append(news)
        
        # Create albums from real news content
        for category_name, category_news in news_by_category.items():
            if len(category_news) >= 3:  # Need at least 3 articles for an album
                # Generate realistic title and description
                album_title = generate_album_title(category_name)
                album_description = generate_album_description(category_name, album_title)
                
                # Determine if premium based on category
                premium_categories = ['Teknologi', 'Bisnis', 'Investasi', 'Lifestyle', 'Kesehatan']
                is_premium = any(premium in category_name for premium in premium_categories)
                
                # Create chapters from actual news with realistic titles
                chapters = []
                for i, news in enumerate(category_news[:6], 1):  # Max 6 chapters
                    chapter_title = generate_chapter_title(album_title, i, category_name)
                    chapters.append({
                        "news_id": news.id,
                        "title": chapter_title,
                        "number": i
                    })
                
                albums_data.append({
                    "title": album_title,
                    "description": album_description,
                    "is_premium": is_premium,
                    "is_visible": True,
                    "is_completed": len(chapters) >= 5,  # Complete if 5+ chapters
                    "is_hiatus": False,
                    "category_id": category_news[0].category_id,
                    "chapters": chapters
                })
        
        # If we don't have enough category-based albums, create mixed albums
        if len(albums_data) < 3:
            print("📝 Creating mixed-content albums...")
            
            # Create mixed albums from remaining news
            remaining_news = [n for n in news_articles if not any(n.id in [c["news_id"] for c in album["chapters"]] for album in albums_data)]
            
            if len(remaining_news) >= 4:
                mixed_albums = [
                    {
                        "title": "Kumpulan Artikel Terpopuler",
                        "description": "Artikel-artikel dengan pembacaan tertinggi yang dikurasi khusus untuk pembaca setia",
                        "is_premium": False,
                        "is_visible": True,
                        "is_completed": True,
                        "is_hiatus": False,
                        "category_id": random.choice(categories).id,
                        "chapters": [{"news_id": n.id, "title": f"Artikel Populer #{i+1}", "number": i+1} 
                                   for i, n in enumerate(remaining_news[:5])]
                    },
                    {
                        "title": "Seri Artikel Terbaru",
                        "description": "Artikel-artikel terbaru yang layak dibaca dan memberikan wawasan terkini",
                        "is_premium": True,
                        "is_visible": True,
                        "is_completed": False,
                        "is_hiatus": False,
                        "category_id": random.choice(categories).id,
                        "chapters": [{"news_id": n.id, "title": f"Artikel Terbaru #{i+1}", "number": i+1} 
                                   for i, n in enumerate(remaining_news[5:10])]
                    }
                ]
                albums_data.extend(mixed_albums)
        
        if not albums_data:
            print("❌ Could not create albums from available content.")
            return
        
        print(f"📚 Creating {len(albums_data)} albums from real content...")
        
        created_albums = 0
        
        for album_data in albums_data:
            try:
                # Select random admin user
                user = random.choice(users)
                
                # Select random cover image
                cover_image = random.choice(images) if images else None
                
                # Create album
                album = Album(
                    title=album_data["title"],
                    description=album_data["description"],
                    category_id=album_data["category_id"],
                    user_id=user.id,
                    cover_image_id=cover_image.id if cover_image else None,
                    is_premium=album_data["is_premium"],
                    is_visible=album_data["is_visible"],
                    is_completed=album_data["is_completed"],
                    is_hiatus=album_data["is_hiatus"],
                    is_archived=False,
                    total_chapters=0,
                    total_reads=random.randint(0, 500)
                )
                
                album.validate()
                db.session.add(album)
                db.session.flush()  # Get the album ID
                
                # Add chapters from real news articles
                chapter_count = 0
                for chapter_data in album_data["chapters"]:
                    chapter = AlbumChapter(
                        album_id=album.id,
                        news_id=chapter_data["news_id"],
                        chapter_title=chapter_data["title"],
                        chapter_number=chapter_data["number"],
                        is_visible=True
                    )
                    
                    chapter.validate()
                    db.session.add(chapter)
                    chapter_count += 1
                
                # Update album chapter count
                album.total_chapters = chapter_count
                
                created_albums += 1
                category_name = next((cat.name for cat in categories if cat.id == album_data["category_id"]), "Unknown")
                print(f"✅ Created album: {album.title} ({category_name}) with {chapter_count} chapters by {user.username}")
                
            except Exception as e:
                print(f"❌ Error creating album '{album_data['title']}': {e}")
                db.session.rollback()
                continue
        
        try:
            db.session.commit()
            print(f"\n🎉 Successfully created {created_albums} albums from real content!")
            print("📊 Album Statistics:")
            print(f"   - Total albums created: {created_albums}")
            print(f"   - Premium albums: {Album.query.filter_by(is_premium=True).count()}")
            print(f"   - Completed albums: {Album.query.filter_by(is_completed=True).count()}")
            print(f"   - Hiatus albums: {Album.query.filter_by(is_hiatus=True).count()}")
            print(f"   - Total chapters created: {AlbumChapter.query.count()}")
            print("You can now test the album management functionality.")
        except Exception as e:
            print(f"❌ Error committing to database: {e}")
            db.session.rollback()

if __name__ == "__main__":
    add_test_albums() 