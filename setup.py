#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name = "images_of",
    version = "0.1",

    author = "acimi-ursi",
    description = "Tools for managing the ImagesOfNetwork on reddit",
    url = "https://github.com/amici-ursi/ImagesOfNetwork",

    packages = find_packages(),

    install_requires = [
        "praw==3.4",
    ],

    scripts = [
        "copy_wiki_pages.py",
        "imagesof_bot.py",
        "subreddit_setup_and_copy.py",
    ],
)
