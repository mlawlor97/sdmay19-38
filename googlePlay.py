from utils import RateLimiter, requestHTML, safeExecute, getPermissions
from utils import writeAppDB, writeVersionDB, checkAppDB, checkVersionDB  # DB connectors
from SupportFiles.webDriverUtils import WebDriver
from SupportFiles.crawlerBase import CrawlerBase
from SupportFiles.metaDataBase import DataCollectionBase
# from googleplayapi.googleplay import GooglePlayAPI
from googleplayapi.gpapi.googleplay import GooglePlayAPI, SecurityCheckError

from datetime import datetime

class GoogleData(DataCollectionBase):

    def getPackage(self):
        self.tryCollection('package', lambda: self.url.split('id=')[-1].split('&')[0])

    def getDeveloper(self):
        self.tryCollection('developer', lambda: self.soup.select('a[href*="apps/dev"]')[0].text.strip())

    def getCategory(self):
        self.tryCollection('category', lambda: self.soup.find(itemprop='genre').text)

    def getPrice(self):
        def func():
            price = self.soup.find(itemprop='price')['content']
            return price if price is not '0' else '$0.00'

        self.tryCollection('price', func)

    def getContentRating(self):
        self.tryCollection('content_rating', lambda: self.soup.find(itemprop='contentRating')['content'])

    def getDescription(self):
        self.tryCollection('description', lambda: self.soup.find(itemprop='description')['content'])

    def getRating(self):
        self.tryCollection('rating', lambda: float("{0:.2f}".format(float(self.soup.find(itemprop='ratingValue')['content']))))

    def getNumDownloads(self):
        self.tryCollection('downloads', lambda: self.soup.find('div', string="Installs").next_sibling.find('span').text)


class GoogleVersion(DataCollectionBase):

    def getSize(self):
        self.tryCollection('size', lambda: self.soup.find('div', string="Size").next_sibling.find('span').text)

    def getPatchNotes(self):
        self.tryCollection('patch_notes', lambda: self.soup.find('h2', string="What's New").parent.next_sibling.find('content').text)

    def getPublishDate(self):
        date = self.soup.find('div', string='Updated').next_sibling.find('span').text
        date = datetime.strptime(date, "%B %d, %Y")

        self.tryCollection('publish_date', lambda: date)

    def getRequirements(self):
        self.tryCollection('requirements', lambda: self.soup.find('div', string='Requires Android').next_sibling.find('span').text)


# noinspection PyCompatibility
class GooglePlay(CrawlerBase):
    """Webcrawler for the googleplay store."""

    def __init__(self, siteUrl="https://play.google.com", rateLimiter=RateLimiter(10, 3)):
        super().__init__(siteUrl, rateLimiter)
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

        for app in apps:
            self.scrapeApp(f"{self.siteUrl}{app.attrs['href']}")

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

        if appEntry is None:
            playData = GoogleData(appPage, soup).getAll()
            price, package = playData.metaData.get('price'), playData.metaData.get('package')
            id_ = writeAppDB("GooglePlay", name, appPage, playData.metaData) 
        else:
            price, package = appEntry.get('price'), appEntry.get('package')
            id_ = appEntry.get('_id')
        
        version = safeExecute(soup.find('div', string="Current Version").next_sibling.find, 'span')
        if version is None:
            return
        version = version.text

        versions = checkVersionDB(id_, version)
        if versions == []:
            playVersion = GoogleVersion(appPage, soup).getAll()
            writeVersionDB("GooglePlay", name, id_, version, playVersion.metaData)
        else:
            return

        # Downloading google play apks
        # if price == "$0.00":
        #     self.gpa.log(package)
        #     fl = self.gpa.download(package)
        #     with open(package + ".apk", "wb") as apk_file:
        #         for chunk in fl.get("file").get("data"):
        #             apk_file.write(chunk)


def main():
    try:
        GooglePlay().crawl()
    except KeyboardInterrupt:
        print("Ended Early")
    print("Finished")


if __name__ == '__main__':
    main()
