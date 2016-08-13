import re
import logging

from praw.errors import Forbidden

from images_of import AcceptFlag

LOG = logging.getLogger(__name__)


class Match:
    def __init__(self, reason, detail):
        self.reason = reason
        self.detail = detail


class Subreddit:
    def __init__(self, name, search, feeds=[], ignore=None,
                 ignore_case=None, whitelist=[], blacklist=[],
                 wiki_blacklist=False, feed_limit=None, **kwargs):
        """
        Create new Subreddit object. This object is responsible for
        checking if posts meet sub-specific criteria for whether or
        not a post belongs.

        :param name: Subreddit name
        :param feeds: Atom feeds of content to be posted
        :param search: terms or regexes to be searched
        :param ignore: terms or regexes to ignore
        :param whitelist: list of subreddits to always accept
        :param blacklist: list of subreddits to never accept
        :param wiki_blacklist: subreddit has a blacklist on it's wiki
        """

        LOG.debug('Setting up /r/{}'.format(name))

        def make_regex(x, flags=0):
            if x is None:
                return None
            if isinstance(x, str):
                x = [x]

            terms = '(\\b{}\\b)'.format('\\b|\\b'.join(x))
            return re.compile(terms, flags)

        self.name = name
        self.feeds = feeds
        self.search_re = make_regex(search, re.IGNORECASE)
        self.ignore_re = make_regex(ignore, re.IGNORECASE)
        self.ignore_case_re = make_regex(ignore_case)
        self.whitelist = [sub.lower() for sub in whitelist]
        blacklist_pats = [sub.lower() for sub in blacklist]
        self.blacklist_res = set([re.compile(pat) for pat in blacklist_pats])
        self.wiki_blacklist = wiki_blacklist
        self.feed_limit = feed_limit

        if kwargs:
            bad_keys = list(kwargs.keys())
            LOG.warning('Unrecognized subreddit settings: {}'.format(bad_keys))

    def load_wiki_blacklist(self, r):
        """
        Load blacklist from subreddit wiki.

        The subreddit may know that it needs to fetch pages externally,
        but is only a container for settings, and cannot fetch the
        contents of a wiki page by itself. Provided with a Reddit instance,
        it can go out and update it's blacklist.

        The wiki page 'subredditblacklist' should be a list of users,
        one per line, including the /u/ portion of the username.

        :param r: A praw.Reddit object.
        """
        if not self.wiki_blacklist or hasattr(self, 'wiki_blacklist_loaded'):
            return

        try:
            LOG.info('Loading wiki blacklist for /r/{}'.format(self.name))
            content = r.get_wiki_page(
                self.name, 'subredditblacklist').content_md
            wiki_blacklist = set(re.compile(sub.strip().lower()[3:]) for
                                 sub in content.splitlines() if sub)
        except Forbidden:
            LOG.warning(
                'Forbidden from reading blacklist on /r/{}'.format(self.name))
            wiki_blacklist = set()

        self.blacklist_res = self.blacklist_res.union(wiki_blacklist)
        self.wiki_blacklist_loaded = True

    def check(self, post, flag=AcceptFlag.OK):
        """See if post is appropriate for this subreddit"""

        if flag is AcceptFlag.BAD:
            return

        title = post.title
        post_sub = post.subreddit.display_name.lower()

        if post_sub in self.whitelist:
            return Match('whitelist', post_sub)
        if flag is AcceptFlag.OK_IF_WHITELISTED:
            return
        if any(bl_sub.fullmatch(post_sub) for bl_sub in self.blacklist_res):
            return

        if self.ignore_case_re and self.ignore_case_re.search(title):
            return
        if self.ignore_re and self.ignore_re.search(title):
            return

        match = self.search_re.search(title)
        if match:
            return Match('match', match.group())

        return
