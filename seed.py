#!/usr/bin/env python3
"""
Seed script — run on first startup to create users + permissions.
Creates one user per role (superuser, admin, general) + RBAC foundation.

Usage:
    python seed.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import (
    db, User, UserRole, BrandIdentity,
    Permission, CustomRole, Page,
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
                verified=True,
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
                verified=True,
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
                verified=True,
                first_name="Test",
                last_name="User",
            )
            u.set_password("user123")
            db.session.add(u)
            print("  + Created user: user / user123")
        else:
            print("  ~ User already exists")

        # ── Brand Identity (minimal defaults) ────────────────────────────
        if not BrandIdentity.query.first():
            brand = BrandIdentity(
                brand_name="LilyOpenCMS",
                tagline="Modern content management for the digital age",
                homepage_design="news",
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

            editor_perms = Permission.query.filter(
                Permission.resource.in_(["news", "images", "videos"]),
            ).all()
            editor.permissions = editor_perms

            writer_perms = Permission.query.filter(
                Permission.name.in_(["news:read", "news:create", "news:update"]),
            ).all()
            writer.permissions = writer_perms

            print("  + Created custom roles: Editor, Writer")
        else:
            print("  ~ Custom roles already exists")

        # ── Default Pages ────────────────────────────────────────────────
        if Page.query.count() == 0:
            admin = User.query.filter_by(username="admin").first()
            default_pages = [
                {
                    "title": "Tentang Kami",
                    "slug": "tentang-kami",
                    "content": "<h2>Tentang LilyOpenCMS</h2><p>LilyOpenCMS adalah sistem manajemen konten modern yang dirancang untuk berbagai kebutuhan — dari blog pribadi hingga portal berita dan perusahaan.</p><p>Dibangun dengan Flask dan PostgreSQL, LilyOpenCMS menawarkan fleksibilitas, keamanan, dan performa tinggi.</p>",
                    "excerpt": "Pelajari lebih lanjut tentang LilyOpenCMS",
                    "template": "default",
                    "is_published": True,
                    "show_in_menu": True,
                    "menu_order": 1,
                    "meta_title": "Tentang Kami — LilyOpenCMS",
                    "meta_description": "Pelajari lebih lanjut tentang LilyOpenCMS, sistem manajemen konten modern.",
                    "author_id": admin.id if admin else None,
                },
                {
                    "title": "Kebijakan Privasi",
                    "slug": "kebijakan-privasi",
                    "content": "<h2>Kebijakan Privasi</h2><p>Kami menghargai privasi Anda. Halaman ini menjelaskan bagaimana kami mengumpulkan, menggunakan, dan melindungi data pribadi Anda.</p><h3>Data yang Dikumpulkan</h3><p>Kami mengumpulkan data seperti nama, alamat email, dan konten yang Anda posting.</p><h3>Penggunaan Data</h3><p>Data digunakan untuk menyediakan dan meningkatkan layanan kami.</p>",
                    "excerpt": "Kebijakan privasi LilyOpenCMS",
                    "template": "default",
                    "is_published": True,
                    "show_in_menu": True,
                    "menu_order": 2,
                    "meta_title": "Kebijakan Privasi — LilyOpenCMS",
                    "meta_description": "Kebijakan privasi LilyOpenCMS.",
                    "author_id": admin.id if admin else None,
                },
                {
                    "title": "Syarat & Ketentuan",
                    "slug": "syarat-ketentuan",
                    "content": "<h2>Syarat & Ketentuan</h2><p>Dengan menggunakan LilyOpenCMS, Anda menyetujui syarat dan ketentuan berikut.</p>",
                    "excerpt": "Syarat dan ketentuan penggunaan LilyOpenCMS",
                    "template": "default",
                    "is_published": True,
                    "show_in_menu": True,
                    "menu_order": 3,
                    "meta_title": "Syarat & Ketentuan — LilyOpenCMS",
                    "meta_description": "Syarat dan ketentuan penggunaan LilyOpenCMS.",
                    "author_id": admin.id if admin else None,
                },
                {
                    "title": "Layanan",
                    "slug": "layanan",
                    "content": "<h2>Layanan Kami</h2><p>Kami menyediakan berbagai layanan manajemen konten untuk memenuhi kebutuhan Anda.</p><ul><li>Blog Pribadi</li><li>Portal Berita</li><li>Profil Perusahaan</li><li>Toko Online</li></ul>",
                    "excerpt": "Layanan yang ditawarkan oleh LilyOpenCMS",
                    "template": "default",
                    "is_published": True,
                    "show_in_menu": True,
                    "menu_order": 4,
                    "meta_title": "Layanan — LilyOpenCMS",
                    "meta_description": "Layanan manajemen konten LilyOpenCMS.",
                    "author_id": admin.id if admin else None,
                },
            ]
            for page_data in default_pages:
                page = Page(**page_data)
                db.session.add(page)
            print(f"  + Created {len(default_pages)} default pages")
        else:
            print("  ~ Default pages already exist")

        db.session.commit()
        print("\nSeed complete!")


if __name__ == "__main__":
    seed()
