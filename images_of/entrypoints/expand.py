import logging
from textwrap import dedent
import traceback

import click
from praw.errors import SubredditExists

from images_of import settings, Reddit


def create_sub(r, sub):
    try:
        logging.info('Attempting to create /r/{}'.format(sub))
        r.create_subreddit(sub, sub)
        logging.info('Created /r/{}'.format(sub))
    except SubredditExists:
        logging.warning('/r/{} exists'.format(sub))
    except:
        logging.warning(traceback.format_exc())


def invite_mods(r, sub):
    cur_mods = [u.name for u in r.get_moderators(sub)]
    logging.debug('current mods for /r/{}: {}'.format(sub, cur_mods))

    need_mods = [mod for mod in settings.DEFAULT_MODS if mod not in cur_mods]
    logging.debug('inviting {}'.format(need_mods))

    if not need_mods:
        return

    s = r.get_subreddit(sub)
    for mod in need_mods:
        s.add_moderator(mod)

    logging.info('invited {} to moderate')


def setup_notifications(r, sub):
    setup = dedent("""\
        {
        "subreddit": "{{subreddit}}",
        "karma": 1,
        "filter-users": [],
        "filter-subreddits": []
        }""")

    logging.info('Requesting notifications about /r/{} from /u/Sub_Mentions'
                 .format(sub))
    r.send_message('Sub_Mentions', 'Action: Subscribe',
                   setup.replace('{{subreddit}}', sub))

def setup_sub(r, sub, sub_settings, multi, skip_creation,
           skip_mods, skip_notifications):

    if not skip_creation:
        create_sub(r, sub)

    if sub_settings:
        logging.info('Copying settings to /r/{}'.format(sub))
        r.set_settings(sub, **sub_settings)

    if not skip_mods:
        invite_mods(r, sub)

    if multi:
        logging.info('Adding /r/{} to /user/{}/m/{}'
                     .format(sub, settings.USERNAME, multi))
        multi.add_subreddit(sub)

    if not skip_notifications:
        setup_notifications(r, sub)


@click.command()
@click.option('--skip-creation', is_flag=True, help="Don't create, only configure subreddits.")
@click.option('--skip-settings', is_flag=True, help="Don't replace subreddit settings.")
@click.option('--skip-mods', is_flag=True, help="Don't invite mods.")
@click.option('--skip-multi', is_flag=True, help="Don't add subreddits to multireddit.")
@click.option('--skip-notifications', is_flag=True, help="Don't set up notifications.")
@click.argument('subs', required=True, nargs=-1)
def main(subs, skip_multi, skip_settings, **kwargs):
    """Prop up new subreddits and set them up for the network."""

    r = Reddit('Expand {} Network /u/{}'
               .format(settings.NETWORK_NAME, settings.USERNAME))
    r.oauth()

    sub_settings = None
    if not skip_settings:
        sub_settings = r.get_settings(settings.MASTER_SUB)
    logging.debug('Copied information from {}: {}'
                  .format(settings.MASTER_SUB, sub_settings)

    multi = None
    if not skip_multi and settings.MULTIREDDIT:
        multi = r.get_multireddit(settings.USERNAME, settings.MULTIREDDIT)

    for sub in subs:
        setup_sub(r, sub, sub_settings, multi, **kwargs)

if __name__ == '__main__':
    main()
