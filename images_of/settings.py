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

        self.MASTER_SUB = _conf_get(conf, 'master', 'name', default=self.MASTER_SUB)

        update_slaves = _conf_get(conf, 'update_slaves', default=False)
        slaves = _conf_get(conf, 'slave')
        if slaves is None:
            return

        fixed_slaves = {}
        for name, vals in slaves.items():
            fixed_slaves[name] = {}
            for k, v in vals.items():
                nk = k.replace('-', '_')
                fixed_slaves[name][nk] = slaves[name][k]
        slaves = fixed_slaves

        if update_slaves:
            old_slaves = {sub['name']: sub for sub in self.SLAVE_SUBS}
            for s in old_slaves:
                del s['name']
            old_slaves.update(slaves)
            slaves = old_slaves

        new_slaves = []
        for k, v in slaves.items():
            v.update({'name': k})
            new_slaves.append(v)

        self.SLAVE_SUBS = new_slaves


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

    MASTER_SUB = ""
    SLAVE_SUBS = []

    EXTENSIONS = []
    DOMAINS = []


settings = Settings()

