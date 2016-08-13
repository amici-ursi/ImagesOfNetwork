import click
from images_of import command, settings, Reddit


@command
@click.option(
    '--print-mods', is_flag=True,
    help='List the non-default moderators for all subreddits')
def main(print_mods):
    """Find subs without mods and disenfranchised mods"""

    mods = settings.DEFAULT_MODS

    r = Reddit('Moderator Auditor v0.1')
    r.oauth()

    subs = sorted([sub['name'] for sub in settings.CHILD_SUBS])
    empty_subs = list()

    orphan_mods = dict()
    s = r.get_subreddit(settings.PARENT_SUB)
    main_sub_mods = [u.name for u in s.get_moderators()]

    for sub in subs:
        s = r.get_subreddit(sub)
        cur_mods = [u.name for u in s.get_moderators()]
        real_mods = [m for m in cur_mods if m not in mods]

        if not real_mods:
            empty_subs.append(sub)
        else:
            if print_mods:
                print('{} : {}'.format(sub, real_mods))

            for m in [i for i in real_mods if i not in main_sub_mods]:
                orphan_mods[m] = orphan_mods.get(m, []) + [sub]

    print()
    print('Unmoderated Subreddits: {}'.format(len(empty_subs)))
    print('-----------------------')

    for sub in sorted(empty_subs):
        print(sub)

    print()
    print('Orphaned Moderators: {}'.format(len(orphan_mods)))
    print('-------------------------')

    for m, s in orphan_mods.items():
        print('{} : {}'.format(m, s))


if __name__ == '__main__':
    main()
