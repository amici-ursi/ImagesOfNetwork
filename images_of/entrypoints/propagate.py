import click
import logging

from images_of import command, settings, Reddit


LOG = logging.getLogger(__name__)


def split_content(content, start_delim, end_delim,
                  tags_required=True, case_insensitive=False):
    if case_insensitive:
        content_match = content.lower()
        start_delim = start_delim.lower()
        end_delim = end_delim.lower()
    else:
        content_match = content

    if tags_required:
        ok = True
        if start_delim not in content_match:
            LOG.warning('Missing {}'.format(start_delim))
            ok = False

        if end_delim not in content_match:
            LOG.warning('Missing {}'.format(start_delim))
            ok = False

        if not ok:
            return None

    head = ""
    if start_delim in content_match:
        start = content_match.find(start_delim)
        end = start + len(start_delim)
        head, content = content[:start], content[end:]
        content_match = content_match[end:]

    tail = ""
    if end_delim in content_match:
        start = content_match.find(end_delim)
        end = start + len(end_delim)
        content, tail = content[:start], content[end:]

    return (head, content, tail)


def copy_wiki_page(r, page, dom, subs, force):
    start_delim = "#Start-{}-Network".format(settings.NETWORK_NAME)
    end_delim = "#End-{}-Network".format(settings.NETWORK_NAME)

    content = r.get_wiki_page(dom, page).content_md
    # Throw away the head and tail sections, don't care about them, we won't
    # be copying them or editing this page.
    content = split_content(content, start_delim, end_delim, False, True)[1]

    for sub in subs:
        LOG.info('Updating /r/{}/wiki/{}'.format(sub, page))
        sub_content = r.get_wiki_page(sub, page).content_md
        parts = split_content(sub_content, start_delim, end_delim, not force)

        new_content = ''.join([
            parts[0],
            start_delim,
            content,
            end_delim,
            parts[2]
        ])

        LOG.debug('New content for /r/{}/wiki/{}: {}'.format(sub, page,
                                                             new_content))

        r.edit_wiki_page(sub, page, new_content)


@command
@click.option('--automod', is_flag=True,
              help=("Copy automod settings. "
                    "This is an alias for '--wiki config/automoderator'"))
@click.option('--toolbox', is_flag=True, help='Copy toolbox settings')
@click.option('--wiki', multiple=True, help='Wiki page to copy')
@click.option('-f', '--force', is_flag=True,
              help='Overwrite even if section tags not found')
def main(automod, toolbox, wiki, force):
    """Propigate settings across the network"""

    dom = settings.PARENT_SUB
    subs = [sub['name'] for sub in settings.CHILD_SUBS]

    r = Reddit('Copy Network Settings v0.1 /u/{}'.format(settings.USERNAME))
    r.oauth()

    if automod:
        wiki = set(wiki)
        wiki.update(['config/automoderator'])
        wiki = list(wiki)

    for page in wiki:
        copy_wiki_page(r, page, dom, subs, force)

    if toolbox:
        page = 'toolbox'
        content = r.get_wiki_page(dom, page).content_md
        for sub in subs:
            r.edit_wiki_page(sub, page, content)

if __name__ == '__main__':
    main()
