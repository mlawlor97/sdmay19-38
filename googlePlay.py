from utils import RateLimiter, requestHTML
from SupportFiles.webDriverUtils import WebDriver
from SupportFiles.crawlerBase import CrawlerBase
from SupportFiles.metaDataBase import DataCollectionBase


class GoogleData(DataCollectionBase):

    def getName(self):
        self.tryCollection('Name', lambda: self.soup.find(itemprop='name').text.strip(), True)
        return False if self.metaData.get('Name') is ('' or None) else None

    def getPackage(self):
        self.tryCollection('Package', lambda: self.url.split('=')[-1])
        # self.soup = self.soup.select('[data-p~=\"' + self.metaData.get('Package') + '\"]')

    def getDeveloper(self):
        self.tryCollection('Developer', lambda: self.soup.select('a[href*=apps/dev]')[0].text.strip())

    def getCategory(self):
        self.tryCollection('Category', lambda: self.soup.find(itemprop='genre').text)

    def getPrice(self):
        def func():
            price = self.soup.find(itemprop='price')['content']
            return price if price is not '0' else '$0.00'

        self.tryCollection('Price', func)

    def getContentRating(self):
        self.tryCollection('Content Rating', lambda: self.soup.find(itemprop='contentRating')['content'])

    def getDescription(self):
        self.tryCollection('Description', lambda: self.soup.find(itemprop='description')['content'])

    def getRating(self):
        self.tryCollection('Rating', lambda: float("{0:.2f}".format(float(self.soup.find(itemprop='ratingValue')['content']))))

    def getVersion(self):
        self.tryCollection('Version', lambda: self.soup.find('div', string="Current Version").next_sibling.find('span').text)

    def getNumDownloads(self):
        self.tryCollection('Downloads', lambda: self.soup.find('div', string="Installs").next_sibling.find('span').text)

    def getSize(self):
        self.tryCollection('Size', lambda: self.soup.find('div', string="Size").next_sibling.find('span').text)

    def getRequirements(self):
        self.tryCollection('Requirements', lambda: self.soup.find('div', string='Requires Android').next_sibling.find('span').text)

    def getPublishDate(self):
        self.tryCollection('Publish Date', lambda: self.soup.find('div', string='Updated').next_sibling.find('span').text)

    def getPatchNotes(self):
        self.tryCollection('Patch Notes ' + self.metaData.get('Version'), lambda: self.soup.find('h2', string="What's New").parent.next_sibling.find('content').text)


# noinspection PyCompatibility
class GooglePlay(CrawlerBase):

    def __init__(self, siteUrl="https://play.google.com", rateLimiter=RateLimiter(10, 3)):
        super().__init__(siteUrl, rateLimiter)
        self.webDriver = WebDriver()
        self.categoryLinks = []
        self.subCategories = []
        self.commonCollections = [
            "/collection/topselling_free",
            "/collection/topselling_paid",
            "/collection/topgrossing",
            "/collection/topselling_new_paid",
            "/collection/topselling_new_free"
        ]
        self.appList = dict({})  # May toss after getting DB connection / will get very big

    def crawl(self):
        # Get categories
        self.getCategories(requestHTML(self.siteUrl + '/store/apps'))

        # Iterate over all categories
        for category in self.categoryLinks:

            # Get list of all subcategories plus the common collections
            [self.subCategories.append(category + subCat) for subCat in self.commonCollections]

            self.getSubCategories(category)
            if self.subCategories.__len__() == self.commonCollections.__len__():
                self.subCategories.append(category)

            # Iterate over all subcategories
            [self.getApps(subCategory) for subCategory in self.subCategories]

            # Clear cache
            self.subCategories.clear()
        self.appList.clear()

    def getCategories(self, soup):
        soup = soup.find(class_='action-bar')
        [self.categoryLinks.append(self.siteUrl + cat['href']) for cat in soup(class_='child-submenu-link')]

    def getSubCategories(self, categoryPage):
        soup = requestHTML(categoryPage)
        [self.subCategories.append(self.siteUrl + cat['href']) for cat in soup(class_='title-link')]

    def getApps(self, categoryPage):
        if self.webDriver.loadPage(categoryPage, 'class name', 'loaded'):
            return

        soup = self.webDriver.googleScroller()

        soup = soup.find('div', class_="card-list")
        apps = soup('a', class_="title")

        for app in apps:
            name = app.text.strip()

            if self.appList.get(name):
                self.appList[name] = self.appList[name] + 1
            else:
                self.appList[name] = 1
                self.scrapeApp(self.siteUrl + app.attrs['href'])

    def scrapeApp(self, appPage):
        soup = requestHTML(appPage)
        playData = GoogleData(appPage, soup).getAll()

        # if playData.metaData.__len__() is not playData.methods.__len__():
        if playData is Exception:
            soup = self.webDriver.loadPage(appPage, 'xpath', "//h1[@itemprop='name']", True)
            playData = GoogleData(appPage, soup).getAll()

        playData.uploadJSON()

        if playData.metaData.get('Price') == "$0.00":
            print('Free')
        #     downloadGoogleApk(playData.metaData.get('Package'))


def main():
    GooglePlay().crawl()
    # GooglePlay().scrapeApp('https://play.google.com/store/apps/details?id=com.google.vr.expeditions')


if __name__ == '__main__':
    main()
