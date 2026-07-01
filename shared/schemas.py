"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

from marshmallow import Schema, fields, validate, EXCLUDE


class BaseSchema(Schema):
    """Base schema with common configuration."""
    class Meta:
        unknown = EXCLUDE
        ordered = True


class PaginationQuerySchema(BaseSchema):
    """Common pagination query parameters."""
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(load_default=20, validate=validate.Range(min=1, max=100))


class NewsCreateSchema(BaseSchema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    content = fields.Str(required=True, validate=validate.Length(min=1))
    tagar = fields.Str(load_default=None, validate=validate.Length(max=255))
    category_id = fields.Int(required=True)
    is_visible = fields.Bool(load_default=True)
    is_main_news = fields.Bool(load_default=False)
    is_news = fields.Bool(load_default=False)
    is_premium = fields.Bool(load_default=False)
    writer = fields.Str(load_default=None, validate=validate.Length(max=100))
    external_source = fields.Str(load_default=None, validate=validate.Length(max=255))
    image_id = fields.Int(load_default=None)
    # SEO fields
    meta_description = fields.Str(load_default=None, validate=validate.Length(max=500))
    meta_keywords = fields.Str(load_default=None, validate=validate.Length(max=500))
    og_title = fields.Str(load_default=None, validate=validate.Length(max=200))
    og_description = fields.Str(load_default=None, validate=validate.Length(max=500))
    og_image = fields.Str(load_default=None, validate=validate.Length(max=255))
    canonical_url = fields.Str(load_default=None, validate=validate.Length(max=255))
    seo_slug = fields.Str(load_default=None, validate=validate.Length(max=255))


class NewsUpdateSchema(BaseSchema):
    title = fields.Str(validate=validate.Length(min=1, max=200))
    content = fields.Str(validate=validate.Length(min=1))
    tagar = fields.Str(load_default=None, validate=validate.Length(max=255))
    category_id = fields.Int()
    is_visible = fields.Bool()
    is_main_news = fields.Bool()
    is_news = fields.Bool()
    is_premium = fields.Bool()
    is_archived = fields.Bool()
    writer = fields.Str(load_default=None, validate=validate.Length(max=100))
    image_id = fields.Int(load_default=None)
    meta_description = fields.Str(load_default=None, validate=validate.Length(max=500))
    meta_keywords = fields.Str(load_default=None, validate=validate.Length(max=500))
    og_title = fields.Str(load_default=None, validate=validate.Length(max=200))
    og_description = fields.Str(load_default=None, validate=validate.Length(max=500))
    og_image = fields.Str(load_default=None, validate=validate.Length(max=255))


class CategorySchema(BaseSchema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))


class AlbumCreateSchema(BaseSchema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(load_default=None)
    category_id = fields.Int(required=True)
    cover_image_id = fields.Int(load_default=None)
    is_visible = fields.Bool(load_default=True)
    is_premium = fields.Bool(load_default=False)


class UserUpdateSchema(BaseSchema):
    email = fields.Email(load_default=None)
    first_name = fields.Str(load_default=None, validate=validate.Length(max=100))
    last_name = fields.Str(load_default=None, validate=validate.Length(max=100))
    bio = fields.Str(load_default=None)
    is_active = fields.Bool()
    is_suspended = fields.Bool()
    suspension_reason = fields.Str(load_default=None)
