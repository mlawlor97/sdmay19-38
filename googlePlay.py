from utils import RateLimiter, requestHTML, safeExecute, getPermissions, getApkValues, mkStoreDirs, logToFile
from utils import writeAppDB, writeVersionDB, checkAppDB, checkVersionDB  # DB connectors
from SupportFiles.webDriverUtils import WebDriver
from SupportFiles.crawlerBase import CrawlerBase
from SupportFiles.metaDataBase2 import DataCollectionBase
# from googleplayapi.googleplay import GooglePlayAPI
from googleplayapi.gpapi.googleplay import GooglePlayAPI, SecurityCheckError, RequestError

from threading import Thread, Lock
from datetime import datetime
import uuid
import os


class GoogleData(DataCollectionBase):

    def price(self):
        price = self.soup.find(itemprop='price', content=True)['content']
        return price if price != "0" else "$0.00"

    _getPkg = ("package", lambda _: _.url.split('id=')[-1].split('&')[0])
    _getDev = ("developer", lambda _: _.soup.select(
        'a[href*="apps/dev"]')[0].text.strip())
    _getCat = ("category", lambda _: _.soup.find(itemprop='genre').text)
    _getPrice = ("price", lambda _: _.price())
    _getCntRate = ("content_rating", lambda _: _.soup.find(
        itemprop='contentRating')['content'])
    _getDesc = ("description", lambda _: _.soup.find(
        itemprop='description')['content'])
    _getRating = ("rating", lambda _: "{0:.2f}".format(
        float(_.soup.find(itemprop='ratingValue')['content'])))
    _getNumDown = ("downloads", lambda _: _.soup.find(
        'div', string="Installs").next_sibling.find('span').text)


class GoogleVersion(DataCollectionBase):

    def date(self):
        date = self.soup.find(
            'div', string='Updated').next_sibling.find('span').text
        date = datetime.strptime(date, "%B %d, %Y")
        return date

    _getSize = ("file_size", lambda _: _.soup.find(
        'div', string="Size").next_sibling.find('span').text)
    _getPatch = ("patch_notes", lambda _: _.soup.find(
        'h2', string="What's New").parent.next_sibling.find('content').text)
    _getPubDate = ("publish_date", lambda _: _.date())
    _getReqs = ("requirements", lambda _: _.soup.find(
        'div', string="Requires Android").next_sibling.find('span').text)


# noinspection PyCompatibility
class GooglePlay(CrawlerBase):
    """Webcrawler for the googleplay store."""
    siteUrl = "https://play.google.com"
    rateLimiter = RateLimiter(10, 3)

    def __init__(self, siteUrl=siteUrl, limiter=rateLimiter):
        super().__init__(siteUrl, limiter)
        self.webDriver = WebDriver()
        # self.subCategories = []
        self.commonCollections = [
            "/collection/topselling_free",
            "/collection/topselling_paid",
            "/collection/topgrossing",
            "/collection/topselling_new_paid",
            "/collection/topselling_new_free"
        ]
        self.gpa = GooglePlayAPI()
        self.lock = Lock()
        # self.gpa.login("sdmay19@gmail.com", "Forensics4")
        self.gpa.login(gsfId=3948690411096122542,
                       authSubToken="FwfSBWszDgviSe1ivuuvKa0qjnOTUlcpvGzS9sEtSSdn59NrCqTO9oeyE2h5qiorr-ycCw.")
        mkStoreDirs(storeName='googleplay')

    def crawl(self):
        # Get categories
        categories = self.getCategories(requestHTML(f"{self.siteUrl}/store/apps"))
        threads = []

        # Iterate over all categories
        for category in categories:
            threads.append(Thread(target=self.crawlCategory, args=(category, )))
            threads[-1].start()
        
        [t.join() for t in threads]

    @staticmethod
    def getCategories(soup):
        soup = soup.find(id="action-dropdown-children-Categories")
        return [cat['href'] for cat in soup(href=True)]

    def getSubCategories(self, categoryPage, subCategories):
        soup = requestHTML(categoryPage)
        [subCategories.append(self.siteUrl + cat['href']) for cat in soup(class_='title-link')]

    def crawlCategory(self, category):
        subCategories = []

        [subCategories.append(category + subCat) for subCat in self.commonCollections]

        self.getSubCategories(category, subCategories)
        if subCategories.__len__() == self.commonCollections.__len__():
            subCategories.append(category)
        
        [self.getApps(subCategory) for subCategory in subCategories]
        print(f"Finished Category {category}")

        subCategories.clear()


    def getApps(self, categoryPage):
        self.lock.acquire()

        if self.webDriver.loadPage(categoryPage, 'class name', 'loaded') is None:
            return

        soup = self.webDriver.googleScroller()

        soup = soup.find('div', class_="card-list")
        apps = soup('a', class_="title")

        self.lock.release()

        for app in apps:
            self.scrapeApp(f"{self.siteUrl}{app.attrs['href']}")

    def scrapeApp(self, appPage):
        soup = requestHTML(appPage)
        name = soup.find(itemprop='name')

        appEntry = checkAppDB(appPage)
        if not name:
            self.lock.acquire()
            soup = self.webDriver.loadPage(appPage, 'xpath', "//h1[@itemprop='name']", True)
            self.lock.release()
            name = soup.find(itemprop='name')
        if not name:
            print(appPage)
            return
        name = name.text.strip()
        appDir = mkStoreDirs(appName=name)

        if appEntry is None:
            playData = GoogleData(appPage, soup).getAll()
            price, package = playData.metaData.get('price'), playData.metaData.get('package')
            # id_ = writeAppDB("GooglePlay", name, appPage, package, playData.metaData)
        else:
            id_ = appEntry.get('_id')
            appEntry = appEntry.get('metadata')
            price, package = appEntry.get('price'), appEntry.get('package')

        version = safeExecute(soup.find('div', string="Current Version").next_sibling.find, 'span')
        if version is None:
            return
        version = version.text

        versions = checkVersionDB(id_, version)
        if versions != []:
            return
        playVersion = GoogleVersion(appPage, soup).getAll()
        filePath = None

        # Downloading google play apks
        if price == "$0.00":
            filePath = self.downloadApk(package, appDir)

        writeVersionDB("GooglePlay", name, id_, version,playVersion.metaData, filePath)

    def downloadApk(self, package, savePath):
        fileName = uuid.uuid4().hex + ".apk"
        savePath = os.path.normpath(savePath + "/" + fileName)
        self.gpa.log(package)
        try:
            fl = self.gpa.download(package, versionCode=None)
        except RequestError:
            # print(f"failed to download {package}")
            logToFile("../incompatible.txt", package)
            return None
        with open(savePath, "wb") as apk_file:
            for chunk in fl.get("file").get("data"):
                apk_file.write(chunk)
        return savePath


def main():
    # url = "https://play.google.com/store/apps/details?id=com.intergraph.mobileresponder"
    # GooglePlay().scrapeApp(url)
    try:
        GooglePlay().crawl()
    except KeyboardInterrupt:
        print("Ended Early")
    print("Finished")


if __name__ == '__main__':
    main()
