"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

from marshmallow import Schema, fields, validate, EXCLUDE


class RegisterSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        ordered = True

    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))
    email = fields.Email(load_default=None)
    first_name = fields.Str(load_default=None, validate=validate.Length(max=100))
    last_name = fields.Str(load_default=None, validate=validate.Length(max=100))


class LoginSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        ordered = True

    username = fields.Str(required=True)
    password = fields.Str(required=True)


class ChangePasswordSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        ordered = True

    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=6, max=128))


class ForgotPasswordSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        ordered = True

    email = fields.Email(required=True)


class ResetPasswordSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        ordered = True

    token = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=6, max=128))


class UserUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        ordered = True

    email = fields.Email(load_default=None)
    first_name = fields.Str(load_default=None, validate=validate.Length(max=100))
    last_name = fields.Str(load_default=None, validate=validate.Length(max=100))
    bio = fields.Str(load_default=None)
    profile_picture = fields.Str(load_default=None, validate=validate.Length(max=255))
    is_active = fields.Bool(load_default=None)
    is_suspended = fields.Bool(load_default=None)
    suspension_reason = fields.Str(load_default=None)
    role = fields.Str(load_default=None)


class PermissionSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        ordered = True

    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(load_default=None, validate=validate.Length(max=255))
    resource = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    action = fields.Str(required=True, validate=validate.Length(min=1, max=50))


class CustomRoleSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        ordered = True

    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(load_default=None, validate=validate.Length(max=255))
    is_active = fields.Bool(load_default=True)
    permission_ids = fields.List(fields.Int(), load_default=None)
