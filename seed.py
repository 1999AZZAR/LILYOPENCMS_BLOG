#!/usr/bin/env python3
"""
Seed script — run on first startup to populate the database.
Creates superuser account + sample data for testing.

Usage:
    python seed.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import (
    db, User, UserRole, Category, News, BrandIdentity,
    SocialMedia, ContactDetail, NavigationLink, Permission, CustomRole,
)


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # ── Superuser ────────────────────────────────────────────────────
        if not User.query.filter_by(username="suadmin").first():
            su = User(
                username="suadmin",
                email="admin@lilyopencms.local",
                role=UserRole.SUPERUSER,
                is_active=True,
                is_premium=True,
                first_name="Super",
                last_name="Admin",
            )
            su.set_password("suladang")
            db.session.add(su)
            print("  + Created superuser: suadmin / suladang")
        else:
            print("  ~ Superuser already exists")

        # ── Admin user ───────────────────────────────────────────────────
        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                email="admin@example.com",
                role=UserRole.ADMIN,
                is_active=True,
                first_name="Admin",
                last_name="User",
            )
            admin.set_password("admin123")
            db.session.add(admin)
            print("  + Created admin: admin / admin123")
        else:
            print("  ~ Admin already exists")

        # ── General user ─────────────────────────────────────────────────
        if not User.query.filter_by(username="user").first():
            u = User(
                username="user",
                email="user@example.com",
                role=UserRole.GENERAL,
                is_active=True,
                first_name="Test",
                last_name="User",
            )
            u.set_password("user123")
            db.session.add(u)
            print("  + Created user: user / user123")
        else:
            print("  ~ User already exists")

        db.session.flush()

        # ── Categories ───────────────────────────────────────────────────
        cat_names = ["Teknologi", "Bisnis", "Olahraga", "Hiburan", "Kesehatan"]
        categories = {}
        for name in cat_names:
            cat = Category.query.filter_by(name=name).first()
            if not cat:
                cat = Category(name=name)
                db.session.add(cat)
                print(f"  + Created category: {name}")
            categories[name] = cat

        db.session.flush()

        # ── Sample News ──────────────────────────────────────────────────
        su = User.query.filter_by(username="suadmin").first()
        cat_tek = categories["Teknologi"]
        cat_bis = categories["Bisnis"]

        if News.query.count() == 0:
            articles = [
                News(
                    title="Selamat Datang di LilyOpenCMS",
                    content="<p>Sistem manajemen konten modern berbasis Flask.</p><p>LilyOpenCMS dirancang untuk kemudahan penggunaan dan performa tinggi.</p>",
                    user_id=su.id,
                    category_id=cat_tek.id,
                    is_visible=True,
                    is_main_news=True,
                    is_news=True,
                    tagar="lily,cms,flask",
                    writer="Super Admin",
                ),
                News(
                    title="Fitur Unggulan LilyOpenCMS",
                    content="<p>Multi-design system, modular architecture, Docker-ready, dan integrasi sidecar untuk observability.</p>",
                    user_id=su.id,
                    category_id=cat_tek.id,
                    is_visible=True,
                    is_news=True,
                    tagar="fitur,modular,docker",
                    writer="Super Admin",
                ),
                News(
                    title="Tips Manajemen Konten Efektif",
                    content="<p>Konten yang baik dimulai dari perencanaan. Gunakan fitur scheduling untuk mempublikasikan artikel tepat waktu.</p>",
                    user_id=su.id,
                    category_id=cat_bis.id,
                    is_visible=True,
                    is_news=True,
                    tagar="tips,konten,manajemen",
                    writer="Super Admin",
                ),
                News(
                    title="Panduan Setup Development Environment",
                    content="<p>Clone repo, jalankan <code>docker compose up</code>, dan mulai mengembangkan. PostgreSQL, Redis, dan semua sidecar sudah terkonfigurasi.</p>",
                    user_id=su.id,
                    category_id=cat_tek.id,
                    is_visible=True,
                    is_news=True,
                    tagar="tutorial,development,docker",
                    writer="Super Admin",
                ),
                News(
                    title="Optimasi Performa Aplikasi Web",
                    content="<p>Gunakan caching, connection pooling, dan async workers untuk meningkatkan performa aplikasi web Anda.</p>",
                    user_id=su.id,
                    category_id=cat_bis.id,
                    is_visible=True,
                    is_news=True,
                    tagar="performa,optimasi,caching",
                    writer="Super Admin",
                ),
            ]
            for a in articles:
                db.session.add(a)
            print(f"  + Created {len(articles)} sample news articles")
        else:
            print("  ~ News already exists, skipping")

        # ── Brand Identity ───────────────────────────────────────────────
        if not BrandIdentity.query.first():
            brand = BrandIdentity(
                brand_name="LilyOpenCMS",
                tagline="Modern content management for the digital age",
                homepage_design="default",
                enable_news=True,
                enable_videos=True,
                enable_gallery=True,
                enable_albums=True,
                enable_premium=True,
                enable_about=True,
            )
            db.session.add(brand)
            print("  + Created brand identity")
        else:
            print("  ~ Brand identity already exists")

        # ── Social Media Links ───────────────────────────────────────────
        if SocialMedia.query.count() == 0:
            socials = [
                SocialMedia(name="GitHub", url="https://github.com/1999AZZAR/lilyopencms"),
                SocialMedia(name="Twitter", url="https://twitter.com/lilyopencms"),
            ]
            for s in socials:
                db.session.add(s)
            print(f"  + Created {len(socials)} social media links")
        else:
            print("  ~ Social media already exists")

        # ── Contact Details ──────────────────────────────────────────────
        if ContactDetail.query.count() == 0:
            contacts = [
                ContactDetail(title="Email", content="admin@lilyopencms.local", icon_class="envelope", link="mailto:admin@lilyopencms.local", section_order=1),
                ContactDetail(title="Website", content="lilyopencms.local", icon_class="globe", link="https://lilyopencms.local", section_order=2),
            ]
            for c in contacts:
                db.session.add(c)
            print(f"  + Created {len(contacts)} contact details")
        else:
            print("  ~ Contact details already exists")

        # ── Navigation Links ─────────────────────────────────────────────
        if NavigationLink.query.count() == 0:
            navs = [
                NavigationLink(name="Utama", url="/", location="navbar", order=1),
                NavigationLink(name="Berita", url="/news", location="navbar", order=2),
                NavigationLink(name="Artikel", url="/articles", location="navbar", order=3),
                NavigationLink(name="Tentang", url="/about", location="navbar", order=4),
            ]
            for n in navs:
                db.session.add(n)
            print(f"  + Created {len(navs)} navigation links")
        else:
            print("  ~ Navigation links already exists")

        # ── Permissions ──────────────────────────────────────────────────
        if Permission.query.count() == 0:
            perms = [
                ("news:read", "Read news", "news", "read"),
                ("news:create", "Create news", "news", "create"),
                ("news:update", "Update news", "news", "update"),
                ("news:delete", "Delete news", "news", "delete"),
                ("news:publish", "Publish news", "news", "publish"),
                ("users:read", "Read users", "users", "read"),
                ("users:update", "Update users", "users", "update"),
                ("users:delete", "Delete users", "users", "delete"),
                ("users:suspend", "Suspend users", "users", "suspend"),
                ("roles:read", "Read roles", "roles", "read"),
                ("roles:create", "Create roles", "roles", "create"),
                ("roles:update", "Update roles", "roles", "update"),
                ("roles:delete", "Delete roles", "roles", "delete"),
                ("permissions:read", "Read permissions", "permissions", "read"),
                ("permissions:create", "Create permissions", "permissions", "create"),
                ("permissions:update", "Update permissions", "permissions", "update"),
                ("permissions:delete", "Delete permissions", "permissions", "delete"),
                ("settings:read", "Read settings", "settings", "read"),
                ("settings:update", "Update settings", "settings", "update"),
                ("analytics:read", "Read analytics", "analytics", "read"),
                ("analytics:export", "Export analytics", "analytics", "export"),
            ]
            for name, desc, resource, action in perms:
                p = Permission(name=name, description=desc, resource=resource, action=action)
                db.session.add(p)
            print(f"  + Created {len(perms)} permissions")
        else:
            print("  ~ Permissions already exists")

        # ── Custom Roles ─────────────────────────────────────────────────
        if CustomRole.query.count() == 0:
            editor = CustomRole(name="Editor", description="Can manage and publish content", is_active=True)
            writer = CustomRole(name="Writer", description="Can create content", is_active=True)
            db.session.add_all([editor, writer])
            db.session.flush()

            # Assign permissions to Editor
            editor_perms = Permission.query.filter(
                Permission.resource.in_(["news", "images", "videos"]),
            ).all()
            editor.permissions = editor_perms

            # Assign permissions to Writer
            writer_perms = Permission.query.filter(
                Permission.name.in_(["news:read", "news:create", "news:update"]),
            ).all()
            writer.permissions = writer_perms

            print("  + Created custom roles: Editor, Writer")
        else:
            print("  ~ Custom roles already exists")

        db.session.commit()
        print("\nSeed complete!")


if __name__ == "__main__":
    seed()
