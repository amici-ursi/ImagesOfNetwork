import click

from images_of import settings, Reddit
from images_of.bot import Bot


@click.command()
@click.option('--no-post', is_flag=True, help='Do not post to reddit.')
def main(no_post):
    """Reddit Network scraper and x-poster bot."""

    r = Reddit('{} v6.0 /u/{}'.format(settings.NETWORK_NAME, settings.USERNAME))
    r.oauth()

    b = Bot(r, should_post=not no_post)
    b.run()


if __name__ == '__main__':
    main()
