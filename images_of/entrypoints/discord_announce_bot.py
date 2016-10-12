import click
from images_of import command, settings, Reddit
from images_of.discord_announcer import DiscordBot, DiscordBotSettings


@command
@click.option('-M', '--no-modlog', is_flag=True,
              help='Do not process network modlog events')
@click.option('-O', '--no-oc', is_flag=True,
              help='Do not process network for OC submissions')
@click.option('-I', '--no-inbox', is_flag=True,
              help='Do not process inbox for messages/replies')
@click.option('-F', '--no-falsepositives', is_flag=True,
              help='Do not announce false-positive reports')
@click.option('-r', '--run-interval',
              help='Number of minutes to process items', default=1)
@click.option('-s', '--stats-interval',
              help='Number of minutes to send stats info', default=15)
def main(no_modlog, no_oc, no_inbox,
         no_falsepositives, run_interval, stats_interval):
    """Discord Announcer Bot to relay specified information
       to designated Discord channels.
    """

    reddit = Reddit('{} Discord Announcer v1.1 - /u/{}'
                    .format(settings.NETWORK_NAME, settings.USERNAME))
    reddit.oauth()

    discobot = DiscordBot(reddit)

    botsettings = DiscordBotSettings()

    botsettings.DO_MODLOG = not no_modlog
    botsettings.DO_OC = not no_oc
    botsettings.DO_INBOX = not no_inbox
    botsettings.DO_FALSEPOS = not no_falsepositives
    botsettings.RUN_INTERVAL = run_interval
    botsettings.STATS_INTERVAL = stats_interval

    discobot.run(botsettings)


if __name__ == '__main__':
    main()
