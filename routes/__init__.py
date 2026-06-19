from .common_imports import *
main_blueprint = Blueprint("main", __name__)

from .routes_auth import *
from .routes_chategories import *
from .routes_helper import *
from .routes_images import *
from .routes_infos import *
from .routes_news import *
from .routes_public import *
from .settings import *
from .routes_socialmedia import *
from .routes_subscriptions import *
from .routes_users import *
from .routes_roles import *
from .routes_analytics import *
from .routes_video import *
from .routes_albums import *

__all__ = [
    "main_blueprint",
    "routes_auth",
    "routes_chategories",
    "routes_helper",
    "routes_images",
    "routes_infos",
    "routes_news",
    "routes_public",
    "settings",
    "routes_socialmedia",
    "routes_users",
    "routes_roles",
    "routes_analytics",
    "routes_video",
    "routes_albums",
]