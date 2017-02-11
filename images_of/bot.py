import logging
import re
from collections import deque
from datetime import datetime
from time import sleep

import requests
from praw.helpers import submission_stream
from praw.errors import AlreadySubmitted, APIException, HTTPException

from images_of import settings, AcceptFlag
from images_of.subreddit import Subreddit

RETRY_MINUTES = 2
LOG = logging.getLogger(__name__)


class Bot:
    def __init__(self, r, should_post=True):
        self.r = r
        self.should_post = should_post
        self.recent_posts = deque(maxlen=50)

        LOG.info('Loading global user blacklist from wiki')
        self.blacklist_users = self._read_blacklist('userblacklist')

        LOG.info('Loading global subreddit blacklist from wiki')
        blacklist_sub_pats = self._read_blacklist('subredditblacklist')
        self.blacklist_sub_res = [re.compile(pat) for pat
                                  in blacklist_sub_pats]

        self.subreddits = []
        for sub_settings in settings.CHILD_SUBS:
            self._load_sub(sub_settings)
        for sub_settings in settings.COUSIN_SUBS:
            self._load_sub(sub_settings)

        ext_pattern = '({})$'.format('|'.join(settings.EXTENSIONS))
        self.ext_re = re.compile(ext_pattern, flags=re.IGNORECASE)

        domain_pattern = '^({})$'.format('|'.join(settings.DOMAINS))
        self.domain_re = re.compile(domain_pattern, flags=re.IGNORECASE)

    def _load_sub(self, settings):
        sub = Subreddit(**settings)
        sub.load_wiki_blacklist(self.r)
        self.subreddits.append(sub)

    def _read_blacklist(self, wiki_page):
        content = self.r.get_wiki_page(
            settings.PARENT_SUB, wiki_page).content_md
        entries = [line.strip().lower()[3:] for line
                   in content.splitlines() if line]
        return set(entries)

    def check(self, post):
        """
        Check global conditions on a post. Returns an `AcceptFlag` indicating
        if the post should be accepted, denied, or the conditions under which
        a subreddit may accept it.
        """

        ok_ret = AcceptFlag.OK
        if post.over_18:
            if not settings.NSFW_OK and settings.NSFW_WHITELIST_OK:
                ok_ret = AcceptFlag.OK_IF_WHITELISTED
            elif not settings.NSFW_OK:
                return AcceptFlag.BAD

        # sometimes, we fail to load up the author information, in which case
        # 'author' comes up as None.
        try:
            user = post.author.name.lower()
        except AttributeError:
            LOG.warning('No author information available for submission %s.',
                        post.url)
            return AcceptFlag.BAD

        if user in self.blacklist_users:
            return AcceptFlag.BAD

        sub = post.subreddit.display_name.lower()
        if any(bl_sub.fullmatch(sub) for bl_sub in self.blacklist_sub_res):
            return AcceptFlag.BAD

        if self.domain_re.search(post.domain):
            return ok_ret

        if self.ext_re.search(post.url):
            return ok_ret

        return AcceptFlag.BAD

    def crosspost(self, post, sub, match):
        title = post.title
        comment = '[Original post]({}) by /u/{} in /r/{}\n{}'.format(
            post.permalink,
            post.author,
            post.subreddit,
            settings.COMMENT_FOOTER.format(
                reason=match.reason,
                detail=match.detail
            )
        )

        log_entry = (post.url, sub.name)
        if log_entry in self.recent_posts:
            # put it back at the end of the queue
            self.recent_posts.remove(log_entry)
            self.recent_posts.append(log_entry)
            LOG.info('Already posted {} to /r/{}. Skipping.'.format(title,
                                                                    sub.name))
            return
        else:
            self.recent_posts.append(log_entry)
            LOG.debug(
                'Added {} to recent posts. Now tracking {} items.'.format(
                    log_entry, len(self.recent_posts))
            )
        try:
            LOG.info('X-Posting into /r/{}: {}'.format(sub.name, title))
            if self.should_post:
                xpost = self.r.submit(
                    sub.name,
                    title,
                    url=post.url,
                    captcha=None,
                    send_replies=True,
                    resubmit=False
                )
            if post.over_18:
                LOG.info('Marking NSFW')
                if self.should_post:
                    xpost.mark_as_nsfw()

            LOG.debug('Commenting: {}'.format(comment))
            if self.should_post:
                xpost.add_comment(comment)

        except AlreadySubmitted:
            LOG.info('Already submitted. Skipping.')
        except KeyError:
            # XXX AlreadySubmitted isn't being raised for some reason
            LOG.info('Already Submitted (KeyError). Skipping.')
        except APIException as e:
            LOG.warning(e)

    def verify_age(self, post):
        if hasattr(post, 'age_verified'):
            return True

        created = datetime.utcfromtimestamp(post.author.created_utc)
        age = (datetime.utcnow() - created).days
        if age > 7:
            post.age_verified = True
            return True
        return False

    def _do_post(self, post):
        flag = self.check(post)
        if flag is AcceptFlag.BAD:
            return

        for sub in self.subreddits:
            match = sub.check(post, flag)
            if match:
                if not self.verify_age(post):
                    return
                self.crosspost(post, sub, match)

    def run(self):
        while True:
            stream = submission_stream(self.r, 'all', verbosity=0)

            try:
                for post in stream:
                    self._do_post(post)
            except (HTTPException, requests.ReadTimeout,
                    requests.ConnectionError) as e:
                LOG.error('{}: {}'.format(type(e), e))
            else:
                LOG.error('Stream ended.')

            LOG.info('Sleeping for {} minutes.'.format(RETRY_MINUTES))
            sleep(60 * RETRY_MINUTES)
