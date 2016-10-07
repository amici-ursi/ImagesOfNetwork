#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="images_of",
    version="0.1.0",

    author="acimi-ursi",
    description="Tools for managing the ImagesOfNetwork on reddit",
    url="https://github.com/amici-ursi/ImagesOfNetwork",

    packages=find_packages(),

    install_requires=[
        "click",
        "praw==3.5",
        "pytoml",
        "discord.py==0.10.0",
        "sphinx",
        "feedparser",
    ],

    entry_points={
        "console_scripts": [
            "ion_expand = images_of.entrypoints.expand:main",
            "ion_setup_oauth = images_of.entrypoints.oauth:main",
            "ion_bot = images_of.entrypoints.bot:main",
            "ion_propagate = images_of.entrypoints.propagate:main",
            "ion_invite_mods = images_of.entrypoints.invite_mods:main",
            "ion_bulkmail = images_of.entrypoints.bulkmail:main",
            "ion_audit_mods = images_of.entrypoints.audit_mods:main",
            "ion_blacklist_requests = "
            "images_of.entrypoints.blacklist_requests:main",
            "ion_hot_sister = images_of.entrypoints.hot_sister:main",
            "ion_discord_bot = "
            "images_of.entrypoints.discord_announce_bot:main",
            "ion_feeds = images_of.entrypoints.feeds:main",
        ],
    },

    data_files=[
        ('images_of', 'data/*.toml'),
    ],
)
