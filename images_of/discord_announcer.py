"""
Discord Announcer Bot to relay important and relevant network information to
    designated Discord channels on regular intervals.
"""
import asyncio
from collections import deque
from random import randint
import datetime
import logging
from time import sleep

import discord
import github3
from praw.errors import HTTPException
import requests

from images_of import settings
from images_of.discord_formatters import is_relayable_message, format_inbox_message
from images_of.discord_formatters import format_github_issue_comment, format_github_issue_event
from images_of.discord_formatters import format_github_pull_request, format_github_push_event
from images_of.discord_formatters import format_mod_action

RUN_INTERVAL = 0.5  # minutes
STATS_INTERVAL = 15  # minutes
LOG = logging.getLogger(__name__)

# message type mapping
TYPES = {
    't1': 'comment',
    't2': 'account',
    't3': 'link',
    't4': 'message',
    't5': 'subreddit',
    't6': 'award',
    't8': 'promocampaign'
}
MODLOG_ACTIONS = ['invitemoderator',
                  'acceptmoderatorinvite', 'removemoderator']
EVENT_FILTER = ['IssuesEvent', 'PullRequestEvent', 'PushEvent']
#edited, unlabeled, unassigned, assigned, labeled
ISSUE_ACTION_FILTER = ["opened", "closed", "reopened"]
PULL_REQUEST_ACTION_FILTER = ["opened", "edited",
                              "closed", "reopened", "synchronize"]


class DiscordBot:
    """Discord Announcer Bot to relay important and relevant network information to
    designated Discord channels on regular intervals."""

    def __init__(self, reddit):
        self.reddit = reddit
        self.run_init = True

        self._setup_client()

        self.last_oc_id = dict()
        self.oc_stream_placeholder = dict()
        self.last_modlog_action = dict()

        self.count_messages = 0
        self.count_oc = 0
        self.count_gh_events = 0
        self.count_modlog = 0

        self.ghub = github3.login(token=settings.GITHUB_OAUTH_TOKEN)
        repo = self.ghub.repository(
            settings.GITHUB_REPO_USER, settings.GITHUB_REPO_NAME)
        self.last_github_event = repo.iter_events(number=1).next().id

    def _setup_client(self):
        loop = asyncio.get_event_loop()
        loop.slow_callback_duration = 10
        self.client = discord.Client()
        self.client.event(self.on_ready)

    # ======================================================

    async def _relay_inbox_message(self, message):

        self.count_messages += 1

        # Determine if it's a message that we do NOT want to relay...
        if is_relayable_message(message):

            if 'false positive' in message.body.lower():
                LOG.info('[Inbox] Announcing false-positive reply.')
                notification = "New __false-positive__ report from **/u/{}**:\r\n{}\r\n ".format(
                    message.author.name, message.permalink[:-7])

                await self.client.send_message(self.falsepos_chan, notification)
                message.mark_as_read()
            else:
                LOG.info('[Inbox] Announcing inbox message.')
                notification = format_inbox_message(message)
                await self.client.send_message(self.inbox_chan, notification)
                message.mark_as_read()

    # ======================================================

    async def _process_oc_stream(self, multi):
        LOG.debug('[OC] Checking for new %s OC submissions...', multi)
        oc_multi = self.reddit.get_multireddit(settings.MULTIREDDIT_USER, multi)

        if self.oc_stream_placeholder.get(multi, None) is None:
            limit = 25
        else:
            limit = round(25 * RUN_INTERVAL)

        oc_stream = list(oc_multi.get_new(limit=limit,
                                          place_holder=self.oc_stream_placeholder.get(multi, None)))
        LOG.debug('[OC] len(oc_stream)=%s oc_stream_placeholder=%s',
                  len(oc_stream), self.oc_stream_placeholder.get(multi, None))

        x = 0
        for submission in oc_stream:
            x += 1
            if submission.id == self.last_oc_id.get(multi, None):
                LOG.debug(
                    '[OC] Found last announced %s OC; stopping processing', multi)
                break

            elif submission.id == self.oc_stream_placeholder.get(multi, None):
                LOG.debug(
                    '[OC] Found start of last %s stream; stopping processing', multi)
                break

            elif submission.author.name.lower() != settings.USERNAME:
                self.last_oc_id[multi] = submission.id
                LOG.info('[OC] OC Post from /u/%s found: %s',
                         submission.author.name, submission.permalink)

                await self.client.send_message(self.oc_chan,
                                               '---\n**New __OC__** by **/u/{}**:\r\n{}'.format(
                                                   submission.author.name, submission.permalink))

        self.oc_stream_placeholder[multi] = oc_stream[0].id

        self.count_oc += x
        LOG.info('[OC] Proccessed %s %s items', x, multi)
    # ======================================================

    async def _process_github_events(self):

        repo = self.ghub.repository(
            settings.GITHUB_REPO_USER, settings.GITHUB_REPO_NAME)

        max_length = round(10 * RUN_INTERVAL)

        event_queue = deque(maxlen=max_length)

        e_i = repo.iter_events(number=max_length)

        cont_loop = True
        date_max = (datetime.datetime.today() +
                    datetime.timedelta(days=-1)).utctimetuple()

        LOG.debug('[GitHub] Loading events from GitHub...')
        while cont_loop:
            event = e_i.next()

            if event.id == self.last_github_event:
                cont_loop = False
                continue

            self.count_gh_events += 1

            if len(event_queue) == max_length:
                cont_loop = False
                continue

            if event.created_at.utctimetuple() >= date_max:
                if event.type in EVENT_FILTER:
                    event_queue.append(event)

            else:
                cont_loop = False

        LOG.info('[GitHub] New GitHub Events: %s', len(event_queue))

        # All events queued... now send events to channel
        while len(event_queue) > 0:
            event = event_queue.pop()
            if event.type == 'PushEvent':
                LOG.info('[GitHub] Sending new PushEvent...')
                await self.client.send_message(self.github_chan, format_github_push_event(event))

            elif event.type == 'IssuesEvent':
                LOG.info('[GitHub] Sending new IssuesEvent...')
                await self.client.send_message(self.github_chan, format_github_issue_event(event))

            elif event.type == 'IssueCommentEvent':
                LOG.info('[GitHub] Sending new IssueCommentEvent...')
                await self.client.send_message(self.github_chan, format_github_issue_comment(event))

            elif event.type == 'PullRequestEvent':
                await self.client.send_message(self.github_chan, format_github_pull_request(event))

        self.last_github_event = repo.iter_events(number=1).next().id

    # ======================================================

    async def _process_network_modlog(self, multi):
        action_queue = deque(maxlen=25)
        url = 'https://www.reddit.com/user/{}/m/{}/about/log'.format(
            settings.MULTIREDDIT_USER, multi)

        if self.last_modlog_action.get(multi, None) is None:
            limit = 25
        else:
            limit = round(25 * RUN_INTERVAL)

        LOG.debug('[ModLog] Getting %s modlog: limit=%s place_holder=%s',
                  multi, limit, self.last_modlog_action.get(multi, None))

        content = self.reddit.get_content(url, limit=limit,
                                          place_holder=self.last_modlog_action.get(multi, None))

        modlog = list(content)

        LOG.info('[ModLog] Processing %s %s modlog actions...',
                 len(modlog), multi)
        self.count_modlog += len(modlog)

        for entry in [e for e in modlog if e.action in MODLOG_ACTIONS]:

            if entry.id == self.last_modlog_action.get(multi, None):
                LOG.debug(
                    '[ModLog] Found previous %s modlog placeholder entry.', multi)
                break

            else:
                action_queue.append(entry)

        while len(action_queue) > 0:
            entry = action_queue.pop()
            await self._announce_mod_action(entry)

        self.last_modlog_action[multi] = modlog[0].id
        LOG.debug('[ModLog] Finished processing %s modlog.', multi)

    # ------------------------------------

    async def _announce_mod_action(self, entry):
        message = format_mod_action(entry)

        LOG.info('[ModLog] Announcing modlog moderator %s action', entry.action)
        await self.client.send_message(self.mod_chan, message)

    # ------------------------------------

    async def _report_client_stats(self):
        while True:
            await asyncio.sleep(60 * STATS_INTERVAL)

            msg = 'Messages: **{}**\n'.format(self.count_messages) \
                + 'Multireddit posts: **{}**\n'.format(self.count_oc) \
                + 'GitHub Events: **{}**\n'.format(self.count_gh_events) \
                + 'Network Modlog Actions: **{}**\r\n'.format(self.count_modlog)

            self.count_gh_events = 0
            self.count_messages = 0
            self.count_modlog = 0
            self.count_oc = 0

            await self.client.send_message(self.stats_chan, msg)

            x = randint(1, 20)
            if x == 5:
                await self.client.send_message(self.github_chan, "*Bite my shiny, metal ass!*")

    # -------------------------------------

    async def _process_messages(self):
        LOG.debug('[Inbox] Checking for new messages...')
        inbox = list(self.reddit.get_unread(limit=None))
        LOG.info('[Inbox] Unread messages: %s', len(inbox))
        for message in inbox:
            await self._relay_inbox_message(message)

    # ------------------------------------

    async def _run_loop(self):
        while True:
            await self._run_once()
            LOG.info('Sleeping for %s minute(s)...', RUN_INTERVAL)
            await asyncio.sleep(60 * RUN_INTERVAL)

    async def _run_once(self):
        try:
            await self._process_messages()
            await self._process_github_events()
            for multi in settings.MULTIREDDITS:
                await self._process_oc_stream(multi)
                await self._process_network_modlog(multi)

        except HTTPException as ex:
            LOG.error('%s: %s', type(ex), ex)
        except requests.ReadTimeout as ex:
            LOG.error('%s: %s', type(ex), ex)
        except requests.ConnectionError as ex:
            LOG.error('%s: %s', type(ex), ex)
        else:
            LOG.debug('All tasks processed.')

    # ======================================================

    async def on_ready(self):
        """Event that fires once the Discord client has connected to Discord, logged in,
        and is ready to process new commands/events."""

        LOG.info('[Discord] Logged in as %s', self.client.user.name)

        self.inbox_chan = self.client.get_channel(settings.DISCORD_INBOX_CHAN_ID)
        self.falsepos_chan = self.client.get_channel(settings.DISCORD_FALSEPOS_CHAN_ID)
        self.github_chan = self.client.get_channel(settings.DISCORD_GITHUB_CHAN_ID)
        self.oc_chan = self.client.get_channel(settings.DISCORD_OC_CHAN_ID)
        self.mod_chan = self.client.get_channel(settings.DISCORD_MOD_CHAN_ID)
        self.stats_chan = self.client.get_channel(settings.DISCORD_KEEPALIVE_CHAN_ID)

        asyncio.ensure_future(self._report_client_stats(),
                              loop=self.client.loop)

        await self.client.send_message(self.stats_chan, 'Ready: {}'.format(datetime.datetime.now()))

        if self.run_init:
            self.run_init = False
            await self._run_loop()
            LOG.warning("Thread returning from 'await self._run_loop'!")
            self.run_init = True

    # ------------------------------------

    def run(self):
        """Initialize the Discord Bot and begin its processessing loop."""

        while True:
            try:
                LOG.info('[Discord] Starting Discord client...')
                self.client.run(settings.DISCORD_TOKEN)
            except RuntimeError as ex:
                LOG.error('%s: %s', type(ex), ex, exc_info=ex)
            else:
                LOG.warning("Thread returned from 'client.run()' blocking call!")

            sleep(30)
            self._setup_client()
