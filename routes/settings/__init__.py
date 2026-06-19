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

# This ensures all routes are registered when the settings module is imported