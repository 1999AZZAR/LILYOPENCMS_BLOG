"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Auth module models — re-exported from the central models.py.

During the vertical slice migration, models remain in models.py to avoid
circular imports. This file provides a canonical import path for the auth
module. Once all modules are extracted, models will live here permanently.
"""

from models import (  # noqa: F401
    User,
    UserRole,
    Permission,
    CustomRole,
    UserActivity,
    role_permission,
)
