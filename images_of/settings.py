"""
images_of settings module.

Anything that's not secret should probably go in here, as it will be common
to all clients. Anything that is, or needs to be tested elsewhere should be
set in local_settings.
"""
import os.path
import pytoml as toml
import pkg_resources


def _conf_get(conf, *args, default=None):
    try:
        cur = conf
        for arg in args:
            cur = cur[arg]
        return cur
    except KeyError:
        return default


class Settings:
    def __init__(self):
        conf = pkg_resources.resource_string(__name__, 'data/settings.toml')
        self.loads(conf)

        self._try_load(os.path.expanduser('~/.config/ion/settings.toml'))
        self._try_load('ion.toml')

    def _try_load(self, fname):
        try:
            self.load(fname)
        except FileNotFoundError:
            pass

    def load(self, fname):
        with open(fname, 'r') as f:
            raw = f.read()
        self.loads(raw)

    def loads(self, raw):
        conf = toml.loads(raw)

        # reddit
        self.USERNAME = _conf_get(conf, 'auth',
                                  'username', default=self.USERNAME)
        self.PASSWORD = _conf_get(conf, 'auth',
                                  'password', default=self.PASSWORD)

        self.CLIENT_ID = _conf_get(
            conf, 'auth', 'client-id', default=self.CLIENT_ID)
        self.CLIENT_SECRET = _conf_get(
            conf, 'auth', 'client-secret', default=self.CLIENT_SECRET)
        self.REDIRECT_URI = _conf_get(
            conf, 'auth', 'redirect-uri', default=self.REDIRECT_URI)
        self.REFRESH_TOKEN = _conf_get(
            conf, 'auth', 'refresh-token', default=self.REFRESH_TOKEN)

        # network
        self.NETWORK_NAME = _conf_get(conf, 'network',
                                      'name', default=self.NETWORK_NAME)

        multi_user = _conf_get(conf, 'network', 'multireddit-user')
        if multi_user is not None:
            self.MULTIREDDIT_USER = multi_user
            self._multi_user_set = True
        elif not hasattr(self, '_multi_user_set'):
            self.MULTIREDDIT_USER = _conf_get(
                conf, 'auth', 'username', default=self.USERNAME)

        self.MULTIREDDITS = _conf_get(
            conf, 'network', 'multireddits', default=self.MULTIREDDITS)

        self.DEFAULT_MODS = _conf_get(conf, 'network',
                                      'mods', default=self.DEFAULT_MODS)
        self.WIKI_PAGES = _conf_get(conf, 'network',
                                    'wiki-pages', default=self.WIKI_PAGES)
        self.NSFW_OK = _conf_get(conf, 'network', 'nsfw', default=self.NSFW_OK)
        self.NSFW_WHITELIST_OK = _conf_get(conf, 'network', 'nsfw-whitelist',
                                           default=self.NSFW_WHITELIST_OK)
        self.COMMENT_FOOTER = _conf_get(conf, 'network', 'comment-footer',
                                        default=self.COMMENT_FOOTER)
        self.DOMAINS = _conf_get(conf, 'posts',
                                 'domains', default=self.DOMAINS)
        self.EXTENSIONS = _conf_get(conf, 'posts',
                                    'extensions', default=self.EXTENSIONS)

        self.PARENT_SUB = _conf_get(conf, 'parent',
                                    'name', default=self.PARENT_SUB)

        update_children = _conf_get(conf, 'update_children', default=False)
        self.CHILD_SUBS = self._load_group(conf, 'child',
                                           self.CHILD_SUBS, update_children)

        update_cousins = _conf_get(conf, 'update_cousins', default=False)
        self.COUSIN_SUBS = self._load_group(conf, 'cousin',
                                            self.COUSIN_SUBS, update_cousins)

        # discord
        self.DISCORD_CLIENTID = _conf_get(conf, 'discord', 'client_id',
                                          default=self.DISCORD_CLIENTID)
        self.DISCORD_TOKEN = _conf_get(conf, 'discord',
                                       'token', default=self.DISCORD_TOKEN)

        self.DISCORD_INBOX_CHAN_ID = _conf_get(
            conf, 'discord', 'inbox_channel',
            default=self.DISCORD_INBOX_CHAN_ID
        )
        self.DISCORD_FALSEPOS_CHAN_ID = _conf_get(
            conf, 'discord', 'falsepos_channel',
            default=self.DISCORD_FALSEPOS_CHAN_ID
        )
        self.DISCORD_OC_CHAN_ID = _conf_get(
            conf, 'discord', 'oc_channel',
            default=self.DISCORD_OC_CHAN_ID
        )
        self.DISCORD_MOD_CHAN_ID = _conf_get(
            conf, 'discord', 'mod_channel',
            default=self.DISCORD_MOD_CHAN_ID
        )
        self.DISCORD_KEEPALIVE_CHAN_ID = _conf_get(
            conf, 'discord', 'keepalive_channel',
            default=self.DISCORD_KEEPALIVE_CHAN_ID
        )

    def _load_group(self, conf, group, old_items, update=False):
        # update indicates that we should update the group rather
        # than overwrite it. This is useful for configurations
        # outside the default that want to add subs instead of
        # replace our defaults.

        items = _conf_get(conf, group, default={})
        if not items:
            return old_items

        fixed_items = {}
        for name, vals in items.items():
            fixed_items[name] = {}
            for k, v in vals.items():
                nk = k.replace('-', '_')
                fixed_items[name][nk] = items[name][k]
        items = fixed_items

        if update:
            old_items = {sub['name']: sub for sub in old_items}
            for s in old_items:
                del s['name']
            old_items.update(items)
            items = old_items

        new_items = []
        for k, v in items.items():
            v.update({'name': k})
            new_items.append(v)

        return new_items

    USERNAME = ""
    PASSWORD = ""

    CLIENT_ID = ""
    CLIENT_SECRET = ""
    REDIRECT_URI = ""
    REFRESH_TOKEN = ""

    NETWORK_NAME = ""
    MULTIREDDIT_USER = None
    MULTIREDDITS = []

    DEFAULT_MODS = []
    WIKI_PAGES = []
    NSFW_OK = False
    NSFW_WHITELIST_OK = True
    COMMENT_FOOTER = ""

    PARENT_SUB = ""
    CHILD_SUBS = []
    COUSIN_SUBS = []

    EXTENSIONS = []
    DOMAINS = []

    DISCORD_CLIENTID = ""
    DISCORD_TOKEN = ""

    DISCORD_INBOX_CHAN_ID = None
    DISCORD_FALSEPOS_CHAN_ID = None
    DISCORD_OC_CHAN_ID = None
    DISCORD_MOD_CHAN_ID = None
    DISCORD_KEEPALIVE_CHAN_ID = None

settings = Settings()
