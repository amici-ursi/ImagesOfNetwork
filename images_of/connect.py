import praw

from images_of import settings

class Reddit(praw.Reddit):
    def oauth(self, **kwargs):
        new_kwargs = {
            'client_id': settings.CLIENT_ID,
            'client_secret': settings.CLIENT_SECRET,
            'redirect_uri': settings.REDIRECT_URI,
        }

        new_kwargs.update(kwargs)
        super().set_oauth_app_info(**new_kwargs)

    def login(self, username=None, password=None):
        # this is depricated, just ignore the warning.
        super().login(
                username or settings.USERNAME,
                password or settings.PASSWORD,
                disable_warning=True
        )
