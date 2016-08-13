import click
import time
from time import gmtime
from datetime import date
from images_of import command, settings, Reddit


@command
@click.option(
    '--history-days',
    help='How many days back into the modlog run. Default is 30 days',
    default=60
)
def main(history_days):
    """Process modlogs to identify inactive mods"""

    mods = settings.DEFAULT_MODS

    r = Reddit(
        '{} ModLog Auditor v0.1 - /u/{}'.format(
            settings.NETWORK_NAME, settings.USERNAME)
    )
    r.oauth()

    subs = sorted([sub['name'] for sub in settings.CHILD_SUBS])

    end_utc = gmtime(time.time() - 60 * 60 * 24 * history_days)
    end_date = date(end_utc[0], end_utc[1], end_utc[2])

    for sub in subs:
        print('Processing {} modlog...'.format(sub))
        done = False
        last = None
        count = 0

        s = r.get_subreddit(sub)
        all_mods = [u.name for u in s.get_moderators()]
        real_mods = [m for m in all_mods if m not in mods]

        # If no real moderators, don't process this subreddit modlog
        if not real_mods:
            continue
        else:
            mod_action_count = dict()
            mod_last_action = dict()

            while not done:
                log = list(s.get_mod_log(limit=50, params={"after": last}))

                if len(log) == 0:
                    done = True
                    break
                else:
                    last = log[-1].id

                for log_entry in [l for l in log if l.mod in real_mods]:
                    created_utc = log_entry.created_utc
                    time_utc = gmtime(created_utc)
                    date_utc = date(time_utc[0], time_utc[1], time_utc[2])

                    if date_utc >= end_date:
                        mod_action_count[log_entry.mod] = mod_action_count.get(
                            log_entry.mod, 0) + 1

                        if date_utc > mod_last_action.get(log_entry.mod,
                                                          date(1901, 1, 1)):
                            mod_last_action[log_entry.mod] = date_utc
                    else:
                        # Reached end date
                        done = True
                        break

                if count >= 5000:
                    done = True
                    break

                count += 100

        print('Subredit Moderation Log Stats '
              'for {}:\t\t({} entries parsed)'.format(sub, count))
        for m in real_mods:
            print('    {}:\n\tActions: {}'
                  '  \tLast Active: {}\n'.format(
                      m, mod_action_count.get(m, 0),
                      mod_last_action.get(m, date(1901, 1, 1))))


if __name__ == '__main__':
    main()
