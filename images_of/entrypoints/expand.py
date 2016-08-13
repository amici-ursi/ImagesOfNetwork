import logging
import re
from textwrap import dedent

import click
from praw.errors import SubredditExists, RateLimitExceeded

from images_of import command, settings, Reddit


DRY_RUN = False
LOG = logging.getLogger(__name__)


def create_sub(r, sub):
    try:
        LOG.info('Attempting to create /r/{}'.format(sub))
        if not DRY_RUN:
            r.create_subreddit(sub, sub)
        LOG.info('Created /r/{}'.format(sub))
    except SubredditExists:
        LOG.warning('/r/{} exists'.format(sub))


def copy_settings(r, sub, topic):
    LOG.info('Copying settings from {}'.format(settings.PARENT_SUB))
    if not DRY_RUN:
        sub_settings = r.get_settings(settings.PARENT_SUB)
    else:
        sub_settings = {'title': settings.NETWORK_NAME}

    LOG.debug('{}'.format(sub_settings))

    sub_settings['title'] = "{} {}".format(sub_settings['title'], topic)
    sub_settings['public_description'] = 'Pictures and images of {}'.format(
        topic)

    LOG.info('Copying settings to /r/{}'.format(sub))

    if DRY_RUN:
        return

    sub_obj = r.get_subreddit(sub)
    try:
        r.set_settings(sub_obj, **sub_settings)
    except RateLimitExceeded:
        # when we change settings on a subreddit,
        # if it's been created within the last 10 minutes,
        # reddit always issues a rate limiting warning
        # informing us about how long we have until we
        # can create a new subreddit, and PRAW interprets
        # this as an error. It's not.
        pass


def invite_mods(r, sub):
    mods = settings.DEFAULT_MODS

    cur_mods = []
    if not DRY_RUN:
        cur_mods = [u.name for u in r.get_moderators(sub)]
    LOG.debug('current mods for /r/{}: {}'.format(sub, cur_mods))

    need_mods = [mod for mod in mods if mod not in cur_mods]
    if not need_mods:
        LOG.info('All mods already invited.')
        return
    else:
        LOG.info('Inviting moderators: {}'.format(need_mods))

    if not DRY_RUN:
        s = r.get_subreddit(sub)
        for mod in need_mods:
            s.add_moderator(mod)

    LOG.info('Mods invited.')


def copy_wiki_pages(r, sub):
    for page in settings.WIKI_PAGES:
        LOG.info('Copying wiki page "{}"'.format(page))
        if not DRY_RUN:
            content = r.get_wiki_page(settings.PARENT_SUB, page).content_md
            r.edit_wiki_page(sub, page, content=content,
                             reason='Subreddit stand-up')


def setup_flair(r, sub):
    # XXX should this be copied from the parent?
    LOG.info('Setting up flair')
    if not DRY_RUN:
        r.configure_flair(sub,
                          flair_enabled=True,
                          flair_position='right',
                          link_flair_enabled=True,
                          link_flair_position='right',
                          flair_self_assign=False)


def add_to_multi(r, sub, multi):
    if not multi:
        LOG.warning("No multireddit to add /r/{} to.".format(sub))
        return

    LOG.info('Adding /r/{} to /user/{}/m/{}'.format(
             sub, settings.MULTIREDDIT_USER, multi))

    if DRY_RUN:
        return

    m = r.get_multireddit(settings.MULTIREDDIT_USER, multi)

    # NOTE: for some reason, at least for this version of PRAW,
    # adding a sub to a multireddit requires us to be logged in.
    r.login()
    m.add_subreddit(sub)


def setup_notifications(r, sub):
    setup = dedent("""\
        {
        "subreddit": "{{subreddit}}",
        "karma": 1,
        "filter-users": [],
        "filter-subreddits": []
        }""")

    LOG.info(
        'Requesting notifications about /r/{} from /u/Sub_Mentions'.format(
            sub)
    )

    if not DRY_RUN:
        r.send_message('Sub_Mentions', 'Action: Subscribe',
                       setup.replace('{{subreddit}}', sub), from_sr=sub)


_start_points = ['creation', 'settings', 'mods', 'wiki',
                 'flair', 'multireddit', 'notifications']


@command
@click.option('-m', '--multi', type=click.Choice(settings.MULTIREDDITS),
              default=settings.MULTIREDDITS[0],
              help="Which multireddit to add the new sub to.")
@click.option('--start-at', type=click.Choice(_start_points),
              help='Where to start the process from.')
@click.option('--only', type=click.Choice(_start_points),
              help='Only run one section of expansion script.')
@click.option('--dry-run', is_flag=True, help='Don\'t hit reddit')
@click.argument('topic', required=True, nargs=-1)
def main(multi, topic, start_at, only, dry_run):
    """Prop up new subreddit and set it for the network."""
    global DRY_RUN
    DRY_RUN = dry_run

    r = None
    if not DRY_RUN:
        r = Reddit('Expand {} Network v0.2 /u/{}'.format(
                   settings.NETWORK_NAME, settings.USERNAME))
        r.oauth()

    topic = ' '.join(topic)
    nice_topic = ''.join(re.findall('[A-Za-z0-9]', topic))
    sub = settings.NETWORK_NAME + ''.join(nice_topic)

    # little helper script to check if we're at or after
    # where we want to start.
    def should_do(point):
        point_idx = _start_points.index(point)
        if only:
            only_idx = _start_points.index(only)
            return only_idx == point_idx
        elif start_at:
            start_idx = _start_points.index(start_at)
            return start_idx <= point_idx
        return True

    if should_do('creation'):
        create_sub(r, sub)

    if should_do('settings'):
        copy_settings(r, sub, topic)

    if should_do('mods'):
        invite_mods(r, sub)

    if should_do('wiki'):
        copy_wiki_pages(r, sub)

    if should_do('flair'):
        setup_flair(r, sub)

    if should_do('multireddit'):
        add_to_multi(r, sub, multi)

    if should_do('notifications'):
        setup_notifications(r, sub)


if __name__ == '__main__':
    main()
