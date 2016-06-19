import click
from collections import defaultdict
from datetime import datetime, timedelta
from images_of import command, settings, Reddit

@command
@click.option('--history-days', help='How many days back into the modlog run. Default is 60 days', default=60)
def main(history_days):
    """Process modlogs to identify inactive mods.

    Max 5k ModActions per modlog processed.

    :param history_days: max days to check the modlog
    """
    
    exclude_mods = settings.DEFAULT_MODS

    r = Reddit('{} ModLog Auditor v0.2 - /u/{}'.format(settings.NETWORK_NAME, settings.USERNAME))
    r.oauth()

    subs = sorted([sub['name'] for sub in settings.CHILD_SUBS])
    
    end_date = datetime.utcnow().date() - timedelta(days=history_days)
    
    for sub in subs:
        print('Processing {} modlog...'.format(sub))
        
        s = r.get_subreddit(sub)
        real_mods = [u.name for u in s.get_moderators()
                     if u.name not in exclude_mods]

        if not real_mods:  # If no real moderators, don't process this subreddit modlog
            continue
        mod_action_count = defaultdict(lambda: 0)
        mod_last_action = {}
        log = enumerate(s.get_mod_log(limit=None), start=1)
        for count, log_entry in log:
            if l.mod not in real_mods:
                continue

            date_utc = datetime.utcfromtimestamp(log_entry.created_utc).date()
            if date_utc >= end_date:
                mod_action_count[log_entry.mod] += 1
                # set if not set, else ignore since actions are chronological
                mod_last_action.setdefault(log_entry.mod, date_utc)
            # Reached end date
            else:
                break
            sub_count = count  # Used in intermediate sub-based stats
            if count >= 5000:
                break


        print('Subredit Moderation Log Stats for {}:\t\t({} entries parsed)'.format(sub, sub_count))
        for m in real_mods:
            print('    {}:\n\tActions: {}  \tLast Active: {}'.format(m, mod_action_count[m], mod_last_action.get(m, "Out of range")))


if __name__ == '__main__':
    main()
