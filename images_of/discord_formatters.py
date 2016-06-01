"""
Contains the various formatting functions to convert reddit and GitHub objects into
Discord-friendly messages that can be relayed to the appropriate channels.
"""


import re
import logging

from images_of import settings

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

EVENT_FILTER = ['IssuesEvent', 'PullRequestEvent', 'PushEvent', 'IssueCommentEvent']
ISSUE_ACTION_FILTER = ["opened", "closed", "reopened", "unlabeled",
                       "unassigned", "assigned", "labeled"]
PULL_REQUEST_ACTION_FILTER = ["opened", "edited", "closed", "reopened", "synchronize"]

#Regex pattern for identifying and stripping out markdown links
MD_LINK_PATTERN = r'(\[)([^\]()#\n]+)\]\(([^\]()#\n]+)\)'
MD_LINK_RE = re.compile(MD_LINK_PATTERN, flags=re.IGNORECASE)


def is_relayable_message(message):
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

    elif message.subject.lower() == 'please blacklist me':
        # Don't announce blacklist requests
        message.mark_as_read()
        LOG.info('[Inbox] Not announcing message type: "blacklist request"')
        return False

    elif message.author is None:
        return False

    elif (message.author.name == 'AutoModerator') or (message.author.name == 'reddit'):
        # Don't announce AutoModerator or reddit messages
        message.mark_as_read()
        LOG.info('[Inbox] Not announcing message type: "AutoMod Response"')
        return False

    else:
        return True

##------------------------------------

def format_inbox_message(message):
    """
    Formats a reddit Inboxable message to one that can be relayed to Discord
    """
    msg_body = message.body[:1500]
    if len(msg_body) == 1500:
        msg_body += '...'

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

##------------------------------------

def format_github_issue_comment(event):
    """
    Formats a GitHub IssueComment event into a relayable Discord message
    """
    action = event.payload['action']
    if action == 'created':
        url = event.payload['issue'].html_url
        user = event.payload['comment'].user.login
        comment = event.payload['comment'].body[:1500]
        title = event.payload['issue'].title

        desc = 'GitHub Comment by **{}** on Issue `{}`:'.format(user, title)
        desc += '\n```\n{}\n```\n'.format(comment)
        desc += '**Link**: {}\r\n '.format(url)

        return desc

##------------------------------------

def format_github_push_event(event):
    """Takes a GitHub PushEvent and returns a markdown-formatted message
    that can be relayed to the Discord channel."""

    push_message = 'New Push to branch `{}` by **{}**:\r\n'.format(
        event.payload['ref'].replace('refs/heads/', ''), event.actor.login)

    for com in event.payload['commits']:
        desc = '\nCommit `{}` by `{}`:\n'.format(com['sha'][:7], com['author']['name']) \
             + '```\n{}```\n'.format(com['message']) \
             + 'https://github.com/amici-ursi/ImagesOfNetwork/commit/{}'.format(com['sha'])

        push_message += desc

    push_message += '\r\n---'
    return push_message




##------------------------------------

def format_github_issue_event(event):
    """Takes a GitHub IssuesEvent and returns a markdown-formatted message
    that can be relayed to the Discord channel."""

    action = event.payload['action']
    if action in ISSUE_ACTION_FILTER:

        title = event.payload['issue'].title
        user = event.actor.login
        url = event.payload['issue'].html_url

        if (action == "unlabeled") or (action == "labeled"):
            label = event.payload['label']
            desc = '**{}** __{}__ **{}** on  issue `{}`'.format(user, action, label, title)

        elif (action == "unassigned") or (action == "assigned"):
            assignee = event.payload['assignee']
            desc = '**{}** __{}__ `{}` on issue `{}`'.format(user, action, assignee, title)

        else:
            desc = 'GitHub Issue __{}__ by **{}**:\n```\n{}\n```\r'.format(action, user, title)

        desc += '\n**Link**: {}\r\n'.format(url)

        return desc


##------------------------------------

def format_github_pull_request(event):
    """
    If the action is "closed" and the merged key is false, the pull request was closed
    with unmerged commits.
    If the action is "closed" and the merged key is true, the pull request was merged.
    """
    action = event.payload['action']
    pr_number = event.payload['number']
    url = event.payload['pull_request'].html_url
    state = event.payload['pull_request'].state
    title = event.payload['pull_request'].title
    user = event.payload['pull_request']['user'].login
    sender = event.payload['sender'].login
    #merged = event.payload['pull_request'].merged

    ## PR Opened
    if state == 'open':
        mergable = event.payload['pull_request'].mergable
        commits = event.payload['pull_request'].commits
        additions = event.payload['pull_request'].additions
        deletions = event.payload['pull_request'].deletions
        changed_files = event.payload['pull_request'].changed_files

        desc = 'Pull Request #{} __{}__'.format(pr_number, action) \
                + ' by **{}**: `{}`\r\n'.format(sender, title)

        desc_pr_info = 'Mergable: **{}**\n'.format(mergable) \
                        + 'Commits: **{}**\n'.format(commits) \
                        + 'Files Changed: **{}** '.format(changed_files) \
                        + '(**+{}**/**-{}**)\r\n'.format(additions, deletions)

        return desc + desc_pr_info + url

    ## PR Closed; Merged or Rejected?
    elif action == 'closed':

        if event.payload['pull_request'].merged:
            desc = 'Pull Request #{} by **{}** __merged__'.format(pr_number, user) \
                    + ' by **{}**: `{}`\r\n'.format(sender, title)

        else:
            desc = 'Pull Request #{} by **{}** __rejected__'.format(pr_number, user) \
                    + ' by **{}**: `{}`\r\n'.format(sender, title)

        return desc + url


#--------------------

def format_mod_action(entry):
    """
    Formats a moderator invited/added/removed modlog action for Discord
    """

    mod_action = entry.action
    mod = '/u/{}'.format(entry.mod)
    sub = '/r/{}'.format(entry.subreddit.display_name)
    target = '/u/{}'.format(entry.target_author)

    message = '***{}*** **Moderator Update**:\r\n'.format(settings.NETWORK_NAME) \
            + '```\n{} has '.format(mod)

    if mod_action == 'invitemoderator':
        message += 'invited {} to be a moderator'.format(target)

    elif mod_action == 'acceptmoderatorinvite':
        message += 'accepted the moderator invite'

    elif mod_action == 'removemoderator':
        message += 'removed {} as a moderator'.format(target)

    message += ' for {}'.format(sub) \
            + '\n```\r\n '

    return message

#------------------------------








#------------------------------
