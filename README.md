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

We're off to the races. Well, today, there's a considerable amount of configuration
laying around various scripts that totally need to be changed, but you have all the
information you need to do it now... right?

### Supervisord

Yeah, we should talk about that.
