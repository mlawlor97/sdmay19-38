from utils import RateLimiter, requestHTML, logToFile, removeSpecialChars, createPath, downloadApk, writeOutput, safeExecute, mkStoreDirs
from utils import writeAppDB, writeVersionDB, checkAppDB, checkVersionDB  # DB Connectors
from SupportFiles.webDriverUtils import WebDriver
from SupportFiles.metaDataBase2 import DataCollectionBase
from SupportFiles.crawlerBase import CrawlerBase

from threading import Thread, Lock
from datetime import datetime, timedelta
from time import sleep, time
import os
import uuid


class GetPureData(DataCollectionBase):

    def rating(self):
        rating = self.soup.find(class_='rating')
        return rating.text.strip() if rating else 0.0

    _getDev     = ("developer",     lambda _: _.soup.find(class_='details-author').find('a').text.strip())
    _getCat     = ("category",      lambda _: _.soup.find(class_='additional')('span')[-1].text.strip())
    _getDesc    = ("description",   lambda _: _.soup.find(class_='content').text)
    _getRating  = ("rating",        lambda _: _.rating())
    _getTags    = ("tags",          lambda _: [tag.text for tag in _.soup.find(class_="tag_list")('li') if tag.text])


class GetPureVersion(DataCollectionBase):

    def changeLog(self):
        log = self.soup.find(class_='ver-whats-new')
        return log.text if log and log.text.strip() != '' else "No Patch Notes"

    def date(self):
        date = str(self.soup.find(class_='update-on').text)
        date = datetime.strptime(date, "%Y-%m-%d")
        return date

    _getType    = ("apk_type",      lambda _: _.soup.find(class_='ver-item-t').text)
    _getSize    = ("file_size",     lambda _: str(_.soup.find(class_='ver-item-s').text))
    _getReqs    = ("requirements",  lambda _: str(_.soup.find('strong', string='Requires Android: ').next_sibling))
    _getPubDate = ("publish_date",  lambda _: _.date())
    _getPatch   = ("patch_notes",   lambda _: _.changeLog())
    _getSign    = ("signature",     lambda _: str(_.soup.find('strong', string='Signature: ').next_sibling).strip())
    _getSha     = ("sha1",           lambda _: str(_.soup.find('strong', string='File SHA1: ').next_sibling).strip())


# noinspection PyCompatibility
class GetPureReview(DataCollectionBase):

    def pubDate(self):
        now = datetime.now()
        date = self.soup.find(class_='author-time').find('span').text.strip()
        if 'ago' in date:
            timePast = date.split(' ')[0]
            timePast = int(timePast) if 'a' not in timePast else 1
            now -= timedelta(days=timePast) if 'days' in date else timedelta(hours=timePast)
        return now.strftime("%Y-%m-%d")

    def message(self):
        article = self.soup.find(class_='article')
        return ''.join(self._msg(article, []))

    def _msg(self, soup, msg):
        for content in soup.contents:
            if content.string:
                msg.append(content.string)
            else:
                alt, href, vidSrc = content.get('alt'), content.get('href'), content.get('data-src')
                if alt:
                    msg.append(alt)
                elif vidSrc:
                    msg.append(f"[{vidSrc}]")
                elif href:
                    msg.append(f"[{href}]")
                self._msg(content, msg)
        return msg

    def msgRating(self):
        rating = self.soup.find(class_='cmt-vote')
        return 0 if 'Like' in rating.text else rating.text.strip()
    
    def responses(self, soup, resps: list):
        soup = soup.find('ul', recursive=False)
        lastSlash = self.url.rfind('/') + 1
        if not soup:
            return
        for response in soup(id=True, recursive=False):
            data = GetPureReview(soup=requestHTML(self.url[:lastSlash] + response['id'].lstrip('c'))).getAll()
            resps.append(data.metaData)
            self.responses(response, resps)
        if resps.__len__() is 0:
            raise AttributeError
        else:
            return resps

    _getUser    = ("user",           lambda _: _.soup.find(class_='author-name').find('span').text.strip())
    _getPubDate = ("publish_date",   lambda _: _.pubDate())
    _getTitle   = ("title",          lambda _: _.soup.find(class_='article-title').text.strip(), False)
    _getReview  = ("message",        lambda _: _.message().strip())
    _getMsgRate = ("message_rating", lambda _: _.msgRating())
    _getReplys  = ("responses",      lambda _: _.responses(_.soup.find(id="cmt-reply-data"), []), False)


# noinspection PyCompatibility
class ApkPure(CrawlerBase):

    siteUrl = "http://apkpure.com"
    rateLimiter = RateLimiter(0, 0)

    def __init__(self, siteUrl=siteUrl, limiter=rateLimiter):
        super().__init__(siteUrl, limiter)
        self.webDriver = WebDriver()
        self.lock = Lock()
        self.categories = []
        mkStoreDirs(storeName='apkpure')

    def crawl(self):
        """Crawls entirety of ApkPure"""
        cats = self.getCategories([])
        threads = []

        for cat in cats[2:3]:
            threads.append(Thread(target=self._crawlCategory, args=(cat, )))
            threads[-1].start()

        [t.join() for t in threads]
                
    def getCategories(self, list_=list()):
        """Gets list of all categories listed on the site
        
        :return: list of all categories
        """
        cats = requestHTML(f"{self.siteUrl}/app")(class_='index-category')
        [[list_.append(cat['href']) for cat in sect(href=True)] for sect in cats]
        return list_

    def _crawlCategory(self, category):
        """Goes through a category and processes all apps within it. Will run on its own thread
        
        :param category: Url of the category that is being processed
        """
        pageNumber = 1
        while True:
            page = f"{category}?page={pageNumber}"

            appList = self.getAppsOnPage(self.siteUrl + page)
            for app in appList:
                currUrl = self.siteUrl + app
                appName, id_ = self.scrapeAppData(currUrl)

                if appName:
                    # self._collectAllVersions(appName, id_, currUrl + '/versions')
                    self._collectAllReviews(appName)   

            if appList.__len__() is 0:
                break             

            pageNumber += 1

        print(f"Finished: {category}")

    @staticmethod
    def getAppsOnPage(url):
        """Gets list of all apps on a page for a category
        
        :param url: Url for the webpage that the apps are on
        :return: list of all links for apps present on the page
        """
        apps = requestHTML(url)(class_='category-template-title')
        return [] if apps is None else [app['href'] for app in [a.find('a', href=True) for a in apps]]

    @staticmethod
    def scrapeAppData(url):
        """Collects all application data from an app
        
        :param url: Url of the application's web page
        :returns: Application Name and Mongo ObjectId
        :rtype: Tuple(String, ObjectId)
        """
        entry = checkAppDB(appUrl=url)  # Gets application entry from the DB
        if entry:  # If the entry exists nothing needs to be done here / May change to run again after an amount of time
            return (entry.get('app_name'), entry.get('_id'))

        soup = safeExecute(requestHTML, url)
        appName = safeExecute(soup.find(class_='title-like').find('h1').text.strip)
        if appName is None:
            return (None, None)

        pureData = GetPureData(url, soup).getAll()
        pkg = url.split('/')[-1]
        id_ = writeAppDB('ApkPure', appName, url, pkg, pureData.metaData)

        return (appName, id_)

    def _collectAllVersions(self, name, id_, url):
        """Creates list of all present versions and passes them for processing
        
        :param name: App Name
        :param id_: ObjectId retrieved from the MongoDB
        :param url: Url of the version page for the app
        """
        soup = requestHTML(url)
        versionList = soup.find(class_='ver')

        if versionList:
            self._scrapeVersions(name, id_, url, versionList('li'))
        else:
            logToFile('Versions.txt', f"{url}\n")

    def _scrapeVersions(self, name, id_, url, versionList):
        """Collects all information for all versions for an application. Only runs on versions that have not been logged into the database. Writes versions into database and downloads apk file.
        
        :param name: App Name
        :param id_: ObjectId retrieved from the MongoDB
        :param url: Url with all listed versions
        :param versionList: List of all present versions
        """
        def _loadVersions(index):
            """Opens up version pop-up for all new versions"""
            for v in versionList[0: difference]:
                self.webDriver.clickPopUp("ver-item-m", "mfp-close", index, False)
                self.webDriver.clickAway("mfp-close", "class name")
                index += 1

            sleep(0.1)
            v = self.webDriver.fetchPage()
            whatsNew = v.find(class_='ver-whats-new')
            if whatsNew:
                while 'loading..' in v.find(class_='ver-whats-new'):
                    print('loading...')
                    v = self.webDriver.fetchPage()
            return v.find(class_='ver')('li')

        versionsLogged = checkVersionDB(id_)
        difference = versionList.__len__() - versionsLogged.__len__()
        if difference is 0:
            return

        self.lock.acquire() 
        safeExecute(self._loadPage, url, 'ver')
        versionList = safeExecute(_loadVersions, 0, default=versionList)
        self.lock.release()
        appDir = mkStoreDirs(appName=name)
        # reviewDir = mkStoreDirs(appName=name, apk=False)
        
        for v in versionList[0: difference]:
            version = safeExecute(v.find('span').text.lstrip, 'V', default=None)
            if version is None:
                print(f"{url} has version problems")
            
            pureVersion = GetPureVersion(url, v).getAll()
            path = self.scrapeApk(f"{self.siteUrl}{v.find(href=True)['href']}", appDir)
            print(path)
            writeVersionDB("ApkPure", name, id_, version, pureVersion.metaData, path)
            exit(0)

    def _collectAllReviews(self, appName):
        """Goes through each page of reviews and sends them for further processing
        
        :param appName: Name of the application
        """
        groupName = removeSpecialChars(appName.lower()).replace(' ', '-').rstrip('-')
        reviewsUrl = f"{self.siteUrl}/group/{groupName}?reviews=1&page="
        baseUrl = f"{self.siteUrl}/group/{groupName}/"

        reviewList = list()
        dir_ = mkStoreDirs(appName=appName)

        # Continues to go through pages of reviews until there are no more
        pageNumber = 1
        while self._scrapeReviews(f"{reviewsUrl}{pageNumber}", baseUrl, reviewList):
            pageNumber += 1

        print(reviewList.__len__())
        writeOutput(dir_ + "review.txt", reviewList)
        exit(0)        

    def _scrapeReviews(self, groupUrl, url, reviewList):
        """Scrapes all reviews on a review page"""
        reviews = requestHTML(url)('li', class_='cmt-root')
        for review in reviews:
            reviewUrl = url + review['id'].lstrip('c')
            self.lock.acquire()
            self._loadPage(reviewUrl, 'bread-crumbs')
            self.webDriver.loadMore('cmt-more-btn')
            soup = self.webDriver.fetchPage()
            self.lock.release()

            reviewData = GetPureReview(reviewUrl, soup).getAll()
            reviewData.tryCollection("rating", 
                lambda _: review.select_one('.cmt-icon-s-strs')['data-score'], False)
            
            reviewList.append(reviewData.JSON)

        return None if reviews.__len__() == 0 else not None

    @staticmethod
    def scrapeApk(downloadUrl, savePath):
        """Downloads the apk from ApkPure
        
        :param downloadUrl: Url of the download page
        :param savePath: Folder to save the apk in
        """
        soup = requestHTML(downloadUrl)
        downloadLink = soup.find(id='download_link')

        if downloadLink:
            fileName = uuid.uuid4().hex + ".apk"
            return downloadApk(downloadLink.get('href'), savePath + fileName, fileName, savePath)
        return None

    def _loadPage(self, url, verifier, searchBy="class name"):
        """Loads the page from the url and gets rid of unnecessary elements
        
        :param url: Url to load
        :param verifier: Element that can only be found when the page is loaded
        :param searchBy: Indentifier of the element that is being looked for
        """
        self.webDriver.loadPage(url, searchBy, verifier)
        self.webDriver.driver.execute_script('policy_review.setReview();')  # Gets rid of cookie agreement
        self.webDriver.driver.execute_script('document.getElementById("ad-aegon-side").remove()')  # Removes QR code


def main():
    try:
        ApkPure().crawl()
    except KeyboardInterrupt:
        print("Ended Early")
    print("Finished")


if __name__ == '__main__':
    main()
