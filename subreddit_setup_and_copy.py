import praw
import OAuth2Util

import traceback, time

# sleep time in seconds
sleeptime = 30

slaver_sub = "imagesofnetwork"
make_slaves = True

username = "amici_ursi"

slave_subs = [ImagesOfAfghanistan',
              'ImagesOfalabama',
              'ImagesOfAlaska',
              'ImagesOfArizona',
              'ImagesOfArkansas',
              'ImagesOfAustralia',
              'ImagesOfBelgium',
              'ImagesOfBelize',
              'ImagesOfBrazil',
              'ImagesOfCalifornia',
              'ImagesOfCanada',
              'ImagesOfChile',
              'ImagesOfChina',
              'ImagesOfColorado',
              'ImagesOfConnecticut',
              'ImagesOfDelaware',
              'ImagesOfEngland',
              'ImagesOfFlorida',
              'ImagesOfFrance',
              'ImagesOfGeorgia',
              'ImagesOfGuatemala',
              'ImagesOfHawaii',
              'ImagesOfHongKong',
              'ImagesOfIceland',
              'ImagesOfIdaho',
              'ImagesOfIllinois',
              'ImagesOfIndia',
              'ImagesOfIndiana',
              'ImagesOfIowa',
              'ImagesOfIran',
              'ImagesOfIsleOfMan',
              'ImagesOfJapan',
              'ImagesOfKansas',
              'ImagesOfKentucky',
              'ImagesOfLibya',
              'ImagesOfLouisiana',
              'ImagesOfMaine',
              'ImagesOfMaldives',
              'ImagesOfMaryland',
              'ImagesOfMassachusetts',
              'ImagesOfMexico',
              'ImagesOfMichigan',
              'ImagesOfMinnesota',
              'ImagesOfMississippi',
              'ImagesOfMissouri',
              'ImagesOfMontana',
              'ImagesOfNebraska',
              'ImagesOfNetherlands',
              'ImagesOfNetwork',
              'ImagesOfNevada',
              'ImagesOfNewHampshire',
              'ImagesOfNewJersey',
              'ImagesOfNewMexico',
              'ImagesOfNewYork',
              'ImagesOfNewZealand',
              'ImagesOfNorthCarolina',
              'ImagesOfNorthDakota',
              'ImagesOfNorway',
              'ImagesOfOhio',
              'ImagesOfOklahoma',
              'ImagesOfOregon',
              'ImagesOfPennsylvania',
              'ImagesOfPeru',
              'ImagesOfRhodeIsland',
              'ImagesOfRussia',
              'ImagesOfScotland',
              'ImagesOfSouthCarolina',
              'ImagesOfSouthDakota',
              'ImagesOfSyria',
              'ImagesOfTennessee',
              'ImagesOfTexas',
              'ImagesOfToronto',
              'ImagesOfUSA',
              'ImagesOfUtah',
              'ImagesOfVermont',
              'ImagesOfVirginia',
              'ImagesOfWales',
              'ImagesOfWashington',
              'ImagesOfwashingtondc',
              'ImagesOfWestVirginia',
              'ImagesOfWisconsin',
              'ImagesOfWyoming',
              'ImagesOfYemen'
              ]

INVITE_MODS = ['Automoderator', 'BotWatchman']

subnotification_setup = """{
"subreddit": "{{subreddit}}",
"karma": 1,
"filter-users": [],
"filter-subreddits": []
}"""

add_to_multi = "imagesofplaces"

USERAGENT = "Copying subreddit settings from {0} to the subs in it's network for /u/{1}".format(slaver_sub, username)

def whipslaves(reddit_session, base_settings, do_mods=False, base_mods=None):
    """To keep any settings of the slave subs, change 'settings' in that line to 'settings2'."""
    settings = reddit_session.get_settings(slaver_sub)
    dummy = False
    slaver_mods = None
    if add_to_multi:
        add_to_multi = reddit_session.get_multireddit(username, add_to_multi)
    if do_mods:
        slaver_mods = [user.name for user in reddit_session.get_moderators(slaver_sub)]
    for subreddit in slave_subs:
        if add_to_multi:
            add_to_multi.add_subreddit(subreddit)
        if subnotification_setup:
            reddit_session.send_message('Sub_Mentions', 'Action: Subscribe', subnotification_setup.replace('{{subreddit}}', subreddit))
        if settings == base_settings:
            continue
        dummy = True
        settings2 = reddit_session.get_settings(subreddit)
        slave_obj = reddit_session.get_subreddit(subreddit)
        reddit_session.set_settings(slave_obj,
                                    exclude_banned_modqueue=settings['exclude_banned_modqueue'], # exclude shadowbanned users from the modqueue and unmoderated
                                    submit_text_label=settings['submit_text_label'],
                                    comment_score_hide_mins=settings['comment_score_hide_mins'],
                                    default_set=settings['default_set'], # no fucking clue
                                    domain=settings['domain'], # legacy thing related to domains.
                                    wikimode=settings['wikimode'], # wiki disabled, mod only, or anyone
                                    spam_links=settings['spam_links'], # spam filter strength on links
                                    spam_selfposts=settings['spam_selfposts'], # spam filter strength on posts
                                    domain_sidebar=settings['domain_sidebar'], # legacy thing related to domains.
                                    collapse_deleted_comments=settings['collapse_deleted_comments'],
                                    header_hover_text=settings['header_hover_text'],
                                    over_18=settings['over_18'], # is the sub NSFW
                                    content_options=settings['content_options'], # allow only link / self posts / both
                                    show_media=settings['show_media'], # thumbnails
                                    submit_link_label=settings['submit_link_label'],
                                    submit_text=settings['submit_text'], 
                                    title=settings['title'], # title, ie slashdot
                                    description=settings['description'], # subreddit description
                                    wiki_edit_age=settings['wiki_edit_age'], # age of accounts that will edit the wiki
                                    hide_ads=settings['hide_ads'], # gold only hide ads feature. Defaults to false if the slaver is not gold only
                                    spam_comments=settings['spam_comments'], # spam filter strength on comments
                                    public_traffic=settings['public_traffic'],
                                    subreddit_type=settings['subreddit_type'], # public, restricted, etc
                                    language=settings['language'],
                                    wiki_edit_karma=settings['wiki_edit_karma'],
                                    public_description=settings['public_description'], # sidebar
                                    domain_css=settings['domain_css'], # legacy thing related to domains
                                    )
    for subreddit in slave_subs:
        if do_mods and (slaver_mods != base_mods):
            dummy = True
            slave_mods = [user.name for user in reddit_session.get_moderators(subreddit)]
            intersected_mods = [name for name in slaver_mods if name not in slave_mods]
            slave_obj = reddit_session.get_subreddit(subreddit)
            for name in intersected_mods:
              slave_obj.add_moderator(name)
            
    return [settings, slaver_mods, dummy]
    
def main(reddit_session, do_mods=False):
    global slave_subs
    base_settings = reddit_session.get_settings(slaver_sub)
    base_mods = INVITE_MODS
    if do_mods:
        base_mods = base_mods or [user.name for user in reddit_session.get_moderators(slaver_sub)]
    if make_slaves:
        for i in slave_subs[:]:
            try:
              r.create_subreddit(i, i)
            except:
              traceback.print_exc()
              slave_subs.remove(i)
    while True:
        try:
            ret = whipslaves(reddit_session, base_settings, do_mods, base_mods)
            if ret[2]:
              base_settings = ret[0]
              base_mods = ret[1]
        except KeyboardInterrupt:
            raise
        except Exception as e:
            traceback.print_exc()
        time.sleep(sleeptime)
        
if __name__ == '__main__':
    r = praw.Reddit(USERAGENT)
    o = OAuth2Util.OAuth2Util(r)
    o.refresh(force=True)
    main(r)
