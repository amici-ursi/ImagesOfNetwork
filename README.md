# ImagesOfNetwork

Tools for managing the ImagesOfNetwork on reddit

# Getting Started

Laying out the steps for getting it running here.

### Reddit

These tools make extensive use of the Reddit API (duh), so lets make sure that
that's all set up first. Head on over to your
[apps preferences](https://www.reddit.com/prefs/apps/) and click the
button to create a developer app. You should see 5 fields here.

- name: Anything you want, you're the only one that's going to see it.
- radio buttons: Make sure `script` is selected
- description: Again just for you. You can even leave it blank.
- about url: ditto
- redirect url: This one's important for setting up OAuth. The suggested
  path for these tools is `http://127.0.0.1:65010/authorize_callback`

Click create app, and note the series of digits under "personal use script".
that's your client id. Also, you'll need to keep tabs on the value of `secret`.

### local\_settings.py

Now that we've got reddit ready for us, we need to configure our workspace.
Go ahead and `cp images_of/local_settings.py.example images_of/local_settings.py`.
This is where you'll keep all of your private settings at. Put your username and
password in the appropriate fields, as well as the client-id and client-secret
we got from reddit earlier. If you used a different redirect uri, you'll also need
to add a field for that (REDIRECT\_URI).

### Install package

Now that reddit and the images\_of package are configured, it's time to install.

```
$ virtualenv -v venv-imagesof -p python3
$ source venv-imagesof/bin/activate
$ python setup.py install
```

NOTE: If you're developing rather than deploying, go ahead and use `python setup.py develop`
instead. That way, as you make changes to the source, they'll get picked up as you go.

### OAuth

Reddit knows about our scripts, our scripts know how to talk to reddit, but they don't
actually have permission to do that just yet. Fortunately for you, there's a tool to make
it easy, and you've already installed it. just run

```
ion_setup_oauth
```

It'll send you reddit asking for all the permissions we need, and start a little
web server locally to collect what we need to get going. After you've accepted the
request on reddit, you can go ahead and close out of the browser, we're done with it.
The script should print out a line that looks something like

```
REFRESH_TOKEN = '56208746x-eC0VB-j2J4T9JoD91xNqclWmGk'
```

Copy that line and stick it in your local\_settings.py. The scripts will use it, along
with the other information we got from reddit earlier to prove that it has permission
to operate on your behalf.

### Rock-em Sock-em Robots

We're ready to roll. We've got everything we need installed, all the priveledges
with reddit, and it looks like we're good to go. Let's take a moment here to pat
ourselves on the back. We've done some good work.

Ok, I suppose we should get back to the real work here.

### Network Preparation

If you're working on the ImagesOf network, skip this, it's already done.

Otherwise, this is for you. These scripts follow a model of one central subreddit
forming a model for a bunch of other subreddits. We're going to create a network
of subreddits, and each of those are going to copy settings from the master.

Go ahead and create your master subreddit. Set it up the way you want. Privacy
settings, flairs, you name it, the basic settings, at least, will all be copied
over when we start making the *real* subs in our netowrk. Just not wiki pages.
They're handled separately, mostly for moderation purposes.

Make sure you at least create the wiki pages 'userblacklist' and 'subredditblacklist'.
You don't have to put anything in them if you don't want, but they need to be there.
If you do want to blacklist some things off the bat, each should contain a list of
users or subreddits, prefixed by /u/ or /r/, one per line.

Great, we've got something to work off of now. Let's move on.

### Network Expansion

Adding new subreddits to the network should be a fairly simple process. We have
A nice simple script to do the job for us. It assumes that our network name is a
prefix, so if that's not what you want, you'll need to make some code adjustments.
Otherwise, here's the command:

```
ion_expand Topic
```

Now watch it work it's magic. When it's done, you should have a nice, all prepared
subreddit called NetworkNameTopic.

If you're nervous about automagically creating subreddits, you can take a look at
what it's going to do by using the `--dry-run flag`. We won't hit reddit, but it
should at least give you an idea of what's going to happen.

Now we probably want to do something with it. It's time to move back to our settings
file. In settings.py, you'll find a `SLAVE_SUBS` settings. Put your new subreddit
there, with all the configuration you need. There's a template to give you an idea
of how things work.

Note: reddit only allows subreddit creation once every 10 minutes or so. Don't get
too excited, take your time. Maybe use the time between creations to make sure
everything looks right. If we didn't copy something right, let us know.

### Running The Bot

We have credentials, we have a network, now let's start copying posts!

```
ion_bot
```

That's really all there is to it. Everything should be set up already. Maybe keep
an eye on it amd make sure what it's doing is sane, but we should be in business.

### Supervisord

Ok, ok, so nothing's perfect. We want to monitor our process so that if the bot
fails, we can prop it back up again. `supervisord` is a sane choice. Make sure
it's installed on your machine (excercise left up to the reader). Here's a little
bit of configuration to get you started, assuming you went ahead and used the
virtualenv as instructed.

```
[group:ion]
programs=ion_bot
directory=/path/to/ImagesOfNetwork

[program:ion_bot]
command=/path/to/ImagesOfNetwork/venv-imagesof/bin/ion_bot
stderr_logfile=/var/log/ion_bot.log
```

Replace /path/to with the appropriate path, of course. Make sure supervisord
is set up and running. You can then use `supervisorctl` to check on the status
of the daemon, and see what we're logging in the specified logfile.
