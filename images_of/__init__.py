try:
    from . import local_settings as settings
except ImportError:
    from . import settings

from .connect import Reddit
