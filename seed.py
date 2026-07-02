#!/usr/bin/env python3
"""
Seed script — run on first startup to create superuser + permissions.
Minimal seed: only creates the superuser account and RBAC foundation.

Usage:
    python seed.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import (
    db, User, UserRole, BrandIdentity,
    Permission, CustomRole,
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

        # ── Brand Identity (minimal defaults) ────────────────────────────
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

        db.session.commit()
        print("\nSeed complete!")


if __name__ == "__main__":
    seed()
