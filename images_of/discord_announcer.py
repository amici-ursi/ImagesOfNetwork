"""
Discord Announcer Bot to relay important and relevant network information to
    designated Discord channels on regular intervals.
"""
import asyncio
from collections import deque
from random import randint
import datetime
from time import sleep

import discord
import github3
from praw.errors import HTTPException
import requests

from images_of import settings
from images_of.logging import getLogger
from images_of.discord_formatters import is_relayable_message, format_inbox_message
from images_of.discord_formatters import format_github_issue_comment, format_github_issue_event
from images_of.discord_formatters import format_github_pull_request, format_github_push_event
from images_of.discord_formatters import format_mod_action

RUN_INTERVAL = 2  # minutes
STATS_INTERVAL = 15  # minutes
LOG = getLogger(__name__)

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
EVENT_FILTER = ['IssuesEvent', 'PullRequestEvent', 'PushEvent', 'IssueCommentEvent']
ISSUE_ACTION_FILTER = ["opened", "closed", "reopened", "unlabeled",
                       "unassigned", "assigned", "labeled"]
PULL_REQUEST_ACTION_FILTER = ["opened", "edited", "closed", "reopened", "synchronize"]


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
        repo = self.ghub.repository(settings.GITHUB_REPO_USER, settings.GITHUB_REPO_NAME)
        self.last_github_event = repo.iter_events(number=1).next().id

    def _setup_client(self):
        #loop = asyncio.get_event_loop()
        #loop.slow_callback_duration = 10
        self.client = discord.Client()
        self.client.event(self.on_ready)

    # ======================================================

    async def _relay_inbox_message(self, message):
        # Determine if it's a message that we do NOT want to relay...
        if is_relayable_message(message):
            self.count_messages += 1

            if 'false positive' in message.body.lower() and self.settings.DO_FALSEPOS:
                LOG.info('[Inbox] Announcing false-positive reply.')
                notification = "New __false-positive__ report from **/u/{}**:\r\n{}\r\n ".format(
                    message.author.name, message.permalink[:-7])

                await self.client.send_message(self.falsepos_chan, notification)
                message.mark_as_read()

            elif self.settings.DO_INBOX:
                LOG.info('[Inbox] Announcing inbox message.')
                notification = format_inbox_message(message)
                await self.client.send_message(self.inbox_chan, notification)
                message.mark_as_read()

    # ======================================================

    async def _process_oc_stream(self, multi):
        LOG.debug('[OC] Checking for new {} OC submissions...', multi)
        oc_multi = self.reddit.get_multireddit(settings.MULTIREDDIT_USER, multi)

        if self.oc_stream_placeholder.get(multi, None) is None:
            limit = 25
        else:
            limit = round(40 * RUN_INTERVAL)

        oc_stream = list(oc_multi.get_new(limit=limit,
                                          place_holder=self.oc_stream_placeholder.get(multi, None)))
        LOG.debug('[OC] len(oc_stream)={} oc_stream_placeholder={}',
                  len(oc_stream), self.oc_stream_placeholder.get(multi, None))

        x = 0
        for submission in oc_stream:
            x += 1
            if submission.id == self.last_oc_id.get(multi, None):
                LOG.debug('[OC] Found last announced {} OC; stopping processing', multi)
                break

            elif submission.id == self.oc_stream_placeholder.get(multi, None):
                LOG.debug('[OC] Found start of last {} stream; stopping processing', multi)
                break

            elif submission.author.name.lower() != settings.USERNAME:
                self.last_oc_id[multi] = submission.id
                LOG.info('[OC] OC Post from /u/{} found: {}',
                         submission.author.name, submission.permalink)

                await self.client.send_message(self.oc_chan,
                                               '---\nNew __OC__ by ``/u/{}``:\r\n{}'.format(
                                                   submission.author.name, submission.permalink))

        self.oc_stream_placeholder[multi] = oc_stream[0].id

        self.count_oc += x
        LOG.info('[OC] Proccessed {} {} items', x, multi)
    # ======================================================

    async def _process_github_events(self):

        repo = self.ghub.repository(settings.GITHUB_REPO_USER, settings.GITHUB_REPO_NAME)

        max_length = round(20 * RUN_INTERVAL)

        event_queue = deque(maxlen=max_length)

        e_i = repo.iter_events(number=max_length)

        cont_loop = True
        date_max = (datetime.datetime.today() + datetime.timedelta(days=-1)).utctimetuple()

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

        LOG.info('[GitHub] New GitHub Events: {}', len(event_queue))

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
            limit = 50
        else:
            limit = round(50 * RUN_INTERVAL)

        LOG.debug('[ModLog] Getting {} modlog: limit={} place_holder={}',
                  multi, limit, self.last_modlog_action.get(multi, None))

        content = self.reddit.get_content(url, limit=limit,
                                          place_holder=self.last_modlog_action.get(multi, None))

        modlog = list(content)

        LOG.info('[ModLog] Processing {} {} modlog actions...', len(modlog), multi)
        self.count_modlog += len(modlog)

        for entry in [e for e in modlog if e.action in MODLOG_ACTIONS]:

            if entry.id == self.last_modlog_action.get(multi, None):
                LOG.debug('[ModLog] Found previous {} modlog placeholder entry.', multi)
                break

            else:
                action_queue.append(entry)

        while len(action_queue) > 0:
            entry = action_queue.pop()
            await self._announce_mod_action(entry)

        self.last_modlog_action[multi] = modlog[0].id
        LOG.debug('[ModLog] Finished processing {} modlog.', multi)

    # ------------------------------------

    async def _announce_mod_action(self, entry):
        message = format_mod_action(entry)

        LOG.info('[ModLog] Announcing modlog moderator {} action', entry.action)
        await self.client.send_message(self.mod_chan, message)

    # ------------------------------------

    async def _report_client_stats(self):
        while True:
            try:
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

                x = randint(1, 100)
                e_msg = ''
                if x == 30:
                    e_msg = "*I guess if you want children beaten, you have to do it yourself...*"
                elif x == 60:
                    e_msg = "*Hey sexy mama, wanna kill all humans?*"
                elif x == 90:
                    e_msg = "*Bite my shiny, metal ass!*"

                if len(e_msg) > 1:
                    await self.client.send_message(self.github_chan, e_msg)

            except Exception as ex:
                LOG.error('{}: {}', type(ex), ex)

    # -------------------------------------

    async def _process_messages(self):
        LOG.debug('[Inbox] Checking for new messages...')
        inbox = list(self.reddit.get_unread(limit=None))
        LOG.info('[Inbox] Unread messages: {}', len(inbox))
        for message in inbox:
            await self._relay_inbox_message(message)

    # ------------------------------------

    async def _run_loop(self):
        while True:
            try:
                await self._run_once()
            except HTTPException as ex:
                LOG.error('{}: {}', type(ex), ex)
            except Exception as ex:
                LOG.error('{}: {}', type(ex), ex)

            LOG.info('Sleeping for {} minute(s)...', RUN_INTERVAL)
            print()
            await asyncio.sleep(60 * RUN_INTERVAL)


    async def _run_once(self):
        try:
            if self.settings.DO_INBOX or self.settings.DO_FALSEPOS:
                await self._process_messages()
                asyncio.sleep(5)

            if self.settings.DO_GITHUB:
                await self._process_github_events()

            for multi in settings.MULTIREDDITS:
                if self.settings.DO_OC:
                    asyncio.sleep(5)
                    await self._process_oc_stream(multi)

            for multi in settings.MULTIREDDITS + [settings.PARENT_SUB]:
                if self.settings.DO_MODLOG:
                    asyncio.sleep(5)
                    await self._process_network_modlog(multi)

        except HTTPException as ex:
            LOG.error('{}: {}', type(ex), ex)
        except requests.ReadTimeout as ex:
            LOG.error('{}: {}', type(ex), ex)
        except requests.ConnectionError as ex:
            LOG.error('{}: {}', type(ex), ex)
        else:
            LOG.debug('All tasks processed.')

    # ======================================================

    async def on_ready(self):
        """Event that fires once the Discord client has connected to Discord, logged in,
        and is ready to process new commands/events."""

        LOG.info('[Discord] Logged in as {}', self.client.user.name)

        self.inbox_chan = self.client.get_channel(settings.DISCORD_INBOX_CHAN_ID)
        self.falsepos_chan = self.client.get_channel(settings.DISCORD_FALSEPOS_CHAN_ID)
        self.github_chan = self.client.get_channel(settings.DISCORD_GITHUB_CHAN_ID)
        self.oc_chan = self.client.get_channel(settings.DISCORD_OC_CHAN_ID)
        self.mod_chan = self.client.get_channel(settings.DISCORD_MOD_CHAN_ID)
        self.stats_chan = self.client.get_channel(settings.DISCORD_KEEPALIVE_CHAN_ID)

        await self.client.send_message(self.stats_chan, 'Ready: {}'.format(datetime.datetime.now()))

        if self.run_init:
            self.run_init = False
            asyncio.ensure_future(self._report_client_stats(), loop=self.client.loop)
            await self._run_loop()
            LOG.warning("Thread returning from 'await self._run_loop'!")
            self.run_init = True

    # ------------------------------------

    def run(self, botsettings):
        """Initialize the Discord Bot and begin its processessing loop."""

        if botsettings is None:
            botsettings = DiscordBotSettings()

        self.settings = botsettings

        global RUN_INTERVAL
        RUN_INTERVAL = botsettings.RUN_INTERVAL
        global STATS_INTERVAL
        STATS_INTERVAL = botsettings.STATS_INTERVAL

        while True:
            try:
                LOG.info('[Discord] Starting Discord client...')
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self.client.start(settings.DISCORD_TOKEN))
            except RuntimeError as ex:
                LOG.error('{}: {}', type(ex), ex, exc_info=ex)
            except HTTPException as ex:
                LOG.error('{}: {}', type(ex), ex, exc_info=ex)
            else:
                LOG.warning("Thread returned from 'client.run()' blocking call!")

            sleep(30)
            self._setup_client()


class DiscordBotSettings:
    def __init__(self):
        self.DO_GITHUB = True
        self.DO_MODLOG = True
        self.DO_OC = True
        self.DO_INBOX = True
        self.DO_FALSEPOS = True
        self.RUN_INTERVAL = 2
        self.STATS_INTERVAL = 15
