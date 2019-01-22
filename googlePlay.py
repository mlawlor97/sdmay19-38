from utils import RateLimiter, requestHTML
from SupportFiles.webDriverUtils import WebDriver
from SupportFiles.crawlerBase import CrawlerBase
from SupportFiles.metaDataBase import DataCollectionBase


class GoogleData(DataCollectionBase):

    def getName(self):
        def func():
            name = self.soup.find(itemprop='name').text.strip()

            if name is not '':
                self.validApplication = True
                return name

        self.tryCollection('Name', func)

    def getPackage(self):
        self.tryCollection('Package', lambda: self.url.split('=')[-1])

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

    def getUpdatedOn(self):
        self.tryCollection('Updated On', lambda: self.soup.find('div', string='Updated').next_sibling.find('span').text)

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
        self.appList = dict({})

    def crawl(self):
        soup = requestHTML(self.siteUrl + '/store/apps')

        # Get categories
        self.getCategories(soup)

        # Iterate over all categories
        for category in self.categoryLinks:

            # Get list of all subcategories plus the common collections
            for subCategory in self.commonCollections:
                self.subCategories.append(category + subCategory)

            self.getSubCategories(category)
            if self.subCategories.__len__() == self.commonCollections.__len__():
                self.subCategories.append(category)

            # Iterate over all subcategories
            for subCategory in self.subCategories:
                # Fetch List of all apps present and process them
                self.getApps(subCategory)

            # Clear cache
            self.subCategories.clear()
        self.appList.clear()

    def getCategories(self, soup):
        soup = soup.find('div', {'class': 'action-bar'})
        categories = soup.find_all('a', {'class': 'child-submenu-link'})

        for cat in categories:
            self.categoryLinks.append(self.siteUrl + cat.attrs['href'])

    def getSubCategories(self, categoryPage):
        soup = requestHTML(categoryPage)
        subCats = soup.find_all('a', {'class': 'title-link'})

        for cat in subCats:
            self.subCategories.append(self.siteUrl + cat.attrs['href'])

    def getApps(self, categoryPage):
        soup = self.webDriver.googleScroller(categoryPage)
        if not soup:
            return

        soup = soup.find('div', {'class': 'card-list'})
        apps = soup.find_all('a', {'class': 'title'})

        for app in apps:
            name = app.text.strip()

            if self.appList.get(name):
                self.appList[name] = self.appList[name] + 1
            else:
                self.appList[name] = 1
                self.scrapeApp(self.siteUrl + app.attrs['href'])

    def scrapeApp(self, appPage):
        soup = requestHTML(appPage)
        playData = GoogleData(appPage, soup)

        try:
            data = playData.getAll()
        except (TypeError, IndexError):
            playData.soup = self.webDriver.loadPage(appPage, "//h1[@itemprop='name']")
            data = playData.getAll()

        # TODO Change to write to DB instead of print
        print(data)

        if playData.metaData.get('Price') == "$0.00":
            print('Free')
        #     downloadGoogleApk(playData.metaData.get('Package'))


def main():
    GooglePlay().crawl()


if __name__ == '__main__':
    main()
