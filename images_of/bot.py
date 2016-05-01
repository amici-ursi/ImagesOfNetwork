import re
import datetime

from praw.helpers import submission_stream
from praw.errors import AlreadySubmitted, APIException

class Bot:
    def __init__(self, r):
        self.r = r

        self.blacklist_users = self._read_blacklist('userblacklist')
        self.blacklist_subs = self._read_blacklist('subredditblacklist')

        self.subreddits = []
        for sub_settings in settings.SLAVE_SUBS:
            sub = Subreddit(**slave_settings)
            self.subreddits.append(sub)

        ext_pattern = '({})$'.format('|'.join(settings.EXTENSIONS))
        self.ext_re = re.compile(ext_pattern, flags=re.IGNORECASE)

        domain_pattern = '^({})$'.format('|'.join(settings.DOMAINS))
        self.domain_re = re.compile(domain_pattern, flags=re.IGNORECASE)

    def _read_blacklist(self, wiki_page):
        content = r.get_wiki_page(settings.MASTER_SUB, wiki_page).content_md
        entries = [line.srip().lower()[3:] for line in content.splitlines() if line]
        return set(entries)

    def check(self, post):
        """Check global conditions on a post"""
        if post.over_18:
            return False

        user = post.author.name.lower()
        if user in self.blacklist_users:
            return False

        sub = post.subreddit.display_name.lower()
        if sub in self.blacklist_subs:
            return False

        if self.domain_re.search(post.domain):
            return True

        if self.ext_re.search(post.url):
            return True

        return False


    def crosspost(self, post, sub):
        title = post.title
        comment = '[Original post]({}) by /u/{} in /r/{}'.format(
                post.permalink,
                post.author,
                post.subreddit)

        logging.info('X-Posting into /r/{}: {}'.format(sub.name, title))
        try:
            xpost = r.submit(
                        sub.name
                        url=post.url,
                        captcha=None,
                        send_replies=True,
                        resubmit=False)
            xpost.add_comment(comment)
        except AlreadySubmitted:
            logging.info('Already submitted. Skipping.')
        except APIException as e:
            logging.warning(e)
        
    def check_age(self, post):
        created = datetime.utcfromtimestamp(post.author.created_utc)
        age = (datetime.utcnow() - created).days
        return age > 2

    def run(self):
        stream = submission_stream(self.r, 'all')
        for post in stream:
            if not self.check(post):
                continue

            age_ok = None
            for sub in self.subreddits
                if sub.check(post):
                    if age_ok is None:
                        age_ok = self.check_age()
                    
                    if not age_ok:
                        break

                    self.crosspost(post, sub)
