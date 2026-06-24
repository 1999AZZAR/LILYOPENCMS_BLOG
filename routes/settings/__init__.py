"""
Copyright (c) 2026 Azzar Budiyanto / LilyOpenCMS.
All rights reserved.

This software is dual-licensed:
1. For open-source use: Licensed under the GNU General Public License v3.0 (GPL-3.0).
2. For commercial use: Subject to a separate Commercial License Agreement.

Contact: azzar.mr.zs@gmail.com for inquiries.
"""

"""
Settings Routes Module

This module contains all settings-related routes organized into logical sub-modules.
Each sub-module handles a specific area of settings functionality.
"""

# Import all settings route modules to ensure they're registered with the blueprint
from . import account
from . import dashboard
from . import performance
from . import content
from . import policies
from . import contact
from . import media
from . import brand
from . import seo
from . import api
from . import root_seo

# This ensures all routes are registered when the settings module is imported
