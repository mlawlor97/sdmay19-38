from utils import RateLimiter, mkStoreDirs, requestHTML, checkAppDB, safeExecute, downloadApk, getPackageName, writeAppDB, writeVersionDB
from SupportFiles.crawlerBase import CrawlerBase
from SupportFiles.metaDataBase2 import DataCollectionBase

import uuid
import re
from datetime import datetime

class SlideMeData(DataCollectionBase):
    
    def tags(self):
        tagList = []
        tags = self.soup.find(class_='terms')('a')
        [tagList.append(tag.text) for tag in tags]
        return tagList

    _getPrice   = ("price",         lambda _: '$' + _.soup.find(itemprop='price')['content'].strip())
    _getDev     = ("developer",     lambda _: _.soup.find(class_='submitted').a.text)
    _getCat     = ("category",      lambda _: _.soup.find(class_='category').a.text)
    _getNumDown = ("downloads",     lambda _: _.soup.find(class_='downloads').text)
    _getRating  = ("rating",        lambda _: _.soup.find(itemprop='ratingValue')['content'].strip())
    _getTags    = ("tags",          lambda _: _.tags())
    _getDesc    = ("description",   lambda _: _.soup.find(itemprop='description')['content'].strip())
    _getSubCat  = ("subcategory",   lambda _: _.soup.find(itemprop='applicationSubCategory')['content'].strip())


class SlideMeVersion(DataCollectionBase):

    def publishDate(self):
        date = str(self.soup.find(itemprop='datePublished')['datetime'].strip())
        date = datetime.strptime(date, '%d-%m-%Y')
        return date

    _getPubDate = ("publish_date",  lambda _: _.publishDate())
    _getOS      = ("min_os",        lambda _: _.soup.find(itemprop='operatingSystem')['content'].strip())


class SlideMe(CrawlerBase):
    siteUrl = "http://slideme.org"
    rateLimiter = RateLimiter(0, 0)

    def __init__(self, siteUrl=siteUrl, rateLimiter=rateLimiter):
        super().__init__(siteUrl, rateLimiter)
        mkStoreDirs(storeName="slideme")

    def crawl(self):
        soup = requestHTML(f"{self.siteUrl}/applications")
        categories = self.getCategories(soup)

        crawlableCats = []

        for cat in categories[-1:]:
        # for cat in categories:
            subs = self.getCategories(requestHTML(cat))
            crawlableCats += subs if subs.__len__() > 0 else [cat]
            break
        
        for cat in crawlableCats:
            page = 0
            while(True):
                apps = self.getApps(requestHTML(f"{cat}&page={page}"))
                if not apps:
                    break
                
                page += 1
                [self.scrapeAppData(app) for app in apps[:1]]
                # [self.scrapeAppData(app) for app in apps]
                return

    def getCategories(self, soup):
        cats = []
        [cats.append(self.siteUrl + cat['href']) for cat in soup(class_="apachesolr-facet")]
        return cats

    def getApps(self, soup):
        return [self.siteUrl + app.find('a')['href'] for app in soup(class_="node-mobileapp")]

    def scrapeAppData(self, url):
        entry = checkAppDB(appUrl=url)
        soup = safeExecute(requestHTML, url)
        if entry:
            appName, id_ = (entry.get('app_name'), entry.get('_id'))
        else:
            appName = safeExecute(soup.find(class_='title').span)
            appName = appName[0]['title']

        if not appName or soup.find(class_='price').text.lower() != 'free':    # Not bothering with paid apps because they do not supply package names
            return

        slideData = SlideMeData(url, soup).getAll()
        savePath = mkStoreDirs(appName=appName)

        apkPath = self._scrapeAPK(soup, savePath)
        if not apkPath:
            return

        package = getPackageName(apkPath)[0]
        slideData.metaData.update({'package' : package})

        id_ = writeAppDB('SlideMe', appName, url, package, slideData.metaData)
        version = soup.find(itemprop='softwareVersion')['content'].strip()

        slideVersion = SlideMeVersion(url, soup).getAll()
        writeVersionDB('SlideMe', appName, id_, version, slideVersion.metaData, apkPath)

    @staticmethod
    def _scrapeAPK(soup, savePath):
        downloadLink = soup.find(class_='download-button').a['href']

        if downloadLink:
            fileName = uuid.uuid4().hex + '.apk'
            return downloadApk(downloadLink, f"{savePath}/{fileName}")
        return None


def main():
    sm = SlideMe()
    sm.scrapeAppData('http://slideme.org/application/telegraph')
    # sm.crawl()

if __name__ == "__main__":
    main()