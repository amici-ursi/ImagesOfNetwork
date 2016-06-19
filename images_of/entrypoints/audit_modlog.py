import click
from collections import defaultdict
from datetime import date, datetime, timedelta
from images_of import command, settings, Reddit

@command
@click.option('--history-days', help='How many days back into the modlog run. Default is 60 days', default=60)
def main(history_days):
    """Process modlogs to identify inactive mods"""
    
    exclude_mods = settings.DEFAULT_MODS
    dummy_min_date = date(1901, 1, 1)

    r = Reddit('{} ModLog Auditor v0.1 - /u/{}'.format(settings.NETWORK_NAME, settings.USERNAME))
    r.oauth()

    subs = sorted([sub['name'] for sub in settings.CHILD_SUBS])
    
    end_date = datetime.utcnow().date() - timedelta(days=history_days)
    
    for sub in subs:
        print('Processing {} modlog...'.format(sub))
        done = False
        last = None
        last_time = -1
        count = 0
        first_id = None
        
        s = r.get_subreddit(sub)
        real_mods = [u.name for u in s.get_moderators()
                     if u.name not in exclude_mods]

        if not real_mods:   ## If no real moderators, don't process this subreddit modlog
            continue
        else:
            mod_action_count = defaultdict(lambda: 0)
            mod_last_action = dict()

            while not done:
                log = list(s.get_mod_log(limit=500, params={"after": last}))

                if len(log) == 0:
                    done = True
                    break
                else:
                    last = log[-1].id
                
                for log_entry in log:
                    if l.mod not in real_mods:
                        continue

                    date_utc = datetime.utcfromtimestamp(log_entry.created_utc).date()

                    if date_utc >= end_date:
                        mod_action_count[log_entry.mod] += 1
                        # set if not set, else ignore since actions are chronological
                        mod_last_action.setdefault(log_entry.mod, date_utc)
                            
                    # Reached end date
                    else:
                        done = True
                        break
                    

                if count >= 5000:
                    done = True
                    break
                    
                count += 500


        print('Subredit Moderation Log Stats for {}:\t\t({} entries parsed)'.format(sub, count))
        for m in real_mods:
            print('    {}:\n\tActions: {}  \tLast Active: {}'.format(m, mod_action_count.get(m, 0), mod_last_action.get(m, dummy_min_date)))


if __name__ == '__main__':
    main()
