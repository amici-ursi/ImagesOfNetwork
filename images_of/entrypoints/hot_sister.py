# Fetches the host posts from a parent multireddit and updates the children's sidebars with a list of them
# The child subreddit's sidebar must include strings to denote the beginning and ending location of the list, the bot will not update the sidebar if these strings are not present
# With the default delimiters, the sidebar should include a chunk of text like:
# 
# **Top posts in our sister subreddit:**
# [](/hot-sister-start)
# [](/hot-sister-end)
# Other text that will be below the list

import re
import html.parser
import time
#import praw
from images_of import settings, Reddit
#import os

# defines the main and sister subreddits, and how many posts to list in the sidebar
PLACES_MULTI_NAME = 'imagesofplaces'
DECADES_MULTI_NAME = 'imagesofthedecades'
POSTS_TO_LIST = 5
START_DELIM = '[](/hot-sister-start)'
END_DELIM = '[](/hot-sister-end)'

def main():
    r = Reddit('{} hot_sister v3 - /u/{}'.format(settings.NETWORK_NAME, settings.USERNAME))
    r.oauth()

    # places multireddit
    places_multi = r.get_multireddit(settings.USERNAME, PLACES_MULTI_NAME)
    places_list_text = str()
    for post in places_multi.get_hot(limit=POSTS_TO_LIST):
        places_list_text += ' * [%s](%s)\n' % (post.title, post.permalink)

    # decades multireddit
    decades_multi = r.get_multireddit(settings.USERNAME, DECADES_MULTI_NAME)
    decades_list_text = str()
    for (i, post) in enumerate(DECADES_MULTI.get_hot(limit=POSTS_TO_LIST)):
        decades_list_text += ' * [%s](%s)\n' % (post.title, post.permalink)

    # bring it together
    combined_text= "* Places:\n{}\n\n* Times:\n{}".format(places_list_text, decades_list_text)

    # set up all the children
    children = sorted([sub['name'] for sub in settings.CHILD_SUBS])
    for child in children:
        print("running on {}".format(child))
        sub = r.get_subreddit(child)

        current_sidebar = sub.get_settings()['description']
        current_sidebar = html.unescape(current_sidebar)

        # ew
        replace_pattern = re.compile('%s.*?%s'.format(
                re.escape(START_DELIM),
                re.escape(END_DELIM)),
            re.IGNORECASE|re.DOTALL|re.UNICODE)

        # ew
        new_sidebar = re.sub(replace_pattern,
                            '{}\\n\\n{}\\n{}'.format(
                                START_DELIM,
                                combinex_text,
                                END_DELIM),
                            current_sidebar)

        sub.update_settings(description=new_sidebar)


if __name__ == '__main__':
    main()
