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

DEFAULT_MODS = ['Automoderator', 'BotWatchman']

MASTER_SUB = "ImagesOfNetwork"
