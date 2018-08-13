import praw
import configparser
import urllib.request


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


def get_img_urls(sub):
    r = praw.Reddit(client_id=ClientInfo.id, client_secret=ClientInfo.secret, user_agent=ClientInfo.user_agent)
    submissions = r.subreddit(sub).hot(limit=10)

    return [submission.url for submission in submissions]


def download_img(img_url, img_title, filename):
    print('Downloading ' + img_title + '....')
    urllib.request.urlretrieve(img_url, filename)


if __name__ == '__main__':

    ClientInfo.id, ClientInfo.secret = get_client_info()

    subreddit = input('Enter Subreddit: ')
    print()
    url_list = get_img_urls(subreddit)
    file_no = 1

    for url in url_list:

        file_name = 'result/{}.jpg'.format(file_no)
        download_img(url, url.split('/')[-1], file_name)
        file_no += 1

    print('Done!')


