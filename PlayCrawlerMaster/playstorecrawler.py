#!/usr/bin/env python3

import logging
import multiprocessing
import os
import random
import re
import requests
import sys
import time

import http.client

from PlayCrawlerMaster.googleplayapi.googleplay import GooglePlayAPI

###########################
# DO NOT TRY THIS AT HOME #
###########################
from urllib3.exceptions import InsecureRequestWarning
requests.urllib3.disable_warnings(InsecureRequestWarning)  # suppress certificate matching warnings

###################
# Globals         #
###################
manager = multiprocessing.Manager()
Global  = manager.Namespace()
Global.offerType = 1  # safe to assume for all our downloads


class PlayStoreCredentials(object):
    """PlayStoreCredentials"""
    def __init__(self, androidId, sdk=24, delay=60, email=None, password=None, authSubToken=None):
        super(PlayStoreCredentials, self).__init__()
        self.androidId = androidId.strip()
        if sdk:
            self.sdk = int(sdk)
        else:
            self.sdk = 24
        if delay:
            self.delay = int(delay)
        else:
            self.delay = 60
        if email:
            self.email = email.strip()
        else:
            self.email = None
        if password:
            self.password = password.strip()
        else:
            self.password = None
        if authSubToken:
            self.authSubToken = authSubToken.strip()
        else:
            self.authSubToken = None

    def __str__(self):
        return str(self.androidId)
# END: class PlayStoreCredentials


class PlayStoreCrawler(object):
    def __init__(self, report, dlFiles=[], dlFilesBeta=[]):
        self.report      = report
        self.dlFiles     = dlFiles
        self.dlFilesBeta = dlFilesBeta

    def checkPlayStore(self, credentials, lang="en_US"):
        """
        checkPlayStore(androidId):
        """
        filenames = []
        logging.debug('Logging in to Play Store with: ' + credentials.androidId)
        playStore = GooglePlayAPI(credentials.androidId, lang)
        if playStore.login(authSubToken=credentials.authSubToken):
            logging.info('{0} searches Play in {1} seconds'.format(credentials.androidId, credentials.delay))
            time.sleep(credentials.delay)

            # if 'com.android.vending' in None:
            #     for storeApk in self.report.dAllApks['com.android.vending']:
            #         try:
            #             if storeApk.extraname and storeApk.extraname.endswith('leanback'):
            #                 devicename = 'fugu'
            #             else:
            #                 devicename = 'sailfish'
            #             logging.debug('{0} VendingAPK: vername={1}, vercode={2}, devicename={3}'.format(credentials.androidId, storeApk.ver, storeApk.vercode, devicename))
            #             playvercode = self.playstore.playUpdate(storeApk.ver, str(storeApk.vercode))
            #             if playvercode:
            #                 logging.debug('{0} Play Store update {1}'.format(credentials.androidId, playvercode))
            #                 filenames.append(self.downloadApk('com.android.vending', credentials.delay + random.randint(0, credentials.delay), playvercode, agentvername=storeApk.ver, agentvercode=str(storeApk.vercode), devicename=devicename))
            #                 logging.info('{0} pauses {1} seconds before continuing'.format(credentials.androidId, credentials.delay))
            #                 time.sleep(credentials.delay)
            #         except:
            #             logging.exception('!!! playstore.playUpdate({0}, {1}) exception ...'.format(storeApk.ver, storeApk.vercode))
            #         # END: try
            #     # END: for storeApk

        else:
            logging.error('Play Store login failed for {0}'.format(credentials.androidId))
        # END: if playStore.login()

        details = playStore.bulkDetails({'com.h8games.helixjump'}, 24)
        for app in details.body.entry:
            version = app.doc.details.appDetails.versionCode
        filenames.append(self.downloadApk(playStore, 'com.h8games.helixjump', 10, version))
        return filenames
    # END: def checkPlayStore

    @staticmethod
    def downloadApk(store, package, delay, version, agentvername=None, agentvercode=None, devicename="sailfish"):
        """
        downloadApk(avi, delay, isBeta): Download the specified ApkInfo from the Play Store to APK file name
        """
        apkName = package + '-GooglePlay.apk'

        try:
            if os.path.exists(apkName):
                logging.info('{0} File {1} already exists'.format(store.androidId, apkName))
                return

            if os.path.exists(os.path.join('.', 'apkcrawler', apkName)):
                logging.info('{0} File {1} already exists (in ./apkcrawler/)'.format(store.androidId, apkName))
                return

            if os.path.exists(os.path.join('..', 'apkcrawler', apkName)):
                logging.info('{0} File {1} already exists (in ../apkcrawler/)'.format(store.androidId, apkName))
                return

            logging.info('{0} downloads "{1}" in {2} seconds'.format(store.androidId, apkName, delay))
            time.sleep(delay)

            # File might have been dowloaded during our wait, check again
            if os.path.exists(apkName):
                logging.info('{0} File {1} already exists'.format(store.androidId, apkName))
                return

            if os.path.exists(os.path.join('.', 'apkcrawler', apkName)):
                logging.info('{0} File {1} already exists (in ./apkcrawler/)'.format(store.androidId, apkName))
                return

            if os.path.exists(os.path.join('..', 'apkcrawler', apkName)):
                logging.info('{0} File {1} already exists (in ../apkcrawler/)'.format(store.androidId, apkName))
                return

            for x in range(1, 4):  # up to three tries
                res = store.download(package, version, Global.offerType, agentvername, agentvercode, devicename)
                if res.body:
                    with open(apkName, 'wb') as local_file:
                        local_file.write(res.body)
                    logging.debug('reg :' + apkName)
                    return apkName
                elif res.status_code == http.client.SERVICE_UNAVAILABLE:
                    wait = delay * x
                    # logging.info('{0} too many sequential requests on the Play Store (503) downloading {1}: waiting {'
                    #              '2} seconds'.format(avi.download_src.androidId, apkname, wait))
                    time.sleep(wait)  # wait longer with each failed try
                    continue
                elif res.status_code == http.client.FORBIDDEN:
                    logging.error('{0} dowloading {1} is forbidden (403)'.format(store.androidId, apkName))
                    return  # Nope, won't happen
                else:
                    logging.error('{0} downloading {1} returned unknown HTTP status {2}'.format(store.androidId, apkName, res.status_code))
                    return  # Nope, won't happen
            else:
                logging.error('{0} downloading {1} failed with repetitive 503 errors'.format(store.androidId, apkName))
                return  # Kept receiving 503, return empty
            # END: for x

        except OSError:
            logging.exception('!!! Filename is not valid: "{0}"'.format(apkName))
            return
    # END: def downloadApk

    def crawl(self, threads=4):
        """
        crawl(): check all PlayStores
        """
        path = os.path.dirname(__file__)
        if path:
            path += '/'
        credentialsFile = path + os.path.splitext(os.path.basename(__file__))[0] + '.config'
        stores = getCredentials(credentialsFile)
        self.checkPlayStore(stores[0])
    # END: crawl():
# END: class PlayStoreCrawler


class CredentialsException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def getCredentials(credentialsfile):
    """
    getCredentials(): Retrieve Play Store credentials from the file
    """
    sReCredentials = '^\s*(?P<ANDROIDID>[^#,]*),\s*(?P<SDK>[^#,]*),\s*(?P<DELAY>[^#,]*),\s*(?P<EMAIL>[^#,]*),' \
                     '\s*(?P<PASSWORD>[^#,]*),\s*(?P<TOKEN>[^#,]*)(\s*#.*)?$'
    reCredentials  = re.compile(sReCredentials)
    tokenDelay = 0
    credentials = []
    if os.path.isfile(credentialsfile):
        with open(credentialsfile, 'r') as f:
            fileLines = f.readlines()
        for line in fileLines:
            if line:
                try:
                    m = reCredentials.match(line)
                    if m:
                        androidId = m.group('ANDROIDID')
                        sdk       = m.group('SDK')
                        delay     = m.group('DELAY')
                        email     = m.group('EMAIL')
                        password  = m.group('PASSWORD')
                        token     = m.group('TOKEN')
                        logging.info('Found credentials for: {0}'.format(androidId))
                        if not token:
                            logging.info('{0} lacks authToken'.format(androidId))
                            if tokenDelay:
                                logging.info('Wait {0} seconds before processing anymore tokens'.format(delay))
                                time.sleep(tokenDelay)
                            token = getToken(androidId, email, password)
                            if token:
                                logging.info('{0} writing authToken to config to {1}'.format(androidId, credentialsfile))
                                updateTokenCredentials(credentialsfile, androidId, delay, email, password, token)
                            else:
                                logging.error('{0} authToken retrieval failed'.format(androidId))
                            tokenDelay = int(delay)  # we don't want to fetch tokens too quickly after one another
                        if token:
                            credentials.append(PlayStoreCredentials(androidId, sdk, delay, email, password, token))
                        else:
                            logging.error('{0} has no valid token and will not be crawled'.format(androidId))
                except:
                    raise CredentialsException('Malformed line in Credentials file', credentialsfile)
    else:
        raise CredentialsException('Credentials file does not exist', credentialsfile)
    return credentials
# END: def getCredentials


def getToken(androidId, email, password, lang="en_US"):
    """
    getToken(): Retrieve a Play Store authToken
    """
    logging.info('{0} requests authToken'.format(androidId))
    return GooglePlayAPI(androidId, lang).login(email, password)
# END: def getToken


def updateTokenCredentials(credentialsfile, androidId, sdk, delay, email, password, token=''):
    """
    updateTokenCredentials(): update the authToken stored in the Credentialsfile for the original line
     Quickly opens the file, changes the line and writes it. Locking is short and should be safe for intermediary changes.
    """
    sReCredentials = '(?P<ID>\s*' + androidId + ',\s*' + sdk + ',\s*' + delay + ',\s*' + email + ',\s*' + password + ',\s*)(?P<TOKEN>[^\s#]*)(?P<COMMENT>\s*#.*)?'
    reCredentials  = re.compile(sReCredentials)

    if os.path.isfile(credentialsfile):
        file_handle = open(credentialsfile, 'r')
        file_string = file_handle.read()
        file_handle.close()

        file_string = (reCredentials.sub('\g<ID>' + token + '\g<COMMENT>', file_string))

        file_handle = open(credentialsfile, 'w')
        file_handle.write(file_string)
        file_handle.close()
# END: def updateTokenCredentials


if __name__ == "__main__":
    """
    main(): single parameter for report_sources.sh output
    """

    crawler = PlayStoreCrawler(None)
    crawler.crawl()
