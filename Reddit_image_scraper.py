import praw
import configparser


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


if __name__ == '__main__':

    ClientInfo.id, ClientInfo.secret = get_client_info()

