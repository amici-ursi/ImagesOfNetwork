import praw
from images_of import settings


class Reddit(praw.Reddit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config.api_request_delay = 1.0

    def oauth(self, **kwargs):
        self.set_oauth_app_info(
            client_id=kwargs.get('client_id') or settings.CLIENT_ID,
            client_secret=(kwargs.get('client_secret') or
                           settings.CLIENT_SECRET),
            redirect_uri=kwargs.get('redirect_uri') or settings.REDIRECT_URI
        )

        self.refresh_access_information(
            kwargs.get('refresh_token') or settings.REFRESH_TOKEN
        )

    def login(self, username=None, password=None):
        # this is depricated, just ignore the warning.
        self.config.api_request_delay = 2.0
        super().login(
            username or settings.USERNAME,
            password or settings.PASSWORD,
            disable_warning=True
        )
