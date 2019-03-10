from utils import RateLimiter, requestHTML, safeExecute, getPermissions, getApkValues, mkStoreDirs
from utils import writeAppDB, writeVersionDB, checkAppDB, checkVersionDB  # DB connectors
from SupportFiles.webDriverUtils import WebDriver
from SupportFiles.crawlerBase import CrawlerBase
from SupportFiles.metaDataBase2 import DataCollectionBase
# from googleplayapi.googleplay import GooglePlayAPI
from googleplayapi.gpapi.googleplay import GooglePlayAPI, SecurityCheckError, RequestError

from datetime import datetime
import uuid
import os

class GoogleData(DataCollectionBase):

    def price(self):
        price = self.soup.find(itemprop='price', content=True)['content']
        return price if price != "0" else "$0.00"

    _getPkg     = ("package",        lambda _: _.url.split('id=')[-1].split('&')[0])
    _getDev     = ("developer",      lambda _: _.soup.select('a[href*="apps/dev"]')[0].text.strip())
    _getCat     = ("category",       lambda _: _.soup.find(itemprop='genre').text)
    _getPrice   = ("price",          lambda _: _.price())
    _getCntRate = ("content_rating", lambda _: _.soup.find(itemprop='contentRating')['content'])
    _getDesc    = ("description",    lambda _: _.soup.find(itemprop='description')['content'])
    _getRating  = ("rating",         lambda _: "{0:.2f}".format(float(_.soup.find(itemprop='ratingValue')['content'])))
    _getNumDown = ("downloads",      lambda _: _.soup.find('div', string="Installs").next_sibling.find('span').text)


class GoogleVersion(DataCollectionBase):

    def date(self):
        date = self.soup.find('div', string='Updated').next_sibling.find('span').text
        date = datetime.strptime(date, "%B %d, %Y")
        return date

    _getSize    = ("file_size",     lambda _: _.soup.find('div', string="Size").next_sibling.find('span').text)
    _getPatch   = ("patch_notes",   lambda _: _.soup.find('h2', string="What's New").parent.next_sibling.find('content').text)
    _getPubDate = ("publish_date",  lambda _: _.date())
    _getReqs    = ("requirements",  lambda _: _.soup.find('div', string="Requires Android").next_sibling.find('span').text)


# noinspection PyCompatibility
class GooglePlay(CrawlerBase):
    """Webcrawler for the googleplay store."""
    siteUrl="https://play.google.com"
    rateLimiter = RateLimiter(10, 3);

    def __init__(self, siteUrl=siteUrl, limiter=rateLimiter):
        super().__init__(siteUrl, limiter)
        self.webDriver = WebDriver()
        self.subCategories = []
        self.commonCollections = [
            "/collection/topselling_free",
            "/collection/topselling_paid",
            "/collection/topgrossing",
            "/collection/topselling_new_paid",
            "/collection/topselling_new_free"
        ]
        self.gpa = GooglePlayAPI()
        # self.gpa.login("sdmay19@gmail.com", "Forensics4")
        self.gpa.login(gsfId=3948690411096122542, authSubToken="FwfSBWszDgviSe1ivuuvKa0qjnOTUlcpvGzS9sEtSSdn59NrCqTO9oeyE2h5qiorr-ycCw.")
        mkStoreDirs(storeName='googleplay')

    def crawl(self):
        # Get categories
        categories = self.getCategories(requestHTML(f"{self.siteUrl}/store/apps"))

        # Iterate over all categories
        for category in categories:

            # Get list of all subcategories plus the common collections
            [self.subCategories.append(category + subCat) for subCat in self.commonCollections]

            self.getSubCategories(category)
            if self.subCategories.__len__() == self.commonCollections.__len__():
                self.subCategories.append(category)

            # Iterate over all subcategories
            [self.getApps(subCategory) for subCategory in self.subCategories]

            # Clear cache
            self.subCategories.clear()

    @staticmethod
    def getCategories(soup):
        soup = soup.find(id="action-dropdown-children-Categories")
        return [cat['href'] for cat in soup(href=True)]

    def getSubCategories(self, categoryPage):
        soup = requestHTML(categoryPage)
        [self.subCategories.append(self.siteUrl + cat['href']) for cat in soup(class_='title-link')]

    def getApps(self, categoryPage):
        if self.webDriver.loadPage(categoryPage, 'class name', 'loaded') is None:
            return

        soup = self.webDriver.googleScroller()

        soup = soup.find('div', class_="card-list")
        apps = soup('a', class_="title")

        for app in apps[0:6]:
            self.scrapeApp(f"{self.siteUrl}{app.attrs['href']}")
        exit(0)

    def scrapeApp(self, appPage):
        soup = requestHTML(appPage)
        name = soup.find(itemprop='name')

        appEntry = checkAppDB(appPage)
        if not name:
            soup = self.webDriver.loadPage(appPage, 'xpath', "//h1[@itemprop='name']", True)
            name = soup.find(itemprop='name')
        if not name:
            print(appPage)
            return
        name = name.text.strip()
        # safeExecute(os.mkdir, os.path.expanduser(self.rootDir + "/" + name))
        appDir = mkStoreDirs(appName=name)

        if appEntry is None:
            playData = GoogleData(appPage, soup).getAll()
            price, package = playData.metaData.get('price'), playData.metaData.get('package')
            id_ = writeAppDB("GooglePlay", name, appPage, playData.metaData) 
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
            # print(versions[0].get('apk_file_path'))  # Checks if filepath is present
            return
        playVersion = GoogleVersion(appPage, soup).getAll()
        calculatedVals = None
        filePath = None

        # Downloading google play apks
        if price == "$0.00":
            # permissions, filePath = self.downloadApk(package, appDir)
            filePath = self.downloadApk(package, appDir)
            # if filePath:
            #     apk_values = getApkValues(filePath)
            #     calculatedVals = dict({
            #         'permissions'   : permissions,
            #         'apk_values'    : apk_values
            #     })
            
        writeVersionDB("GooglePlay", name, id_, version, playVersion.metaData, filePath)

    def downloadApk(self, package, savePath):
        self.gpa.log(package)
        try:
            fl = self.gpa.download(package, versionCode=None)
        except RequestError:
            print(f"failed to download {package}")
            # return (None, None)
            return None
        savePath = savePath + "/" + uuid.uuid4().hex + ".apk"
        with open(savePath, "wb") as apk_file:
            for chunk in fl.get("file").get("data"):
                apk_file.write(chunk)
        # return (getPermissions(savePath), savePath)
        return savePath


def main():
    # GooglePlay().scrapeApp("https://play.google.com/store/apps/details?id=com.google.vr.expeditions")
    GooglePlay().getApps("https://play.google.com/store/apps/collection/promotion_30025e1_daydream_storecategory_topapps?clp=an8KNgowcHJvbW90aW9uXzMwMDI1ZTFfZGF5ZHJlYW1fc3RvcmVjYXRlZ29yeV90b3BhcHBzEAcYAxJFCj92cl90b3BfZGV2aWNlX2ZlYXR1cmVkX2NhdGVnb3J5X2FwcHNfX18xX3Byb21vXzE1NDMzNTYyOTQ1NzYwMDAQDBgD:S:ANO1ljIyjUI&gsr=CoEBan8KNgowcHJvbW90aW9uXzMwMDI1ZTFfZGF5ZHJlYW1fc3RvcmVjYXRlZ29yeV90b3BhcHBzEAcYAxJFCj92cl90b3BfZGV2aWNlX2ZlYXR1cmVkX2NhdGVnb3J5X2FwcHNfX18xX3Byb21vXzE1NDMzNTYyOTQ1NzYwMDAQDBgD:S:ANO1ljL4zsA")
    # try:
    #     GooglePlay().crawl()
    # except KeyboardInterrupt:
    #     print("Ended Early")
    print("Finished")


if __name__ == '__main__':
    main()
