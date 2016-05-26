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
CHILDREN = settings.CHILD_SUBS
PLACES_MULTI_NAME = 'imagesofplaces'
DECADES_MULTI_NAME = 'imagesofthedecades'
POSTS_TO_LIST = 5
START_DELIM = '[](/hot-sister-start)'
END_DELIM = '[](/hot-sister-end)'

# log into reddit
#print("logging into hot_sister")
#client_username = os.environ.get("hot_sister_username")
#print("client_username: {}".format(client_username))
#client_password = os.environ.get("hot_sister_password")
#print("client_password: {}".format(client_password))
#r = praw.Reddit(user_agent="hot_sister fork by /u/amici_ursi")
#r.login(client_username, client_password)



def main():
    #r is for ...
    r = Reddit('{} hot_sister v3 - /u/{}'.format(settings.NETWORK_NAME, settings.USERNAME))
    #log in
    r.login(settings.USERNAME, settings.PASSWORD)
    #identify the places multireddit
    PLACES_MULTI = r.get_multireddit(settings.USERNAME, PLACES_MULTI_NAME)
    #make the places post list
    PLACES_LIST_TEXT = str()
    for (i, post) in enumerate(PLACES_MULTI.get_hot(limit=POSTS_TO_LIST)):
        PLACES_LIST_TEXT += ' * [%s](%s)\n' % (post.title, post.permalink)
    #identify the decades multireddit
    DECADES_MULTI = r.get_multireddit(settings.USERNAME, DECADES_MULTI_NAME)
    #make the decades post list
    DECADES_LIST_TEXT = str()
    for (i, post) in enumerate(DECADES_MULTI.get_hot(limit=POSTS_TO_LIST)):
        DECADES_LIST_TEXT += ' * [%s](%s)\n' % (post.title, post.permalink)
    #combine places and decades lists
    COMBINED_TEXT = "* Places:\n{}\n\n* Times:\n{}".format(PLACES_LIST_TEXT, DECADES_LIST_TEXT)
    #update the children sidebars
    for CHILD in CHILDREN:
        #say who we're updating
        print("running on {}".format(CHILD))
        subreddit = r.get_subreddit(CHILD)
        #get the child's sidebar
        current_sidebar = CHILD.get_settings()['description']
        current_sidebar = html.parser.HTMLParser().unescape(current_sidebar)
        #find the delimiters and what's between them
        replace_pattern = re.compile('%s.*?%s' % (re.escape(START_DELIM), re.escape(END_DELIM)), re.IGNORECASE|re.DOTALL|re.UNICODE)
        #replace the sidebar text with the combined list
        new_sidebar = re.sub(replace_pattern,
                            '%s\\n\\n%s\\n%s' % (START_DELIM, COMBINED_TEXT, END_DELIM),
                            current_sidebar)
        #update the child's sidebar
        CHILD.update_settings(description=new_sidebar)



main()
