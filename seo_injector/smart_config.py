#!/usr/bin/env python3

"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Smart Configuration System for SEO Injector
Provides flexible, template-based configuration management.
"""

import yaml
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class SEOInjectionSettings:
    """SEO injection settings from database."""
    website_name: str = "Hystory"
    website_url: str = "https://hystory.id"
    website_description: str = "Hystory.id adalah platform digital karya anak bangsa yang menghadirkan novel dan cerpen terbaik Indonesia. Kami menjadi ruang bagi penulis untuk berekspresi, membangun komunitas kreatif, dan tumbuh bersama dalam ekosistem literasi digital. Dengan kisah segar, hystory.id mendukung setiap karya untuk berkembang, dikenal luas, dan memberi inspirasi."
    website_language: str = "id"
    organization_name: str = "Hystory"
    organization_logo: str = "https://hystory.id/static/pic/logo.png"
    organization_description: str = "Hystory.id adalah platform digital karya anak bangsa yang menghadirkan novel dan cerpen terbaik Indonesia. Kami menjadi ruang bagi penulis untuk berekspresi, membangun komunitas kreatif, dan tumbuh bersama dalam ekosistem literasi digital. Dengan kisah segar, hystory.id mendukung setiap karya untuk berkembang, dikenal luas, dan memberi inspirasi."
    organization_type: str = "Organization"
    facebook_url: str = ""
    twitter_url: str = ""
    instagram_url: str = ""
    youtube_url: str = ""
    linkedin_url: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    contact_address: str = ""
    default_meta_description: str = ""
    default_meta_keywords: str = ""
    default_meta_author: str = ""
    default_meta_robots: str = "index, follow"
    default_og_title: str = ""
    default_og_description: str = ""
    default_og_image: str = ""
    default_twitter_card: str = "summary"
    default_twitter_title: str = ""
    default_twitter_description: str = ""
    default_structured_data_type: str = "Article"
    default_canonical_url: str = ""
    default_meta_language: str = "id"
    auto_inject_news: bool = True
    auto_inject_albums: bool = True
    auto_inject_chapters: bool = True
    auto_inject_root: bool = True

@dataclass
class SEOTemplate:
    """SEO template configuration."""
    name: str
    description: str
    content_type: str  # news, album, chapter, root
    meta_description_template: str
    meta_keywords_template: str
    og_title_template: str
    og_description_template: str
    schema_markup_template: str
    twitter_title_template: str
    twitter_description_template: str
    variables: List[str]  # Available variables for template

@dataclass
class IndonesianKeywordCategories:
    """Indonesian keyword categories for SEO injection."""
    novel_fiction_keywords: List[str] = None
    article_news_opinion_keywords: List[str] = None
    platform_writer_keywords: List[str] = None

    def __post_init__(self):
        if self.novel_fiction_keywords is None:
            self.novel_fiction_keywords = [
                # Primary competitive keywords
                "baca novel online gratis", "novel online indonesia", "webnovel indonesia",
                "baca novel gratis", "novel online terbaru",

                # Long-tail specific keywords
                "baca novel romansa online gratis", "novel fiksi indonesia terbaru",
                "cerita roman online indonesia", "baca webnovel gratis indonesia",
                "novel online romance indonesia", "baca cerita fiksi gratis",
                "novel digital indonesia", "webnovel romansa indonesia",
                "baca novel online indonesia gratis", "novel terjemahan indonesia",

                # Content-specific keywords
                "cerita bersambung populer", "koleksi novel romansa digital",
                "platform baca fiksi gratis", "rekomendasi webnovel harian",
                "bacaan fiksi terbaru", "platform novel digital indonesia",
                "kumpulan novel online", "novel romansa terbaru",
                "cerita fiksi indonesia", "bacaan novel gratis",

                # Genre-specific keywords
                "novel romance online indonesia", "baca novel fantasy gratis",
                "novel horor online indonesia", "cerita misteri online gratis",
                "novel komedi indonesia", "baca novel drama online",
                "novel action indonesia", "cerita love story online",
                "novel wattpad indonesia", "baca novel korea online",

                # Community and social keywords
                "rekomendasi novel bagus", "novel populer indonesia",
                "baca novel trending", "cerita romantis online",
                "novel rekomendasi 2024", "baca novel viral",
                "cerita seru online", "novel terpopuler indonesia"
            ]

        if self.article_news_opinion_keywords is None:
            self.article_news_opinion_keywords = [
                # Primary news and opinion keywords
                "artikel opini masyarakat", "berita indonesia terbaru",
                "opini publik indonesia", "artikel kritis indonesia",
                "berita komunitas online",

                # Long-tail opinion pieces
                "artikel opini politik indonesia", "tulisan kritis sosial",
                "opini masyarakat digital", "artikel pendapat publik",
                "berita warga indonesia", "tulisan opini terbaru",
                "artikel masyarakat indonesia", "opini publik terkini",

                # Journalism and content keywords
                "jurnalisme warga indonesia", "tulisan kritis terbaru",
                "berita komunitas literasi", "wadah menulis artikel online",
                "opini publik terpopuler", "artikel opini indonesia",
                "platform artikel opini", "wadah menulis online",
                "opini publik digital", "tulisan warga terbaru",

                # Social and community content
                "artikel sosial indonesia", "berita masyarakat terkini",
                "opini warga indonesia", "artikel komunitas online",
                "tulisan masyarakat indonesia", "berita sosial digital",
                "artikel opini sosial", "opini komunitas indonesia",

                # Educational and informative content
                "artikel edukasi indonesia", "tulisan informatif terkini",
                "berita pendidikan online", "artikel pengetahuan indonesia",
                "opini edukasi digital", "tulisan pembelajaran online",
                "artikel literasi indonesia"
            ]

        if self.platform_writer_keywords is None:
            self.platform_writer_keywords = [
                # Primary platform keywords
                "komunitas penulis indonesia", "platform literasi digital indonesia",
                "wadah karya tulis kreatif", "platform penulis online",
                "komunitas kreatif indonesia",

                # Content creation and hosting
                "hosting cerita gratis", "platform tulis online",
                "wadah kreatif indonesia", "ekosistem penulis indie",
                "platform cerita online indonesia", "hosting karya tulis gratis",
                "wadah menulis digital",

                # Community and social features
                "komunitas penulis digital", "platform literasi online",
                "ekosistem penulis indonesia", "komunitas kreatif online",
                "wadah penulis indonesia", "platform komunitas tulis",

                # Author and creator focused
                "platform penulis indie", "wadah karya penulis",
                "komunitas pengarang indonesia", "platform tulis kreatif",
                "ekosistem kreatif indonesia", "wadah penulis digital",

                # Publishing and sharing keywords
                "platform publishing online", "wadah bagi penulis",
                "komunitas penerbit indonesia", "platform karya sastra",
                "wadah literasi digital", "ekosistem penerbit online",

                # Educational and development keywords
                "platform belajar menulis", "wadah penulis pemula",
                "komunitas penulis muda", "platform literasi indonesia",
                "wadah pengembangan tulis", "ekosistem pembelajaran kreatif"
            ]

@dataclass
class SEOQualityRules:
    """SEO quality rules and thresholds."""
    min_meta_description_length: int = 50
    max_meta_description_length: int = 160
    min_meta_keywords_length: int = 10
    max_meta_keywords_length: int = 255
    min_og_title_length: int = 10
    max_og_title_length: int = 200
    min_og_description_length: int = 50
    max_og_description_length: int = 500
    min_content_length: int = 100
    max_keywords_count: int = 10
    min_readability_score: int = 30
    min_quality_score: int = 40

class SmartConfigManager:
    """Manages SEO injection configuration with templates and rules."""

    def __init__(self, config_dir: str = "seo_injector/config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)

        # Default templates
        self.templates = self._load_default_templates()
        self.quality_rules = SEOQualityRules()
        self.settings = SEOInjectionSettings()
        self.keyword_categories = IndonesianKeywordCategories()

        # Load configuration files
        self._load_configuration()
    
    def _load_default_templates(self) -> Dict[str, SEOTemplate]:
        """Load default SEO templates."""
        templates = {}
        
        # News template
        templates['news'] = SEOTemplate(
            name="News Article",
            description="Template for news articles",
            content_type="news",
            meta_description_template="{title} - {website_name}. {excerpt}",
            meta_keywords_template="{title_keywords}, {category_keywords}, {website_name}",
            og_title_template="{title} - {website_name}",
            og_description_template="{excerpt}",
            schema_markup_template="""
            {
                "@context": "https://schema.org",
                "@type": "NewsArticle",
                "headline": "{title}",
                "description": "{excerpt}",
                "author": {
                    "@type": "Person",
                    "name": "{author}"
                },
                "publisher": {
                    "@type": "Organization",
                    "name": "{organization_name}",
                    "logo": {
                        "@type": "ImageObject",
                        "url": "{organization_logo}"
                    }
                },
                "datePublished": "{date_published}",
                "dateModified": "{date_modified}",
                "mainEntityOfPage": {
                    "@type": "WebPage",
                    "@id": "{canonical_url}"
                }
            }
            """,
            twitter_title_template="{title} - {website_name}",
            twitter_description_template="{excerpt}",
            variables=["title", "excerpt", "author", "category", "date_published", "date_modified", "canonical_url", "website_name", "organization_name", "organization_logo", "title_keywords", "category_keywords"]
        )
        
        # Album template
        templates['album'] = SEOTemplate(
            name="Album/Story Collection",
            description="Template for album/story collections",
            content_type="album",
            meta_description_template="{title} - {description} by {author}. {chapter_count} chapters available on {website_name}.",
            meta_keywords_template="{title_keywords}, {author}, {category_keywords}, story, chapters, {website_name}",
            og_title_template="{title} by {author} - {website_name}",
            og_description_template="{description}",
            schema_markup_template="""
            {
                "@context": "https://schema.org",
                "@type": "Book",
                "name": "{title}",
                "description": "{description}",
                "author": {
                    "@type": "Person",
                    "name": "{author}"
                },
                "publisher": {
                    "@type": "Organization",
                    "name": "{organization_name}"
                },
                "numberOfPages": "{chapter_count}",
                "inLanguage": "{language}",
                "datePublished": "{date_published}",
                "dateModified": "{date_modified}"
            }
            """,
            twitter_title_template="{title} by {author}",
            twitter_description_template="{description}",
            variables=["title", "description", "author", "category", "chapter_count", "date_published", "date_modified", "language", "website_name", "organization_name"]
        )
        
        # Chapter template
        templates['chapter'] = SEOTemplate(
            name="Chapter/Episode",
            description="Template for individual chapters",
            content_type="chapter",
            meta_description_template="Chapter {chapter_number}: {title} - {album_title} by {author} on {website_name}.",
            meta_keywords_template="{title_keywords}, {album_title}, {author}, chapter {chapter_number}, {category_keywords}, {website_name}",
            og_title_template="Chapter {chapter_number}: {title} - {album_title}",
            og_description_template="{excerpt}",
            schema_markup_template="""
            {
                "@context": "https://schema.org",
                "@type": "Chapter",
                "name": "{title}",
                "description": "{excerpt}",
                "author": {
                    "@type": "Person",
                    "name": "{author}"
                },
                "isPartOf": {
                    "@type": "Book",
                    "name": "{album_title}"
                },
                "position": "{chapter_number}",
                "datePublished": "{date_published}",
                "dateModified": "{date_modified}"
            }
            """,
            twitter_title_template="Chapter {chapter_number}: {title}",
            twitter_description_template="{excerpt}",
            variables=["title", "excerpt", "author", "album_title", "chapter_number", "category", "date_published", "date_modified", "website_name"]
        )
        
        # Root page template
        templates['root'] = SEOTemplate(
            name="Website Page",
            description="Template for root website pages",
            content_type="root",
            meta_description_template="{page_description} - {website_name}. {website_description}",
            meta_keywords_template="{page_keywords}, {website_name}, {organization_name}",
            og_title_template="{page_title} - {website_name}",
            og_description_template="{page_description}",
            schema_markup_template="""
            {
                "@context": "https://schema.org",
                "@type": "WebPage",
                "name": "{page_title}",
                "description": "{page_description}",
                "url": "{canonical_url}",
                "publisher": {
                    "@type": "Organization",
                    "name": "{organization_name}",
                    "url": "{website_url}"
                },
                "datePublished": "{date_published}",
                "dateModified": "{date_modified}"
            }
            """,
            twitter_title_template="{page_title} - {website_name}",
            twitter_description_template="{page_description}",
            variables=["page_title", "page_description", "page_keywords", "canonical_url", "website_name", "website_url", "organization_name", "date_published", "date_modified"]
        )
        
        return templates
    
    def _load_configuration(self):
        """Load configuration from files."""
        # Load settings from database (if available)
        try:
            self._load_database_settings()
        except Exception as e:
            print(f"Warning: Could not load database settings: {e}")

        # Load custom templates
        self._load_custom_templates()

        # Load quality rules
        self._load_quality_rules()

        # Load Indonesian keyword categories
        self._load_keyword_categories()
    
    def _load_database_settings(self):
        """Load settings from database."""
        # This would connect to the database and load SEO injection settings
        # For now, we'll use default values
    
    def _load_custom_templates(self):
        """Load custom templates from files."""
        templates_file = self.config_dir / "templates.yaml"
        if templates_file.exists():
            try:
                with open(templates_file, 'r', encoding='utf-8') as f:
                    templates_data = yaml.safe_load(f)
                
                for template_name, template_data in templates_data.items():
                    if template_name in self.templates:
                        # Update existing template
                        for key, value in template_data.items():
                            if hasattr(self.templates[template_name], key):
                                setattr(self.templates[template_name], key, value)
            except Exception as e:
                print(f"Warning: Could not load custom templates: {e}")
    
    def _load_quality_rules(self):
        """Load quality rules from file."""
        rules_file = self.config_dir / "quality_rules.yaml"
        if rules_file.exists():
            try:
                with open(rules_file, 'r', encoding='utf-8') as f:
                    rules_data = yaml.safe_load(f)
                
                for key, value in rules_data.items():
                    if hasattr(self.quality_rules, key):
                        setattr(self.quality_rules, key, value)
            except Exception as e:
                print(f"Warning: Could not load quality rules: {e}")
    
    def get_template(self, content_type: str) -> Optional[SEOTemplate]:
        """Get template for content type."""
        return self.templates.get(content_type)
    
    def get_quality_rules(self) -> SEOQualityRules:
        """Get quality rules."""
        return self.quality_rules
    
    def get_settings(self) -> SEOInjectionSettings:
        """Get SEO injection settings."""
        return self.settings
    
    def save_template(self, template: SEOTemplate):
        """Save a template to file."""
        templates_file = self.config_dir / "templates.yaml"
        
        # Load existing templates
        templates_data = {}
        if templates_file.exists():
            try:
                with open(templates_file, 'r', encoding='utf-8') as f:
                    templates_data = yaml.safe_load(f) or {}
            except:
                templates_data = {}
        
        # Update template
        templates_data[template.name.lower()] = asdict(template)
        
        # Save to file
        with open(templates_file, 'w', encoding='utf-8') as f:
            yaml.dump(templates_data, f, default_flow_style=False, allow_unicode=True)
    
    def save_quality_rules(self, rules: SEOQualityRules):
        """Save quality rules to file."""
        rules_file = self.config_dir / "quality_rules.yaml"

        with open(rules_file, 'w', encoding='utf-8') as f:
            yaml.dump(asdict(rules), f, default_flow_style=False, allow_unicode=True)

    def _load_keyword_categories(self):
        """Load Indonesian keyword categories from file."""
        keywords_file = self.config_dir / "indonesian_keywords.yaml"
        if keywords_file.exists():
            try:
                with open(keywords_file, 'r', encoding='utf-8') as f:
                    keywords_data = yaml.safe_load(f) or {}

                # Update keyword categories if they exist in the file
                if 'novel_fiction_keywords' in keywords_data:
                    self.keyword_categories.novel_fiction_keywords = keywords_data['novel_fiction_keywords']
                if 'article_news_opinion_keywords' in keywords_data:
                    self.keyword_categories.article_news_opinion_keywords = keywords_data['article_news_opinion_keywords']
                if 'platform_writer_keywords' in keywords_data:
                    self.keyword_categories.platform_writer_keywords = keywords_data['platform_writer_keywords']
            except Exception as e:
                print(f"Warning: Could not load Indonesian keyword categories: {e}")

    def save_keyword_categories(self, categories: IndonesianKeywordCategories):
        """Save Indonesian keyword categories to file."""
        keywords_file = self.config_dir / "indonesian_keywords.yaml"

        keywords_data = {
            'novel_fiction_keywords': categories.novel_fiction_keywords,
            'article_news_opinion_keywords': categories.article_news_opinion_keywords,
            'platform_writer_keywords': categories.platform_writer_keywords
        }

        with open(keywords_file, 'w', encoding='utf-8') as f:
            yaml.dump(keywords_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    def create_default_config_files(self):
        """Create default configuration files."""
        # Create templates file
        templates_file = self.config_dir / "templates.yaml"
        if not templates_file.exists():
            templates_data = {}
            for template_name, template in self.templates.items():
                templates_data[template_name] = asdict(template)

            with open(templates_file, 'w', encoding='utf-8') as f:
                yaml.dump(templates_data, f, default_flow_style=False, allow_unicode=True)

        # Create quality rules file
        rules_file = self.config_dir / "quality_rules.yaml"
        if not rules_file.exists():
            with open(rules_file, 'w', encoding='utf-8') as f:
                yaml.dump(asdict(self.quality_rules), f, default_flow_style=False, allow_unicode=True)

        # Create settings file
        settings_file = self.config_dir / "settings.yaml"
        if not settings_file.exists():
            with open(settings_file, 'w', encoding='utf-8') as f:
                yaml.dump(asdict(self.settings), f, default_flow_style=False, allow_unicode=True)

        # Create Indonesian keywords file
        keywords_file = self.config_dir / "indonesian_keywords.yaml"
        if not keywords_file.exists():
            keywords_data = {
                'novel_fiction_keywords': self.keyword_categories.novel_fiction_keywords,
                'article_news_opinion_keywords': self.keyword_categories.article_news_opinion_keywords,
                'platform_writer_keywords': self.keyword_categories.platform_writer_keywords
            }

            with open(keywords_file, 'w', encoding='utf-8') as f:
                yaml.dump(keywords_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    def validate_template(self, template: SEOTemplate) -> List[str]:
        """Validate a template configuration."""
        issues = []
        
        # Check required fields
        if not template.name:
            issues.append("Template name is required")
        
        if not template.content_type:
            issues.append("Content type is required")
        
        if not template.meta_description_template:
            issues.append("Meta description template is required")
        
        # Check template variables
        if not template.variables:
            issues.append("Template variables are required")
        
        # Check template syntax (basic validation)
        try:
            template.meta_description_template.format(**{var: "test" for var in template.variables})
        except KeyError as e:
            issues.append(f"Missing variable in meta description template: {e}")
        except Exception as e:
            issues.append(f"Invalid template syntax: {e}")
        
        return issues
    
    def get_available_variables(self, content_type: str) -> List[str]:
        """Get available variables for a content type."""
        template = self.get_template(content_type)
        if template:
            return template.variables
        return []

    def get_keyword_categories(self) -> IndonesianKeywordCategories:
        """Get Indonesian keyword categories."""
        return self.keyword_categories

    def update_keyword_category(self, category: str, keywords: List[str]):
        """Update a specific keyword category."""
        if category == 'novel_fiction':
            self.keyword_categories.novel_fiction_keywords = keywords
        elif category == 'article_news_opinion':
            self.keyword_categories.article_news_opinion_keywords = keywords
        elif category == 'platform_writer':
            self.keyword_categories.platform_writer_keywords = keywords

        # Save updated categories
        self.save_keyword_categories(self.keyword_categories)
    
    def generate_seo_data(self, content_type: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SEO data using template and content data."""
        template = self.get_template(content_type)
        if not template:
            raise ValueError(f"No template found for content type: {content_type}")

        # Prepare variables for template
        template_vars = {}
        for var in template.variables:
            template_vars[var] = content_data.get(var, "")

        # Generate meta keywords with smart Indonesian injection
        meta_keywords = self._generate_smart_keywords(content_type, content_data, template.meta_keywords_template, template_vars)

        # Generate SEO data with error handling
        seo_data = {
            'meta_keywords': meta_keywords,
        }

        # Try to format each template, use fallback if it fails
        try:
            seo_data['meta_description'] = template.meta_description_template.format(**template_vars)
        except Exception:
            seo_data['meta_description'] = f"{content_data.get('title', '')} - {content_data.get('website_name', '')}"

        try:
            seo_data['og_title'] = template.og_title_template.format(**template_vars)
        except Exception:
            seo_data['og_title'] = content_data.get('title', '')

        try:
            seo_data['og_description'] = template.og_description_template.format(**template_vars)
        except Exception:
            seo_data['og_description'] = content_data.get('excerpt', '')

        try:
            seo_data['schema_markup'] = template.schema_markup_template.format(**template_vars)
        except Exception:
            seo_data['schema_markup'] = '{}'

        try:
            seo_data['twitter_title'] = template.twitter_title_template.format(**template_vars)
        except Exception:
            seo_data['twitter_title'] = content_data.get('title', '')

        try:
            seo_data['twitter_description'] = template.twitter_description_template.format(**template_vars)
        except Exception:
            seo_data['twitter_description'] = content_data.get('excerpt', '')

        return seo_data

    def _generate_smart_keywords(self, content_type: str, content_data: Dict[str, Any], template: str, template_vars: Dict[str, Any]) -> str:
        """Generate smart keywords with Indonesian category injection."""
        try:
            # Start with template-based keywords
            base_keywords = template.format(**template_vars)
        except Exception as e:
            # If template fails, generate basic keywords
            print(f"Warning: Template formatting failed: {e}, using fallback")
            base_keywords = self._generate_fallback_keywords(content_data)

        # Detect content category and inject Indonesian keywords
        content_category = self._detect_content_category(content_type, content_data)

        # Get appropriate Indonesian keywords
        indonesian_keywords = self._get_indonesian_keywords_for_category(content_category)

        # Combine and optimize keywords
        final_keywords = self._combine_keywords(base_keywords, indonesian_keywords, content_data)

        return final_keywords

    def _generate_fallback_keywords(self, content_data: Dict[str, Any]) -> str:
        """Generate fallback keywords when template fails."""
        keywords = []

        # Add title keywords
        title = content_data.get('title', '')
        if title:
            title_words = [word.lower() for word in title.split() if len(word) > 2]
            keywords.extend(title_words[:3])

        # Add category
        category = content_data.get('category', '')
        if category:
            keywords.append(category.lower())

        # Add website name
        website_name = content_data.get('website_name', '')
        if website_name:
            keywords.append(website_name.lower())

        return ', '.join(keywords[:8])

    def _detect_content_category(self, content_type: str, content_data: Dict[str, Any]) -> str:
        """Detect the content category for keyword injection."""
        # Prioritize content type for known categories
        if content_type in ['album', 'chapter']:
            return 'novel_fiction'
        elif content_type == 'news':
            return 'article_news_opinion'
        elif content_type == 'root':
            # For root pages, analyze the page content
            page_identifier = content_data.get('page_identifier', '')
            if page_identifier in ['albums', 'stories']:
                return 'novel_fiction'
            elif page_identifier in ['news', 'articles']:
                return 'article_news_opinion'
            else:
                return 'platform_writer'

        # Analyze content for keywords (fallback for unknown content types)
        content_text = ""
        title_text = ""

        if 'content' in content_data:
            content_text = str(content_data['content']).lower()
        if 'title' in content_data:
            title_text = str(content_data['title']).lower()
        if 'description' in content_data:
            content_text += " " + str(content_data['description']).lower()

        combined_text = f"{title_text} {content_text}"

        # Strong novel/fiction indicators (only if not already categorized by type)
        novel_keywords = ['novel', 'cerita', 'fiksi', 'roman', 'chapter', 'bab', 'story', 'webnovel']
        if any(keyword in combined_text for keyword in novel_keywords):
            return 'novel_fiction'

        # Article/News/Opinion indicators
        article_keywords = ['artikel', 'berita', 'opini', 'tulisan', 'kritik', 'analisis', 'komentar', 'pendapat']
        if any(keyword in combined_text for keyword in article_keywords):
            return 'article_news_opinion'

        # Platform/Writer indicators
        platform_keywords = ['penulis', 'komunitas', 'platform', 'hosting', 'karya', 'tulisan', 'konten', 'digital']
        if any(keyword in combined_text for keyword in platform_keywords):
            return 'platform_writer'

        # Default fallback
        return 'article_news_opinion'

    def _get_indonesian_keywords_for_category(self, category: str) -> List[str]:
        """Get Indonesian keywords for a specific category."""
        if category == 'novel_fiction':
            return self.keyword_categories.novel_fiction_keywords[:5]  # Limit to top 5
        elif category == 'article_news_opinion':
            return self.keyword_categories.article_news_opinion_keywords[:5]
        elif category == 'platform_writer':
            return self.keyword_categories.platform_writer_keywords[:5]
        else:
            return self.keyword_categories.article_news_opinion_keywords[:3]  # Default

    def _combine_keywords(self, base_keywords: str, indonesian_keywords: List[str], content_data: Dict[str, Any]) -> str:
        """Combine base keywords with Indonesian keywords intelligently."""
        # Split base keywords
        base_list = [kw.strip() for kw in base_keywords.split(',') if kw.strip()]

        # Add Indonesian keywords
        combined_list = base_list + indonesian_keywords

        # Remove duplicates (case insensitive)
        seen = set()
        unique_keywords = []
        for keyword in combined_list:
            lower_kw = keyword.lower().strip()
            if lower_kw not in seen and len(lower_kw) > 2:
                seen.add(lower_kw)
                unique_keywords.append(keyword)

        # Limit to 10 keywords max
        final_keywords = unique_keywords[:10]

        return ', '.join(final_keywords)
