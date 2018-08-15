import praw
import configparser
import urllib.request

from prawcore.exceptions import Redirect
from prawcore.exceptions import ResponseException
from urllib.error import HTTPError


class ClientInfo:
    id = ''
    secret = ''
    user_agent = 'Reddit_Image_Scraper'


def get_client_info():
    config = configparser.ConfigParser()
    config.read("config.ini")
    id = config["ALPHA"]["client_id"]
    secret = config["ALPHA"]["client_secret"]

    return id, secret


def get_img_urls(sub, li):
    try:
        r = praw.Reddit(client_id=ClientInfo.id, client_secret=ClientInfo.secret, user_agent=ClientInfo.user_agent)
        submissions = r.subreddit(sub).hot(limit=li)

        return [submission.url for submission in submissions]

    except Redirect:
        print("Invalid Subreddit!")
        return 0

    except HTTPError:
        print("Too many Requests. Try again later!")
        return 0

    except ResponseException:
        print("Client info is wrong. Check again.")
        return 0


def download_img(img_url, img_title, filename):
    try:
        print('Downloading ' + img_title + '....')
        urllib.request.urlretrieve(img_url, filename)
        return 1

    except HTTPError:
        print("Too many Requests. Try again later!")
        return 0


if __name__ == '__main__':

    ClientInfo.id, ClientInfo.secret = get_client_info()

    subreddit = input('Enter Subreddit: ')
    num = int(input('Enter Limit: '))
    print()
    url_list = get_img_urls(subreddit, num)
    file_no = 1

    if url_list:

        for url in url_list:

            file_name = 'result/{}.jpg'.format(file_no)
            status = download_img(url, url.split('/')[-1], file_name)

            if not status:
                break

            file_no += 1

    if file_no == num+1:
        print("Successfully Completed!")
