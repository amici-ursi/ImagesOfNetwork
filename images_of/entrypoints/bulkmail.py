import click
from images_of import command, settings, Reddit


@command
@click.option('-s', '--subject', required=True, help='Message subject')
@click.option('-m', '--message', required=True, help='Message body')
def main(subject, message):
    ok = True
    if not subject:
        print('Subject may not be empty')
        ok = False
    if not message:
        print('Messgae may not be empty')
        ok = False
    if not ok:
        return

    r = Reddit('{} Network Mailer v0.1 /u/{}'.format(settings.NETWORK_NAME,
                                                     settings.USERNAME))
    r.oauth()

    subs = ["/r/{}".format(sub['name']) for sub in settings.CHILD_SUBS]
    for sub in subs:
        print('Mailing {}'.format(sub))
        r.send_message(sub, subject, message)


if __name__ == '__main__':
    main()
