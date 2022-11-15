import os
import sys
import praw
import configparser
import urllib.request
import argparse
from argparse import RawTextHelpFormatter

from prawcore.exceptions import Redirect
from prawcore.exceptions import ResponseException
from urllib.error import HTTPError

from threading import Thread


# Globals
dw_results = {}
debug = False


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


def save_list(img_url_list, subreddit):
    link_file = 'result/{}.txt'.format(subreddit)
    for img_url in img_url_list:
        file = open(link_file, 'a')
        file.write('{} \n'.format(img_url))
        file.close()

    return link_file


def delete_img_list(link_file_name):
    os.remove(link_file_name)


def is_img_link(img_link):
    ext = img_link[-4:].lower()
    if ext == '.jpg' or ext == '.png' or ext == '.gif':
        return True
    else:
        return False


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


def download_img(subreddit, img_url, img_title, filename):
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)
    try:
        if debug:
            print('['+subreddit+'] Downloading ' + filename + '....')
        urllib.request.urlretrieve(img_url, filename)
        dw_results[subreddit].append(1)
        return 1

    except HTTPError:
        print("Too many Requests. Try again later!")
        return 0
    except Exception as e:
        print( str(e) )
        return 0


def read_img_links(subreddit, link_file):
    with open(link_file) as f:
        links = f.readlines()

    links = [x.strip() for x in links]
    download_count = 0

    dw_threads = []
    for link in links:
        if not is_img_link(link):
            continue

        file_name = link.split('/')[-1]

        if not file_name:
            continue

        file_path = 'result/{}'.format(subreddit)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        file_loc = '{}/{}'.format(file_path, file_name)

        t = Thread(target=download_img, args=(subreddit, link, file_name, file_loc))
        dw_threads.append(t)
        t.start()
        download_count += 1
    
    # wait for the threads to complete
    for thread in dw_threads:
        thread.join()

    return download_count, 1

def process_subreddit(subreddit, num=10):
    print("Processing: {}".format(subreddit))
    url_list = get_img_urls(subreddit, num)
    file_no = 1

    if url_list:

        link_file = save_list(url_list, subreddit)
        count, status = read_img_links(subreddit, link_file)

        count = len(dw_results[subreddit])

        if status == 1:
            print('\n[{}] Download Complete\n{} - Images Downloaded\n{} - Posts Ignored'.format(subreddit, count, num - count))
        elif status == 0:
            print('\n[{}] Download Incomplete\n{} - Images Downloaded'.format(subreddit, count))

    delete_img_list(link_file)


def read_subreddit_from_file_list(limit):
    subreddit_file = "subreddit.txt"
    if os.path.exists(subreddit_file):
        with open(subreddit_file, 'r', encoding="utf8") as reader:
            multthread_processing(reader.readlines())

def multthread_processing(r_list):
    threads = []
    for subreddit in r_list:
        subreddit = subreddit.strip()
        if not subreddit:
            continue

        dw_results[subreddit] = []
        t = Thread(target=process_subreddit, args=(subreddit, limit))
        threads.append(t)
        t.start()
    
    # wait for the threads to complete
    for thread in threads:
        thread.join()


if __name__ == '__main__':

    ClientInfo.id, ClientInfo.secret = get_client_info()

    about = '''
Download images from Reddit community.
There are 3 ways to use this script:

   1. You can create a file, in root dir, called 'subreddit.txt' and save your community names, one per line, to download its images.
   2. You can pass the communities names with -r param. 
         Like -r XXX YYY - XXX and YYY are communties names
   3. You can use the iterative mode with -i param. 
         We'll ask the subreddit and the hot limit
    '''

    parser = argparse.ArgumentParser(prog=sys.argv[0], description=about, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-r', '--subreddit', action='store', nargs='*', dest='subreddit', default=[], help='subreddit community name without "r/"')
    parser.add_argument('-l', '--limit', action='store', nargs='*', dest='limit', default=[10], help='limit value for use in hot() method - number of images to download')
    parser.add_argument('-d', '--debug', action='store_true', default=False, help='Debug messages')
    parser.add_argument('-i', '--iterative', action='store_true', default=False, help='Iterative mode. Will ask for subreddit and limit')
    
    params = parser.parse_args()
    limit = int(params.limit[0])
    debug = params.debug

    print("#######################################################")
    print("#                Reddit_Image_Scraper                 #")
    print("#-----------------------------------------------------#")
    print("# improoved by: eneias.com                            #")
    print("#######################################################\n")
    print(" >>> subreddit: " + ", ".join(params.subreddit) )
    print(" >>> limit: "     + str(params.limit[0]) )
    print(" >>> iterative: " + str(params.iterative) )
    print(" >>> debug: "     + str(debug) )
    print()


    if params.iterative:
        subreddit = input('Enter Subreddit: ')
        num = int(input('Enter Limit: '))    
        print()
        dw_results[subreddit] = []
        process_subreddit(subreddit, num)
        exit()

    if len(params.subreddit) == 0:
        read_subreddit_from_file_list(limit)
    else:
        multthread_processing(params.subreddit)
    
    print(" >>> done. ")