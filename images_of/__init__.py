# that's all of em. I'm sure we can trim it down a bit
OAUTH_SCOPE = [
        'account',
        'creddits',
        'edit',
        'flair',
        'history',
        'identity',
        'livemanage',
        'modconfig',
        'modcontributors',
        'modflair',
        'modlog',
        'modothers',
        'modposts',
        'modself',
        'modwiki',
        'mysubreddits',
        'privatemessages',
        'read',
        'report',
        'save',
        'submit',
        'subscribe',
        'vote',
        'wikiedit',
        'wikiread',
]

try:
    from . import local_settings as settings
except ImportError:
    from . import settings

from .connect import Reddit
