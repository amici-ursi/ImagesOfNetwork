import os
import logging.config
import pkg_resources
import enum
from functools import wraps

import pytoml as toml
import click

from .settings import settings
from .connect import Reddit  # noqa: F401


__version__ = '0.1.0'


def _setup_logging():
    try:
        with open('logging.toml') as f:
            raw = f.read()
    except FileNotFoundError:
        try:
            with open(os.path.expanduser('~/.config/ion/logging.toml')) as f:
                raw = f.read()
        except FileNotFoundError:
            raw = pkg_resources.resource_string(__name__, 'data/logging.toml')

    conf = toml.loads(raw)
    logging.config.dictConfig(conf)
_setup_logging()


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


@enum.unique
class AcceptFlag(enum.Enum):
    OK = 1
    OK_IF_WHITELISTED = 2
    BAD = 3


def _update_settings(ctx, param, value):
    for p in value:
        settings.load(p)


def command(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        g = click.command()(
            click.option(
                '-c', '--config', help='additional configuration file',
                multiple=True, is_eager=True, expose_value=False,
                callback=_update_settings, type=click.Path(exists=True))(f))
        return g(*args, **kwargs)

    return wrapper
