import click

from images_of import settings, Reddit
from images_of.subreddit import Subreddit

def copy_wiki_page(r, page, dom, subs):
    content = r.get_wiki_page(dom, page).content_md
    for sub in subs:
        r.edit_wiki_page(sub, page, content)

@click.command()
@click.option('--wiki', multiple=True, help='Wiki page to copy')
def main(wiki):
    """Propigate settings across the network"""

    dom = settings.MASTER_SUB
    subs = [slave['name'] for slave in settings.SLAVE_SUBS]

    r = Reddit('Copy Network Settings v0.1 /u/{}'.format(settings.USERNAME))
    r.oauth()

    for page in wiki:
        copy_wiki_page(r, page, dom, subs)

if __name__ == '__main__':
    main()
