import requests
import re
import os
from bs4 import BeautifulSoup

from time import sleep
from threading import Thread
from boxsdk import DevelopmentClient


class RateLimiter:
    """Limits how often you can query websites given the rate limit factors

    Attributes:
        rate: Stores the max number of pages that can be visited
        waitTime: How long the crawler should wait to keep from being rate-limited
        visited: The number of links visited in the current cycle
    """
    def __init__(self, maxPages, waitTime):
        """Sets rate limit for visiting web pages. Will wait given time when threshold is reached

        Args:
            :param maxPages: The max number of pages that can be visited before the site blocks you
            :param waitTime: The amount of time that should be waited when reaching the max number of pages
        """
        self.rate = maxPages
        self.timeOut = waitTime
        self.visited = 0


# Global variable to keep from rate limiting websites
rl = RateLimiter(0, 0)
client = DevelopmentClient()


def setRateLimit(maxPages, waitTime):
    """Assigns values to the RateLimiter

    Args:
        :param maxPages: Max number of pages before being rate-limited
        :param waitTime: Time to wait between visiting max number of pages
    """
    global rl
    rl = RateLimiter(maxPages, waitTime)


def createPath(basePath, *extensions):
    """Helper method to map strings into a path

    :param basePath: Base path
    :param extensions: path extension
    :return: full file path
    """
    basePath = os.getcwd() if basePath == "HOME" else basePath
    return os.path.join(basePath, *extensions)


def getWorkingDirectory():
    return os.getcwd()


def removeSpecialChars(string):
    """Removes special characters from strings

    :param string: String to be worked on
    :return: Given string with special characters removed
    """
    return re.sub('\W+', ' ', string.lower())


def requestHTML(url, *args):
    """Gets formatted HTML of given url

    :param url:  Url to get the HTML of
    :param args: Optional argument to input pure HTML
    :return: BeautifulSoup format of the url's HTML
    """
    global rl
    rl.visited += 1
    if rl.visited >= rl.rate:
        rl.visited = 0
        sleep(rl.timeOut)
        print("waiting")
    if args:
        return BeautifulSoup(args[0], 'lxml')
    return BeautifulSoup(requests.get(url).content, 'lxml')


def logToFile(outputFile, line, *args):
    """Writes given input to specified file

    :param outputFile: File to be written to
    :param line: What to write into file
    :param args: Optional argument that specifies write options
    """
    if args:
        options = args[0]
    else:
        options = 'a'

    f = open(outputFile, options)
    f.write(line)
    f.close()


def downloadApk(apkDownloadLink, savePath, fileName, directoryName):
    """Downloads given apk in the background to reduce time

    :param apkDownloadLink: APK to be downloaded
    :param savePath: Where the apk will be stored
    :param fileName:
    :param directoryName:
    """
    Thread(target=apkThread, args=(apkDownloadLink, savePath, fileName, directoryName)).start()


def apkThread(apkDownloadLink, savePath, fileName, directoryName):
    """Process to download APK files

    :param apkDownloadLink: APK to be downloaded
    :param savePath: Where to save APK files
    :param fileName:
    :param directoryName:
    """
    sleep(0.5)
    session = requests.Session()
    s = session.get(apkDownloadLink).content
    logToFile(savePath, s, 'wb')
    try:
        uploadAPK(savePath, fileName, directoryName)
        os.remove(savePath)
    except:
        os.remove(savePath)


def writeOutput(destination, *args, **kwargs):
    """Writes Output into given destination

    :param destination: Where to write to
    :param args: Optional argument that specifies write type
    :param kwargs: Information to be writen in the format of 'key: value'
    """
    if destination == 'DB':
        # TODO Change to DB location
        destination = 'ApkPure Crawler Output.txt'

    if args:
        logToFile(destination, '', args[0])
    else:
        logToFile(destination, '', 'w')

    for key, value in kwargs.items():
        logToFile(destination, key + ': ' + value.__str__() + '\n')


def uploadAPK(filePath, fileName):
    folder_id = '54833153949'
    client.folder(folder_id).upload(filePath, fileName)
