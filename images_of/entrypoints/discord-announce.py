import praw
import discord
import asyncio
import re
import logging
import images_of

from time import sleep
from discord.ext import commands
from images_of import settings, Reddit

LOG = logging.getLogger(__name__)

# message type mapping
types = {
    't1':'comment',
    't2':'account',
    't3':'link',
    't4':'message',
    't5':'subreddit',
    't6':'award',
    't8':'promocampaign'
}

CLIENT = discord.Client()
client_id = settings.DISCORD_CLIENTID
token = settings.DISCORD_TOKEN

md_link_pattern = '(\[)([^\]()#\n]+)\]\(([^\]()#\n]+)\)'
md_link_re = re.compile(md_link_pattern, flags=re.IGNORECASE)

@CLIENT.event
@asyncio.coroutine 
def on_ready():
    LOG.info('discord.client: on_ready...')
    LOG.info('discord.client: Logged in as {}'.format(CLIENT.user.name))
    
    inbox_id = '183018837883617280'
    inbox_chan = CLIENT.get_channel(inbox_id)
    falsepos_id = '183605928514420736'
    falsepos_chan = CLIENT.get_channel(falsepos_id)

    LOG.info('Logging into reddit...')
    r = Reddit('{} Inbox-to-Discord Relay v0.1 - /u/{}'.format(settings.NETWORK_NAME, settings.USERNAME))
    r.oauth()

    LOG.info('Checking for new messages...')
    for message in r.get_unread(limit=None):

        sleep(1)
        
        if (message.body == 'remove') or ('mod removal' in message.body):    # Don't announce 'remove' replies
            LOG.info('Not announcing message type: "remove"')
            message.mark_as_read()
            continue

        elif 'blacklist me' in message.subject: # Don't announce blacklist requests
            LOG.info('Not announcing message type: "blacklist request"')
            message.mark_as_read()
            continue

        elif (message.author.name == 'AutoModerator') or (message.author.name == 'reddit'):
            message.mark_as_read()
            LOG.info('Not announcing message type: "AutoMod Response"')
            continue

        else:
            LOG.info('Announcing new inbox item type: {}'.format(types[message.name[:2]]))

            
            if 'false positive' in message.body.lower():
                LOG.info('- Announcing false-positive reply...')
                notification = "**New __false-positive__:** {}\n---".format(message.permalink[:-7])
                yield from CLIENT.send_message(falsepos_chan, notification)

            else:
                notification = format_message(message)
                LOG.info('- Announcing inbox message...')
                yield from CLIENT.send_message(inbox_chan, notification)

        message.mark_as_read()


    exit

def format_message(message):
    msg_body = message.body
    msg_body = re.sub('\n\n', '\n', msg_body)
    
    #Strip markdown hyperlinks, append to bottom
    msg_links = md_link_re.findall(msg_body)

    if msg_links:
        msg_body = md_link_re.sub('\g<2>', msg_body)
        msg_body += '\n __*Links:*__\n'
        for m in msg_links:
            msg_body += '- {}\n'.format(m[2])

    notification = "**New __{}__:** \n```\n{}\n```".format(types[message.name[:2]], msg_body)

    #Add permalink for comment replies   
    if message.name[:2] == 't1':
        notification += ('\n**Permalink:** {}\n---'.format(message.permalink))

    return notification


def main():
    global CLIENT
    CLIENT = discord.Client()
    CLIENT.event(on_ready)
    CLIENT.run(token)



if __name__ == '__main__':
    main()


