import praw

from images_of import settings

class Reddit(praw.Reddit):
    def oauth(self, **kwargs):
        self.set_oauth_app_info(
            client_id = kwargs.get('client_id') or settings.CLIENT_ID,
            client_secret = kwargs.get('client_secret') or settings.CLIENT_SECRET,
            redirect_uri = kwargs.get('redirect_uri') or settings.REDIRECT_URI
        )

        self.refresh_access_information(
                kwargs.get('refresh_token') or settings.REFRESH_TOKEN
        )

    def login(self, username=None, password=None):
        # this is depricated, just ignore the warning.
        super().login(
                username or settings.USERNAME,
                password or settings.PASSWORD,
                disable_warning=True
        )
