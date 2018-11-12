import requests
import re
import os
from bs4 import BeautifulSoup
import time
from threading import Thread


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


def setRateLimit(maxPages, waitTime):
    """Assigns values to the RateLimiter

    Args:
        :param maxPages: Max number of pages before being rate-limited
        :param waitTime: Time to wait between visiting max number of pages
    """
    global rl
    rl = RateLimiter(maxPages, waitTime)


# def click(url, tag, *args):
#     """Clicks on given element. Useful for activating pop-ups. Chrome Driver is needed to use
#
#     Args:
#         :param url: url containing the link to the pop-up
#         :param tag: tag of the element that opens the pop-up
#         :param args: optional argument that specifies which element you want to click if multiple contain given tag
#
#     Returns:
#         BeautifulSoup format of html of the page with the pop-up enabled
#     """
#     index = 0 if not args else args[0]
#
#     options = webdriver.ChromeOptions().add_argument('--headless')
#     phantom = webdriver.Chrome(chrome_options=options,
#                                executable_path=createPath(os.getcwd(), 'chromedriver'))
#
#     phantom.get(url)
#     WebDriverWait(phantom, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, tag)))
#     element = phantom.find_elements_by_class_name(tag)[index]
#     phantom.execute_script('arguments[0].click();', element)
#     time.sleep(0.1)  # Time to load pop-up
#     soup = requestHTML(url, phantom.page_source)
#     phantom.close()
#     return soup


def createPath(path, *paths):
    """Helper method to map strings into a path

    :param path: Base path
    :param paths: path extension
    :return: full file path
    """
    return os.path.join(path, *paths)


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
        time.sleep(rl.timeOut)
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


def makeDirectory(appName):
    """Makes directories for apk files and reviews

    :param appName: Name of the application
    :return: File path of the parent directory
    """
    savePath = os.getcwd() + '/'

    tryMakeDir(savePath + 'reviews/' + appName)
    tryMakeDir(savePath + 'apks/' + appName)

    return savePath


def tryMakeDir(savePath):
    """Helper method to make a directory

    :param savePath: File path of the new directory
    """
    try:
        os.mkdir(savePath)
    except OSError:
        print('Failed to create directory %s ' % savePath)
    else:
        print('Successfully created the directory %s ' % savePath)


def downloadApk(apk, savePath):
    """Downloads given apk in the background to reduce time

    :param apk: APK to be downloaded
    :param savePath: Where the apk will be stored
    """
    Thread(target=apkThread, args=(apk, savePath)).start()


def apkThread(apk, savePath):
    """Process to download APK files

    :param apk: APK to be downloaded
    :param savePath: Where to save APK files
    """
    session = requests.Session()
    s = session.get(apk).content
    logToFile(savePath, s, 'wb')


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
