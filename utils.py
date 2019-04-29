import requests
import re
import os
from subprocess import Popen, PIPE, STDOUT, check_call
from bs4 import BeautifulSoup
from pymongo import MongoClient

import json
from time import sleep
from threading import Thread
import hashlib


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
        self.reports = self.db.Reports


# Global variable to keep from rate limiting websites
rl = RateLimiter(0, 0)
db = MongoConnector()
# root = "/home/emmettkoz"
root = "~/Desktop/lss" #/research/csafe-mobile/senior-design"
start = os.getcwd()
store = ''


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


def downloadApk(apkDownloadLink, savePath):
    """Downloads given apk in the background to reduce time

    :param apkDownloadLink: APK to be downloaded
    :param savePath: Where the apk will be stored
    :param fileName:
    :param directoryName:
    """
    savePath = os.path.normpath(savePath)
    with requests.get(apkDownloadLink, stream=True) as r:
        with open(savePath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
    return savePath


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


def writeAppDB(storeName='', appName='', appUrl='', appPkg='', data=dict({}), reviewsPath=''):
    """Writes New Application Entry to the DB

    :param storeName: Name of the appStore
    :param appName: Name of the application
    :param appUrl: Url of the application
    :param data: A dictionary of all the metadata being collected  
    """
    if data is None:
        data = dict({})

    global db
    appDict = {
        "store_id": storeName,
        "app_name": appName.lower(),
        "app_url": appUrl,
        "app_package": appPkg,
        "metadata": data,
        "reviews_path": reviewsPath
    }
    result = db.applications.insert_one(appDict)
    return result.inserted_id


def writeVersionDB(storeName='', appName='', appId='', version='', data=None, filePath=''):
    if data is None:
        data = dict({})

    global db
    if filePath:
        filePath = os.path.normpath(filePath)
        apkVals = dict({
            "extracted": getApkValues(filePath),
            "calculated": genHashValues(filePath)
        })
        existing = db.versions.find_one(
            {"apk_info.calculated": apkVals.get("calculated")})

        writeReportDB(apkVals['extracted'], appId)

        data.update({'file_size' : convert_bytes(os.path.getsize(filePath))})
        data.update({'permissions' : getPermissions(filePath)})
        if existing:
            os.remove(filePath)
            filePath = existing.get("apk_location")
        else:
            filePath = filePath[filePath.index('lss') + 3:]
    else:
        apkVals = None

    appDict = {
        "store_id": storeName,
        "app_name": appName,
        "app_id": appId,
        "version": version,
        "metadata": data,
        "apk_location": filePath,
        "apk_info": apkVals
    }

    result = db.versions.insert_one(appDict)
    return result.inserted_id

def writeReportDB(shas, _id):
    global db
    report = db.reports.find_one({'sha' : shas})
    if not report:
        return
    db.reports.update_one({'sha': shas}, {'versions': report.get('versions') + [_id]})

def checkAppDB(appUrl=None):
    """Returns the application entry from the DB based off the url"""
    global db
    return db.applications.find_one({"app_url": appUrl})


def checkVersionDB(appId, version=None):
    """Returns a list of versions for a specified application

    :param appId: ObjectId retrieved from the application entry from the DB
    :returns: list of all versions associated with an application
    """
    global db
    body = {"app_id": appId, "version": version} if version else {
        "app_id": appId}
    return list(db.versions.find(body))


def getPermissions(apkFilePath):
    permList = []
    temp = os.getcwd()
    os.chdir(start)
    permLoc = os.path.join("SupportFiles", "Permissions.jar")
    p = Popen(['java', '-jar', permLoc, apkFilePath],
              stdout=PIPE, stderr=STDOUT)
    [permList.append(line.strip().decode('ascii')) for line in p.stdout]
    os.chdir(temp)
    return permList


# Only need this because SlideMe is stupid and doesn't list it
def getPackageName(apkFilePath):
    temp = os.getcwd()
    os.chdir(start)
    permLoc = os.path.join("SupportFiles", "Package.jar")
    p = Popen(['java', '-jar', permLoc, apkFilePath],
              stdout=PIPE, stderr=STDOUT)
    os.chdir(temp)
    return [line.strip().decode('ascii') for line in p.stdout]


def getApkValues(apkFilePath):
    # return dict({})  # Dummy value until on linux instance
    temp = os.getcwd()
    os.chdir(start)
    metaCert = os.path.join("META-INF", "CERT.RSA")
    p1 = Popen(['unzip', '-p', apkFilePath, metaCert], stdout=PIPE)
    p = Popen(['keytool', '-printcert'], stdin=p1.stdout, stdout=PIPE)
    stdout, stderr = p.communicate()

    id_dict = dict({})
    for line in stdout.decode('utf-8').split('\n'):
        args = line.split('\t')
        if args.__len__() == 2 and args[0] == "":
            vals = args[1].strip().split()
            type_ = vals[0].rstrip(":")
            if type_ == "MD5" or type_ == "SHA1" or type_ == "SHA256":
                id_dict.update({type_: vals[1].replace(":", "")})
    os.chdir(temp)
    return id_dict


def genHashValues(apkFilePath):
    id_dict = dict({})

    with open(apkFilePath, "rb") as f:
        bytes = f.read()
        id_dict.update({"MD5": hashlib.md5(bytes).hexdigest()})
        id_dict.update({"SHA1": hashlib.sha1(bytes).hexdigest()})
        id_dict.update({"SHA256": hashlib.sha256(bytes).hexdigest()})

    return id_dict


def mkStoreDirs(storeName=None, appName=None):
    global root, store
    if storeName:
        safeExecute(os.mkdir, os.path.expanduser(root + '/apk'))
        safeExecute(os.mkdir, os.path.expanduser(root + '/apk/' + storeName))
        os.chdir(os.path.expanduser(root + '/apk/' + storeName))
    else:
        appName = removeSpecialChars(appName).replace(' ', '_').lower()
        safeExecute(os.mkdir, appName)
        return os.path.normpath(os.getcwd() + '/' + appName + '/')


def safeExecute(func, *args, default=None, error=BaseException):
    try:
        return func(*args)
    except error:
        return default

def convert_bytes(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1000.0:
            return "%3.1f %s" % (num, x)
        num /= 1000.0

def removeApp(appId):
    global db
    db.applications.delete_one({"_id": appId})