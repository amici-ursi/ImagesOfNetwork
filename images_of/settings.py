"""
images_of settings module.

Anything that's not secret should probably go in here, as it will be common
to all clients. Anything that is, or needs to be tested elsewhere should be
set in local_settings.
"""
import logging
logging.getLogger().setLevel(logging.WARNING)

# Reddit Auth Info

USERNAME = 'username'
PASSWORD = 'password'

CLIENT_ID = 'clientid'
CLIENT_SECRET = 'clientsecret'
REDIRECT_URI = 'http://127.0.0.1:65010/authorize_callback'

# Network Information

NETWORK_NAME = "ImagesOf"
MULTIREDDIT = "ImagesOfPlaces"
MASTER_SUB = "ImagesOfNetwork"

DEFAULT_MODS = ['AutoModerator', 'BotWatchman']
DEFAULT_DESCRIPTION = 'An __ImagesOf__ Network Subreddit'
WIKI_PAGES = ['config/automoderator', 'toolbox']

# Post Checking

EXTENSIONS = [
    r'\.jpg',
    r'\.jpeg',
    r'\.png',
    r'\.gif',
    r'\.gifv',
    r'\.apng',
    r'\.tiff',
    r'\.bmp',
    r'\.xcf',
]

DOMAINS = [
    r'500px\.com',
    r'abload\.de',
    r'cdn\.theatlantic\.com',
    r'.*\.deviantart\.com',
    r'.*\.deviantart\.net',
    r'fav\.me',
    r'.*\.fbcdn\.net',
    r'.*\.files\.wordpress\.com',
    r'flic\.kr',
    r'flickr\.com',
    r'forgifs\.com',
    r'gfycat\.com',
    r'(.*\.)?gifsoup\.com',
    r'(.*\.)?gyazo\.com',
    r'(.*\.)?imageshack\.us',
    r'imgclean\.com',
    r'(i\.)?imgur\.com',
    r'instagr\.am',
    r'instagram\.com',
    r'(cdn\.)?mediacru\.sh',
    r'(.*\.)?media\.tumblr\.com',
    r'(.*\.)?min\.us',
    r'(.*\.)?minus\.com',
    r'(.*\.)?panoramio\.com',
    r'photoburst\.net',
    r'(.*\.)?photoshelter\.com',
    r'pbs\.twimg\.com',
    r'(.*\.)?photobucket\.com',
    r'picsarus\.com',
    r'puu\.sh',
    r'scontent\.cdninstagram\.com',
    r'(.*\.)?staticflickr\.com',
    r'(.*\.)?tinypic\.com',
    r'twitpic\.com',
    r'upload.wikimedia\.org',
    r'i\.reddituploads.com',
]
