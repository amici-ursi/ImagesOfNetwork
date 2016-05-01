from images_of import settings, Reddit
from images_of.bot import Bot

def main():
    r = Reddit('{} v6.0 /u/{}'.format(settings.NETWORK_NAME, settings.USERNAME))
    r.oauth()

    b = Bot(r)
    b.run()

if __name__ == '__main__':
    main()
