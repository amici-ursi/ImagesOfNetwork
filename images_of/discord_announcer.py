import asyncio
import datetime
import logging
import re
from collections import deque
import requests
import discord
import github3
from praw.errors import HTTPException
from images_of import settings


RETRY_MINUTES = 2
LOG = logging.getLogger(__name__)

# message type mapping
TYPES = {
    't1':'comment',
    't2':'account',
    't3':'link',
    't4':'message',
    't5':'subreddit',
    't6':'award',
    't8':'promocampaign'
}
MODLOG_ACTIONS = ['invitemoderator', 'acceptmoderatorinvite', 'removemoderator']
EVENT_FILTER = ['IssuesEvent', 'PullRequestEvent', 'PushEvent']
#edited, unlabeled, unassigned, assigned, labeled
ISSUE_ACTION_FILTER = ["opened", "closed", "reopened"]
PULL_REQUEST_ACTION_FILTER = ["opened", "edited", "closed", "reopened", "synchronize"]


CLIENT = discord.Client()

CLIENT_ID = settings.DISCORD_CLIENTID
TOKEN = settings.DISCORD_TOKEN

#Regex pattern for identifying and stripping out markdown links
MD_LINK_PATTERN = r'(\[)([^\]()#\n]+)\]\(([^\]()#\n]+)\)'
MD_LINK_RE = re.compile(MD_LINK_PATTERN, flags=re.IGNORECASE)

class DiscordBot:
    """Discord Announcer Bot to relay important and relevant network information to
    designated Discord channels on regular intervals."""
    def __init__(self, reddit):
        self.reddit = reddit
        self.keep_alive_time = datetime.datetime.now()

        global CLIENT
        CLIENT.event(self.on_ready)

        self.last_oc_id = None
        self.oc_stream_placeholder = None
        self.last_modlog_action = None

        self.count_messages = 0
        self.count_oc = 0
        self.count_gh_events = 0
        self.count_modlog = 0

        self.ghub = github3.login(token=settings.GITHUB_OAUTH_TOKEN)
        repo = self.ghub.repository(settings.GITHUB_REPO_USER, settings.GITHUB_REPO_NAME)
        self.last_github_event = repo.iter_events(number=1).next().id

    ## ======================================================

    async def _relay_inbox_message(self, message):

        self.count_messages += 1

        # Determine if it's a message that we do NOT want to relay...
        if self._is_relayable_message(message):

            if 'false positive' in message.body.lower():
                LOG.info('[Inbox] Announcing false-positive reply.')
                notification = "New __false-positive__ report from **/u/{}**:\r\n{}\r\n ".format(
                    message.author.name, message.permalink[:-7])

                await CLIENT.send_message(FALSEPOS_CHAN, notification)
                message.mark_as_read()
            else:
                LOG.info('[Inbox] Announcing inbox message.')
                notification = self._format_message(message)
                await CLIENT.send_message(INBOX_CHAN, notification)
                message.mark_as_read()


    ##------------------------------------

    @staticmethod
    def _is_relayable_message(message):
        """
        Determines if an inbox message is a type of message that should or should not be relayed
        to Discord. Does not relay mod removal or remove replies, blacklist requests, or messages
        from AutoModerator/reddit itself.
        """
        #only matching remove exactly
        if (message.body == 'remove') or ('mod removal' in message.body):
            # Don't announce 'remove' or 'mod removal' replies
            message.mark_as_read()
            LOG.info('[Inbox] Not announcing message type: "remove"/"mod removal"')
            return False

        elif 'blacklist me' in message.subject:
            # Don't announce blacklist requests
            message.mark_as_read()
            LOG.info('[Inbox] Not announcing message type: "blacklist request"')
            return False

        elif (message.author.name == 'AutoModerator') or (message.author.name == 'reddit'):
            # Don't announce AutoModerator or reddit messages
            message.mark_as_read()
            LOG.info('[Inbox] Not announcing message type: "AutoMod Response"')
            return False

        else:
            return True

    ##------------------------------------

    @staticmethod
    def _format_message(message):
        msg_body = message.body
        msg_body = re.sub('\n\n', '\n', msg_body)

        #Strip markdown hyperlinks, append to bottom
        msg_links = MD_LINK_RE.findall(msg_body)

        if msg_links:
            msg_body = MD_LINK_RE.sub(r'\g<2>', msg_body)
            msg_body += '\r\n __*Links:*__\n'
            i = 0
            for msg in msg_links:
                i += 1
                msg_body += '{}: {}\n'.format(i, msg[2])

        msg_type = TYPES[message.name[:2]]
        if msg_type == 'comment':
            if message.is_root:
                msg_type = 'post comment'
            else:
                msg_type = 'comment reply'

        notification = ("New __{}__ from **/u/{}**: \n```\n{}\n```".format(
            msg_type, message.author.name, msg_body))

        #Add permalink for comment replies
        if message.name[:2] == 't1':
            notification += ('\n**Permalink:** {}?context=10\r\n '.format(message.permalink))

        return notification


    ## ======================================================

    async def _process_oc_stream(self):
        oc_multi = self.reddit.get_multireddit(settings.MULTI_OWNER, settings.MULTIREDDIT)

        if self.oc_stream_placeholder is None:
            limit = 125
        else:
            limit = round(25 * RETRY_MINUTES)

        oc_stream = list(oc_multi.get_new(limit=limit, place_holder=self.oc_stream_placeholder))
        LOG.debug('[OC] len(oc_stream)=%s oc_stream_placeholder=%s',
                  len(oc_stream), self.oc_stream_placeholder)

        x = 0
        for submission in oc_stream:
            x += 1
            if submission.id == self.last_oc_id:
                LOG.debug('[OC] Found last announced OC; stopping processing')
                break

            elif submission.id == self.oc_stream_placeholder:
                LOG.debug('[OC] Found start of last stream; stopping processing')
                break

            else:
                if submission.author.name.lower() != settings.USERNAME:

                    self.last_oc_id = submission.id

                    LOG.info('[OC] OC Post from /u/%s found: %s',
                             submission.author.name, submission.permalink)

                    await CLIENT.send_message(OC_CHAN,
                                              '---\n**New __OC__** by **/u/{}**:\r\n{}'.format(
                                                  submission.author.name, submission.permalink))


        self.oc_stream_placeholder = oc_stream[0].id

        self.count_oc += x
        LOG.info('[OC] Proccessed %s items', x)
    ## ======================================================

    async def _process_github_events(self):

        repo = self.ghub.repository(settings.GITHUB_REPO_USER, settings.GITHUB_REPO_NAME)

        max_length = (10 * RETRY_MINUTES)

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


        LOG.info('[GitHub] New GitHub Events: %s', len(event_queue))

        #All events queued... now send events to channel
        while len(event_queue) > 0:
            event = event_queue.pop()
            if event.type == 'PushEvent':
                LOG.info('[GitHub] Sending new PushEvent...')
                await CLIENT.send_message(GITHUB_CHAN, self.format_push_event(event))

            elif event.type == 'IssuesEvent':
                LOG.info('[GitHub] Sending new IssuesEvent...')
                await CLIENT.send_message(GITHUB_CHAN, self.format_issue_event(event))

            elif event.type == 'PullRequestEvent':
                pass

        self.last_github_event = repo.iter_events(number=1).next().id


    ##------------------------------------

    @staticmethod
    def format_push_event(event):
        """Takes a GitHub PushEvent and returns a markdown-formatted message
        that can be relayed to the Discord channel."""

        push_message = 'New Push to branch `{}` by **{}**:\r\n'.format(
            event.payload['ref'].replace('refs/heads/', ''), event.actor.login)

        for com in event.payload['commits']:
            desc = '\nCommit `{}` by `{}`:\n'.format(com['sha'], com['author']['name'])
            desc += '```\n{}```\n'.format(com['message'])
            desc += 'https://github.com/amici-ursi/ImagesOfNetwork/commit/{}'.format(com['sha'])
            #desc += '\n---\n'
            push_message += desc

        push_message += '\r\n---'
        return push_message


    ##------------------------------------

    @staticmethod
    def format_issue_event(event):
        """Takes a GitHub IssuesEvent and returns a markdown-formatted message
        that can be relayed to the Discord channel."""

        action = event.payload['action']
        if action in ISSUE_ACTION_FILTER:

            title = event.payload['issue'].title
            user = event.actor.login
            url = event.payload['issue'].html_url

            desc = 'GitHub Issue __{}__ by **{}**:\n```\n{}\n```\r'.format(action, user, title)
            desc += '\n**Link**: {}\n'.format(url)

            return desc


    ##------------------------------------

    @staticmethod
    def format_pull_request_event(event):
        """
        If the action is "closed" and the merged key is false, the pull request was closed
        with unmerged commits.
        If the action is "closed" and the merged key is true, the pull request was merged.
        """

        pass


    ## ======================================================

    async def _process_network_modlog(self):
        action_queue = deque(maxlen=25)
        url = 'https://www.reddit.com/user/{}/m/{}/about/log'.format(
            settings.MULTI_OWNER, settings.MULTIREDDIT)

        if self.last_modlog_action is None:
            limit = 100
        else:
            limit = round(25 * RETRY_MINUTES)

        LOG.debug('[ModLog] Getting network modlog: limit=%s place_holder=%s',
                  limit, self.last_modlog_action)
        content = self.reddit.get_content(url, limit=limit, place_holder=self.last_modlog_action)

        modlog = list(content)

        LOG.info('[ModLog] Processing %s modlog actions...', len(modlog))
        self.count_modlog += len(modlog)

        for entry in [e for e in modlog if e.action in MODLOG_ACTIONS]:

            if entry.id == self.last_modlog_action:
                LOG.debug('[ModLog] Found previous modlog placeholder entry.')
                break

            else:
                action_queue.append(entry)

        while len(action_queue) > 0:
            entry = action_queue.pop()
            await self._announce_mod_action(entry)

        self.last_modlog_action = modlog[0].id
        LOG.debug('[ModLog] Finished processing network modlog.')


    ##------------------------------------

    async def _announce_mod_action(self, entry):
        mod_action = entry.action
        mod = '/u/{}'.format(entry.mod)
        sub = '/r/{}'.format(entry.subreddit.display_name)
        target = '/u/{}'.format(entry.target_author)

        message = '__*{} Moderator Update*__:\r\n'.format(settings.NETWORK_NAME)
        message += '```\n{} has '.format(mod)

        if mod_action == 'invitemoderator':
            message += 'invited {} to be a moderator'.format(target)

        elif mod_action == 'acceptmoderatorinvite':
            message += 'accepted a moderator invite'

        elif mod_action == 'removemoderator':
            message += 'removed {} as a moderator'.format(target)

        message += ' for {}'.format(sub)
        message += '\n```\r\n '

        LOG.info('[ModLog] Announcing modlog moderator %s action', entry.action)
        await CLIENT.send_message(MOD_CHAN, message)

    ## ======================================================

    @CLIENT.event
    async def on_ready(self):
        """Event that fires once the Discord CLIENT has connected to Discord, logged in,
        and is ready to process new commands/events."""

        LOG.info('[Discord] Logged in as %s', CLIENT.user.name)

        global INBOX_CHAN
        global FALSEPOS_CHAN
        global GITHUB_CHAN
        global OC_CHAN
        global MOD_CHAN
        global KEEPALIVE_CHAN

        INBOX_CHAN = CLIENT.get_channel(settings.DISCORD_INBOX_CHAN_ID)
        FALSEPOS_CHAN = CLIENT.get_channel(settings.DISCORD_FALSEPOS_CHAN_ID)
        GITHUB_CHAN = CLIENT.get_channel(settings.DISCORD_GITHUB_CHAN_ID)
        OC_CHAN = CLIENT.get_channel(settings.DISCORD_OC_CHAN_ID)
        MOD_CHAN = CLIENT.get_channel(settings.DISCORD_MOD_CHAN_ID)
        KEEPALIVE_CHAN = CLIENT.get_channel(settings.DISCORD_KEEPALIVE_CHAN_ID)

        await CLIENT.send_message(KEEPALIVE_CHAN, 'Ready : {}'.format(datetime.datetime.now()))

        await self._run()
        LOG.warning("Thread returning from 'await self._run'!")

    ##------------------------------------

    async def _client_keepalive(self):

        if (self.keep_alive_time + datetime.timedelta(minutes=15)) <= datetime.datetime.now():
            msg = 'Messages: **{}**\n'.format(self.count_messages)
            msg += 'Multireddit posts: **{}**\n'.format(self.count_oc)
            msg += 'GitHub Events: **{}**\n'.format(self.count_gh_events)
            msg += 'Network Modlog Actions: **{}**\r\n'.format(self.count_modlog)

            await CLIENT.send_message(KEEPALIVE_CHAN, msg)

            self.keep_alive_time = datetime.datetime.now()
            self.count_gh_events = 0
            self.count_messages = 0
            self.count_modlog = 0
            self.count_oc = 0

    ##------------------------------------

    @asyncio.coroutine
    async def _run(self):
        while True:
            try:

                LOG.debug('[Inbox] Checking for new messages...')
                inbox = list(self.reddit.get_unread(limit=None))
                LOG.info('[Inbox] Unread messages: %s', len(inbox))
                for message in inbox:
                    await self._relay_inbox_message(message)

                LOG.debug('[OC] Checking for new OC submissions...')
                await self._process_oc_stream()

                # Check GitHub RSS feed....
                await self._process_github_events()

                #Process network subreddit mod-log for new events...
                await self._process_network_modlog()

                await self._client_keepalive()

            except HTTPException as ex:
                LOG.error('%s: %s', type(ex), ex)
            except requests.ReadTimeout as ex:
                LOG.error('%s: %s', type(ex), ex)
            except requests.ConnectionError as ex:
                LOG.error('%s: %s', type(ex), ex)
            else:
                LOG.debug('All tasks processed.')

            LOG.info('Sleeping for %s minute(s)...', RETRY_MINUTES)
            await asyncio.sleep((60 * RETRY_MINUTES) / 2)
            await asyncio.sleep((60 * RETRY_MINUTES) / 2)

    ##------------------------------------

    def run(self):
        """Initialized the Discord Bot and begin its processessing loop."""
        #e = asyncio.get_event_loop()
        #e.set_debug(True)

        while True:
            global CLIENT
            try:
                LOG.info('[Discord] Starting Discord client...')
                CLIENT.run(TOKEN)
            except RuntimeError as ex:
                LOG.error('%s: %s', type(ex), ex)
            else:
                LOG.warning("Thread returned from 'CLIENT.run()' blocking call!")
                asyncio.sleep(30)

                CLIENT = discord.Client()


