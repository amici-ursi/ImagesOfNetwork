#!/usr/bin/env python
import praw

USERNAME = 'username'
PASSWORD = 'password'

# Whichever one you want it to copy from (don't include the /r/)
SUBREDDIT_TO_COPY_FROM = 'imagesofnetwork'

# Add more if you need to
PAGES_TO_COPY = ['config/automoderator']


def get_wiki_content(r, page):
    return r.get_wiki_page(SUBREDDIT_TO_COPY_FROM, page).content_md


def copy_to_subs(r, page, content, subs):
    for sub in subs:
        print('Copied {} to {}.'.format(page, sub))
        r.edit_wiki_page(sub, page=page, content=content, reason='link flair')


def main():
    r = praw.Reddit('Copies Wiki Pages v1.0 /u/EDGYALLCAPSUSERNAME')
    r.login(USERNAME, PASSWORD)

    with open('subs.txt.places') as f:
        subs_to_copy_to = f.read().splitlines()

    for page in PAGES_TO_COPY:
        print("Copying {}...".format(page))
        wiki_content = get_wiki_content(r, page)
        copy_to_subs(r, page, wiki_content, subs_to_copy_to)

if __name__ == '__main__':
    main()
