import praw
import configparser


class ClientInfo:
    id = ''
    secret = ''
    user_agent = 'praw'


def get_client_info():
    config = configparser.ConfigParser()
    config.read("config.ini")
    id = config["ALPHA"]["client_id"]
    secret = config["ALPHA"]["client_secret"]

    return id, secret


def get_img_urls(sub):
    r = praw.Reddit(client_id=ClientInfo.id, client_secret=ClientInfo.secret, user_agent=ClientInfo.user_agent)
    submissions = r.subreddit(sub).hot(limit=10)

    return [submission.url for submission in submissions]


if __name__ == '__main__':

    ClientInfo.id, ClientInfo.secret = get_client_info()

    subreddit = input('Enter Subreddit: ')
    print(get_img_urls(subreddit))
