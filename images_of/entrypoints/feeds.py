import logging

import feedparser
from praw.errors import AlreadySubmitted, APIException, HTTPException

from images_of import command, settings, Reddit


LOG = logging.getLogger(__name__)


@command
def main():
    r = Reddit('posts relevant feeds to the {} - /u/{}'.format(settings.NETWORK_NAME, settings.USERNAME))
    r.oauth()

    for child in settings.CHILD_SUBS:
        for feed in child.feeds:
            sub = child['name']
            thisfeed = feedparser.parse(feed)

            for item in thisfeed.entries:
                LOG.info('Posting OC into /r/{}: {}'.format(sub, item.title))
                try:
                    r.submit(sub, title=item.title, url=item.link, captcha=None, send_replies=True, resubmit=False)
                except AlreadySubmitted:
                    LOG.info('Already submitted. Skipping.')
                except APIException as e:
                    LOG.warning(e)

if __name__ == '__main__':
    main()
