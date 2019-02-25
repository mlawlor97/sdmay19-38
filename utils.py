import requests
import re
import os
from subprocess import Popen, PIPE, STDOUT, check_call
from bs4 import BeautifulSoup
from pymongo import MongoClient

import json
from time import sleep
from threading import Thread
# from boxsdk import DevelopmentClient

class RateLimiter:
    """Limits how often you can query websites given the rate limit factors

    Attributes:
        rate: Stores the max number of pages that can be visited
        waitTime: How long the crawler should wait to keep from being rate-limited
        visited: The number of links visited in the current cycle
    """
    def __init__(self, maxPages=0, waitTime=0):
        """Sets rate limit for visiting web pages. Will wait given time when threshold is reached

        Args:
            :param maxPages: The max number of pages that can be visited before the site blocks you
            :param waitTime: The amount of time that should be waited when reaching the max number of pages
        """
        self.rate = maxPages
        self.timeOut = waitTime
        self.visited = 0


class MongoConnector:

    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017')
        self.db = self.client.test2
        self.applications = self.db.Applications
        self.versions = self.db.Versions


# Global variable to keep from rate limiting websites
rl = RateLimiter(0, 0)
db = MongoConnector()
# client = DevelopmentClient()


def setRateLimit(maxPages, waitTime):
    """Assigns values to the RateLimiter

    Args:
        :param maxPages: Max number of pages before being rate-limited
        :param waitTime: Time to wait between visiting max number of pages
    """
    global rl
    rl = RateLimiter(maxPages, waitTime)


def createPath(*extensions, basePath=os.getcwd()):
    """Helper method to map strings into a path

    :param extensions: path extension
    :param basePath: Base path
    :return: full file path
    """
    return os.path.join(basePath, *extensions)


def removeSpecialChars(string):
    """Removes special characters from strings

    :param string: String to be worked on
    :return: Given string with special characters removed
    """
    return re.sub(r'\W+', ' ', string.lower())


def requestHTML(url='', *html):
    """Gets formatted HTML of given url

    :param url:  Url to get the HTML of
    :param html: Optional passing of pure HTML
    :return: BeautifulSoup format of the url's HTML
    """
    global rl
    rl.visited += 1
    sleep(1)
    if rl.visited >= rl.rate:
        rl.visited = 0
        sleep(rl.timeOut)
        print("waiting") if rl.rate > 0 else None
    if html:
        return BeautifulSoup(html[0], 'html.parser')
    return BeautifulSoup(requests.get(url).content, 'html.parser')


def logToFile(outputFile, line='', writeType='a'):
    """Writes given input to specified file

    :param outputFile: File to be written to
    :param line: What to write into file
    :param writeType: Optional argument that specifies write options
    """
    f = open(outputFile, writeType)
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
        # uploadAPK(savePath, fileName, directoryName)
        os.remove(savePath)
    except Exception:
        os.remove(savePath)


def writeOutput(destination='DB', writeType='w', dataDict=None):
    """Writes Output into given destination

    :param destination: Where to write to
    :param writeType: Optional argument that specifies write type
    :param dataDict: Information to be writen in the format of 'key: value'
    """
    if destination == 'DB':
        destination = 'ApkPure Crawler Output.txt'

    logToFile(destination, writeType=writeType)
    logToFile(destination, json.dumps(dataDict, indent=4) + '\n')


def writeAppDB(storeName='', appName='', appUrl='', data=None):
    if data is None:
        data = dict({})

    global db
    appDict = {
        "store_id"  : storeName,
        "app_name"  : appName.lower(),
        "app_url"   : appUrl,
        "metadata"  : data
    }
    result = db.applications.insert_one(appDict)
    return result.inserted_id


def writeVersionDB(storeName='', appName='', appId='', version='', data=None):
    if data is None:
        data = dict({})

    global db
    appDict = {
        "store_id"  : storeName,
        "app_name"  : appName,
        "app_id"    : appId,
        "version"   : version,
        "metadata"  : data
    }
    result = db.versions.insert_one(appDict)
    return result.inserted_id

def checkAppDB(appUrl=None):
    global db
    return db.applications.find_one({"app_url": appUrl})

def checkVersionDB(appId, version=None):
    global db
    body = {"app_id": appId, "version": version} if version else {"app_id": appId}
    return list(db.versions.find(body))

# def uploadAPK(filePath, fileName):
    # folder_id = '54833153949'
    # client.folder(folder_id).upload(filePath, fileName)

def getPermissions(apkFilePath, permList=list()):
    p = Popen(['java', '-jar', 'SupportFiles/Permissions.jar', apkFilePath], stdout=PIPE, stderr=STDOUT)
    [permList.append(line.strip().decode('ascii')) for line in p.stdout]
    return permList

def getApkValues(apkFilePath, shaList=list()):
    p1 = Popen(("unzip -p " + apkFilePath + " META-INF/CERT.RSA").split(), stdout=PIPE)
    p = Popen(['keytool', '-printcert'], stdin=p1.stdout, stdout=PIPE)
    stdout, stderr = p.communicate()

    id_dict = dict({})
    for line in stdout.decode('utf-8').split('\n'):
        args = line.split('\t')
        if args.__len__() == 2 and args[0] == "":
            vals = args[1].strip().split()
            type_ = vals[0].rstrip(":")
            if type_ == "MD5" or type_ == "SHA1" or type_ == "SHA256":
                id_dict.update({type_: vals})
    return id_dict

def safeExecute(func, *args, default=None, error=BaseException):
    try:
        return func(*args)
    except error:
        return default