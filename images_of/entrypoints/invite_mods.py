import click
from images_of import command, settings, Reddit


@command
@click.option('--defaults', is_flag=True, help='Invite default moderators')
@click.option('--cousins', is_flag=True,
              help='Invite to cousin subs as well as children')
@click.argument('mods', nargs=-1)
def main(mods, defaults, cousins):

    if defaults:
        mods = set(mods)
        mods.union(settings.DEFAULT_MODS)
        mods = list(mods)

    if not mods:
        print('No moderators specified. Quitting.')
        return

    r = Reddit('Mass Moderator Invite v0.1 /u/{}'.format(settings.USERNAME))
    r.oauth()

    subs = [sub['name'] for sub in settings.CHILD_SUBS]
    if cousins:
        cuzs = set(sub['name'] for sub in settings.COUSIN_SUBS)
        cuzs.update(subs)
        subs = sorted(cuzs)

    for sub in subs:
        s = r.get_subreddit(sub)
        cur_mods = [u.name for u in s.get_moderators()]
        need_mods = [m for m in mods if m not in cur_mods]

        if not need_mods:
            print('No mods needed for /r/{}.'.format(sub))

        for mod in need_mods:
            print('Inviting {} to moderate /r/{}.'.format(mod, sub))
            s.add_moderator(mod)

if __name__ == '__main__':
    main()
