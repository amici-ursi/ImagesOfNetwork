import logging

import click

from images_of import settings, Reddit
from images_of.subreddit import Subreddit

def split_content(content, start_delim, end_delim, tags_required=True):
    if tags_required:
        ok = True
        if start_delim not in content:
            logging.warning('Missing {}'.format(start_delim))
            ok = False

        if end_delim not in content:
            logging.warning('Missing {}'.format(start_delim))
            ok = False

        if not ok:
            return None

    head = ""
    if start_delim in content:
        head, content = content.split(start_delim)

    tail = ""
    if end_delim in content:
        content, tail = content.split(end_delim)

    return (head, content, tail)

def copy_wiki_page(r, page, dom, subs, force):
    start_delim = "#Start-{}-Network-Config".format(settings.NETWORK_NAME)
    end_delim = "#End-{}-Network-Config".format(settings.NETWORK_NAME)

    content = r.get_wiki_page(dom, page).content_md
    # Throw away the head and tail sections, don't care about them, we won't
    # be copying them or editing this page.
    content = split_content(content, start_delim, end_delim, False)[1]

    for sub in subs:
        sub_content = r.get_wiki_page(sub, page).content_md
        parts = split_contents(sub_content, start_delim, end_delim, not force)

        new_content = ''.join(
                parts[0],
                start_delim,
                parts[1],
                end_delim,
                parts[2])

        logging.debug('New content for /r/{}/wiki/{}: {}'.format(
                            sub, page, new_content))

        r.edit_wiki_page(sub, page, new_content)

@click.command()
@click.option('--automod', is_flag=True,
              help='Copy automod settings. This is an alias for \'--wiki config/automoderator\'')
@click.option('--wiki', multiple=True, help='Wiki page to copy')
@click.option('-f', '--force', is_flag=True, help='Overwrite even if section tags not found')
def main(automod, wiki, force):
    """Propigate settings across the network"""

    dom = settings.MASTER_SUB
    subs = [slave['name'] for slave in settings.SLAVE_SUBS]

    r = Reddit('Copy Network Settings v0.1 /u/{}'.format(settings.USERNAME))
    r.oauth()

    if automod:
        wiki = set(wiki)
        wiki.update('config/automoderator')
        wiki = list(wiki)

    for page in wiki:
        copy_wiki_page(r, page, dom, subs, force)

if __name__ == '__main__':
    main()