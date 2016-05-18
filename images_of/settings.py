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

        self.USERNAME = _conf_get(conf, 'auth', 'username', default=self.USERNAME)
        self.PASSWORD = _conf_get(conf, 'auth', 'password', default=self.PASSWORD)
        
        self.CLIENT_ID = _conf_get(conf, 'auth', 'client-id', default=self.CLIENT_ID)
        self.CLIENT_SECRET = _conf_get(conf, 'auth', 'client-secret', default=self.CLIENT_SECRET)
        self.REDIRECT_URI = _conf_get(conf, 'auth', 'redirect-uri', default=self.REDIRECT_URI)
        self.REFRESH_TOKEN = _conf_get(conf, 'auth', 'refresh-token', default=self.REFRESH_TOKEN)

        self.NETWORK_NAME = _conf_get(conf, 'network', 'name', default=self.NETWORK_NAME)
        self.MULTIREDDIT = _conf_get(conf, 'network', 'multireddit', default=self.MULTIREDDIT)

        self.DEFAULT_MODS = _conf_get(conf, 'network', 'mods', default=self.DEFAULT_MODS)
        self.WIKI_PAGES = _conf_get(conf, 'network', 'wiki-pages', default=self.WIKI_PAGES)
        self.NSFW_OK = _conf_get(conf, 'network', 'nsfw', default=self.NSFW_OK)
        self.NSFW_WHITELIST_OK = _conf_get(conf, 'network', 'nsfw-whitelist',
                                           default=self.NSFW_WHITELIST_OK)
        self.COMMENT_FOOTER = _conf_get(conf, 'network', 'comment-footer', default=self.COMMENT_FOOTER)
        self.DOMAINS = _conf_get(conf, 'posts', 'domains', default=self.DOMAINS)
        self.EXTENSIONS = _conf_get(conf, 'posts', 'extensions', default=self.EXTENSIONS)

        self.PARENT_SUB = _conf_get(conf, 'parent', 'name', default=self.PARENT_SUB)

        update_children = _conf_get(conf, 'update_children', default=False)
        children = _conf_get(conf, 'child')
        if children is None:
            return

        fixed_children = {}
        for name, vals in children.items():
            fixed_children[name] = {}
            for k, v in vals.items():
                nk = k.replace('-', '_')
                fixed_children[name][nk] = children[name][k]
        children = fixed_children

        if update_children:
            old_children = {sub['name']: sub for sub in self.CHILD_SUBS}
            for s in old_children:
                del s['name']
            old_children.update(children)
            children = old_children

        new_children = []
        for k, v in children.items():
            v.update({'name': k})
            new_children.append(v)

        self.CHILD_SUBS = new_children


    USERNAME = ""
    PASSWORD = ""

    CLIENT_ID = ""
    CLIENT_SECRET = ""
    REDIRECT_URI = ""
    REFRESH_TOKEN = ""

    NETWORK_NAME = ""
    MULTIREDDIT = ""

    DEFAULT_MODS = []
    WIKI_PAGES = []
    NSFW_OK = False
    NSFW_WHITELIST_OK = True
    COMMENT_FOOTER = ""

    PARENT_SUB = ""
    CHILD_SUBS = []

    EXTENSIONS = []
    DOMAINS = []


settings = Settings()

