import click
import logging

from images_of import settings, Reddit

LOG = logging.getLogger(__name__)


@click.command()
def main():
    """
    Check for blacklist requests and add users to blacklist.
    """

    r = Reddit('{} Update User-Requested Blacklist v0.1 /u/{}'
               .format(settings.NETWORK_NAME, settings.USERNAME))
    r.oauth()

    add_users = set()

    sub = settings.MASTER_SUB

    modmail_inbox = r.get_mod_mail(sub)

    for m in [i for i in modmail_inbox if not i.replies]:

        if any('blacklist me' in i.lower() for i in (m.subject, m.body)):

            orig_blacklist = get_user_blacklist(r)

            author = m.author.name.lower()
            if '/u/{}'.format(author) not in orig_blacklist:
                add_users.add(author)
                m.reply('Your images will no longer be crossposted on the {} Network.'
                        .format(settings.NETWORK_NAME))
            else:
                LOG.info('User {} is already in blacklist; skipping'.format(m.author.name))

    if add_users:
        update_user_blacklist(r, add_users)
    else:
        LOG.info('No new blacklist requests to process')


def get_user_blacklist(r):

    dom = settings.MASTER_SUB
    page = 'userblacklist'
    dom_content = r.get_wiki_page(dom, page).content_md
    orig_blacklist = set(dom_content.split())

    return map(str.lower, orig_blacklist)


def update_user_blacklist(r, add_users):

    dom = settings.MASTER_SUB
    page = 'userblacklist'

    orig_blacklist = get_user_blacklist(r)
    blacklist = set(orig_blacklist)

    LOG.debug('Original blacklist: {}'.format(orig_blacklist))
    LOG.info('Adding users: {}'.format(add_users))

    blacklist.update(['/u/'+u for u in add_users])

    if orig_blacklist == add_users:
        LOG.info('User blacklist has not changed; not modifying the wiki')
        return

    new_content = '\n\n'.join(sorted(blacklist))

    r.edit_wiki_page(dom, page, new_content, 'Blacklist requests for: {}'.format(add_users))


if __name__ == '__main__':
    main()
