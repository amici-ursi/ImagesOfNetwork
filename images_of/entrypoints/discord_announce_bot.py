from images_of import command, settings, Reddit
from images_of.discord_announcer import DiscordBot


@command
def main():
    """Discord Announcer Bot to relay specified information to designated Discord channels."""

    r = Reddit('{} Discord Announcer v1.0 - /u/{}'.format(settings.NETWORK_NAME, settings.USERNAME))
    r.oauth()

    b = DiscordBot(r)
    b.run()


if __name__ == '__main__':
    main()
