import logging

import feedparser
from praw.errors import AlreadySubmitted, APIException, HTTPException

from images_of import command, settings, Reddit
from images_of.subreddit import Subreddit


LOG = logging.getLogger(__name__)


@command
def main():
    r = Reddit('posts relevant feeds to the {} - /u/{}'.format(
        settings.NETWORK_NAME,
        settings.USERNAME))
    r.oauth()

    for child_settings in settings.CHILD_SUBS:
        sub = Subreddit(**child_settings)
        for feed in sub.feeds:
            thisfeed = feedparser.parse(feed)
            comment = 'This content brought to you from "{}"\n{}'.format(
                    thisfeed.feed.title,
                    settings.COMMENT_FOOTER.format(
                        reason='off site feed',
                        detail=thisfeed.feed.title
                    ))
            for item in thisfeed.entries:
                LOG.info('Posting OC into /r/{}: {}'.format(
                    sub.name,
                    item.title))
                try:
                    xpost = r.submit(
                        sub.name,
                        title=item.title,
                        url=item.link,
                        captcha=None,
                        send_replies=True,
                        resubmit=False)
                    xpost.add_comment(comment)
                except AlreadySubmitted:
                    LOG.info('Already submitted. Skipping.')
                except KeyError:
                    # XXX AlreadySubmitted isn't being raised for some reason
                    LOG.info('Already Submitted (KeyError). Skipping.')
                except APIException as e:
                    LOG.warning(e)

if __name__ == '__main__':
    main()