#!usr/bin/env python3

from utils import RateLimiter, requestHTML, writeAppDB
from SupportFiles.webDriverUtils import WebDriver
from SupportFiles.crawlerBase import CrawlerBase
from SupportFiles.metaDataBase import DataCollectionBase
# from googleplayapi.googleplay import GooglePlayAPI
# from PlayCrawlerMaster.googleplayapi.googleplay import GooglePlayAPI

class GoogleData(DataCollectionBase):

    # def getName(self):
    #     self.tryCollection('name', lambda: self.soup.find(itemprop='name').text.strip(), True)
    #     return False if self.metaData.get('Name') is ('' or None) else None

    def getPackage(self):
        self.tryCollection('package', lambda: self.url.split('id=')[-1].split('&')[0])
        # self.soup = self.soup.select('[data-p~=\"' + self.metaData.get('Package') + '\"]')

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

    def getVersion(self):
        self.tryCollection('version', lambda: self.soup.find('div', string="Current Version").next_sibling.find('span').text)

    def getNumDownloads(self):
        self.tryCollection('downloads', lambda: self.soup.find('div', string="Installs").next_sibling.find('span').text)

    def getSize(self):
        self.tryCollection('size', lambda: self.soup.find('div', string="Size").next_sibling.find('span').text)

    def getRequirements(self):
        self.tryCollection('requirements', lambda: self.soup.find('div', string='Requires Android').next_sibling.find('span').text)

    def getPublishDate(self):
        self.tryCollection('publish_date', lambda: self.soup.find('div', string='Updated').next_sibling.find('span').text)

    def getPatchNotes(self):
        self.tryCollection('patch_notes', lambda: self.soup.find('h2', string="What's New").parent.next_sibling.find('content').text)


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
        # self.gpa = GooglePlayAPI(androidId="551F187F79FC41F3", lang="en_us")
        # self.gpa.login("sdmay19@gmail.com", "Forensics4", "ya29.GluuBvrVmzeVYn1HxKQ_61nKGKjDfSXB_7uQ_LPvg8EWceabszVZn5e5VDHuZNF_Zbh_R3BviPmrMV-DSDSR0Ipc_qfmVU3NX8C31RZi34ecakBd4NJEJZpp8brY")

    def __del__(self):
        self.webDriver.__del__()

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
        soup = soup.find(id="action-dropdown-children-Categories")
        [self.categoryLinks.append(cat['href']) for cat in soup(href=True)]

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
                try:
                    self.scrapeApp(self.siteUrl + app.attrs['href'])
                except:
                    continue

    def scrapeApp(self, appPage):
        soup = requestHTML(appPage)
        name = soup.find(itemprop='name')

        if not name:
            soup = self.webDriver.loadPage(appPage, 'xpath', "//h1[@itemprop='name']", True)
            name = soup.find(itemprop='name')
        name = name.text.strip()
        playData = GoogleData(appPage, soup).getAll()

        # print((playData.metaData))
        # package = playData.metaData.get("package")

        id_ = writeAppDB("GooglePlay", name, appPage, playData.metaData) 
        print(id_)       

        # if playData.metaData.get('price') == "$0.00":
            # print('Free')
            # details = self.gpa.details(package)
            # print(details)
        #     downloadGoogleApk(playData.metaData.get('Package'))


def main():
    GooglePlay().crawl()
    # GooglePlay().scrapeApp('https://play.google.com/store/apps/details?id=com.snapchat.android')
    # url = 'https://play.google.com/store/apps/details?id=de.ritterit.lukes&hl=en'
    # url = 'https://play.google.com/store/apps/details?id=com.thomson.cxn&feature=more_from_developer#?t=W251bGwsMSwyLDEwMiwiY29tLnRob21zb24uY3huIl0.'
    # url = 'https://play.google.com/store/apps/details?id=com.salamandertechnologies.track&hl=en_US'
    # url = 'https://play.google.com/store/apps/details?id=com.harris.rf.beonptt.android.ui&hl=en'
    # url = 'https://play.google.com/store/apps/details?id=gov.nih.nlm.erg2012&hl=en_US'
    # url = 'https://play.google.com/store/apps/details?id=com.cube.arc.hfa'
    # url = 'https://play.google.com/store/apps/details?id=gov.fema.mobile.android'
    # url = 'https://play.google.com/store/apps/details?id=com.snap.android.apis'
    # url = 'https://play.google.com/store/apps/details?id=com.intergraph.mobileresponder'
    # GooglePlay().scrapeApp(url)


if __name__ == '__main__':
    main()
