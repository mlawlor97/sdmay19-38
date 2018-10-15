import requests
import re
import os
from bs4 import BeautifulSoup


def createPath(path, *paths):
    return os.path.join(path, *paths)


def removeSpecialChars(string):
    return re.sub('\W+', ' ', string.lower())


def requestHTML(url):
    return BeautifulSoup(requests.get(url).content, 'lxml')


def logToFile(outputFile, line, *args):
    if args:
        options = args[0]
    else:
        options = 'a'

    f = open(outputFile, options)
    f.write(line)
    f.close()


def makeDirectory(appName):
    savePath = os.getcwd() + '/'

    tryMakeDir(savePath + 'reviews/' + appName)
    tryMakeDir(savePath + 'apks/' + appName)

    return savePath


def tryMakeDir(savePath):
    try:
        os.mkdir(savePath)
    except OSError:
        print('Failed to create directory %s ' % savePath)
    else:
        print('Successfully created the directory %s ' % savePath)


def downloadApk(apk):
    session = requests.Session()
    return session.get(apk).content


# TODO Change later to write to DB
def writeOutput(destination, *args, **kwargs):
    if destination == 'DB':
        # TODO Change to DB location
        destination = 'ApkPure Crawler Output.txt'

    if args:
        logToFile(destination, '', args[0])
    else:
        logToFile(destination, '', 'w')

    for key, value in kwargs.items():
        logToFile(destination, key + ': ' + value.__str__() + '\n')
