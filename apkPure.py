from utils import RateLimiter, requestHTML, logToFile, removeSpecialChars, createPath, downloadApk, writeOutput
from utils import writeAppDB, writeVersionDB  # DB Connectors
from SupportFiles.webDriverUtils import WebDriver
from SupportFiles.metaDataBase import DataCollectionBase
from SupportFiles.crawlerBase import CrawlerBase


class GetPureData(DataCollectionBase):

    def getDeveloper(self):
        self.tryCollection('Developer', lambda: self.soup.find(class_="details-author").find('a').text.strip())

    def getPackage(self):
        self.tryCollection('Package', lambda: self.url.split('/')[-1])

    def getCategory(self):
        self.tryCollection('Category', lambda: self.soup.find(class_="additional")('span')[-1].text.strip())

    def getDescription(self):
        self.tryCollection('Description', lambda: self.soup.find(class_="content").text)

    def getRating(self):
        self.tryCollection('Rating', lambda: self.soup.find(class_="rating").text.strip())

    def getTags(self):
        self.tryCollection('Tags', lambda: [tag.text for tag in self.soup.find(class_="tag_list")('li') if tag.text])


class GetPureVersion(DataCollectionBase):

    def getType(self):
        self.tryCollection('Apk Type', lambda: self.soup.find(class_="ver-item-t").text.strip())
        self.soup = self.soup.find(class_="ver-info-m")

    def getFileSize(self):
        self.tryCollection('File Size', lambda: str(self.soup.find('strong', string="File Size: ").next_sibling))

    def getRequirements(self):
        self.tryCollection('Requirements', lambda: str(self.soup.find('strong', string="Requires Android: ").next_sibling))

    def getPublishDate(self):
        self.tryCollection('Publish Date', lambda: str(self.soup.find('strong', string="Update on: ").next_sibling))

    def getSignature(self):
        self.tryCollection('Signature', lambda: str(self.soup.find('strong', string="Signature: ").next_sibling).strip())

    def getSHA(self):
        self.tryCollection('SHA', lambda: str(self.soup.find('strong', string="File SHA1: ").next_sibling))

    def getPatchNotes(self):
        patchNotes = self.soup.find(class_='ver-whats-new')
        self.tryCollection('Patch Notes', lambda: patchNotes.text) if patchNotes else None


class GetPureReview(DataCollectionBase):

    def getUser(self):
        self.tryCollection('User', lambda: self.soup.find(class_="author-name").find('span').text.strip())
        return None if self.metaData.get('User') else TypeError

    def getTitle(self):
        self.tryCollection('Title', lambda: self.soup.find(class_="article-title").text.strip(), True)

    def getPublishDate(self):  # TODO Needs work for ...ago times
        self.tryCollection('Publish Date', lambda: self.soup.find(class_="author-time").find('span').text.strip())

    def getReview(self):  # TODO Get links
        emotes = []
        [emotes.append(emote['alt']) for emote in self.soup.find(class_="article")(class_="emojione")]
        self.tryCollection('Message', lambda: self.soup.find(class_="article").text.strip() + ''.join(emotes))

    def getMessageRating(self):
        rating = self.soup.find(class_="cmt-vote")
        self.tryCollection('Message Rating', lambda: 0 if 'Like' in rating.text else int(rating.text.strip()))


# noinspection PyCompatibility
class ApkPure(CrawlerBase):

    def __init__(self, siteUrl="https://apkpure.com", rateLimiter=RateLimiter()):
        super().__init__(siteUrl, rateLimiter)
        self.webDriver      = WebDriver()
        self.categoryLinks  = []
        self.subCategories  = []
        self.currUrl        = siteUrl
        self.AppName        = None

    def crawl(self):
        self.getCategories()
        for category in self.categoryLinks:
            pageNumber = 1
            while self.getAppsOnPage(self.siteUrl + category + '?page=' + pageNumber.__str__()):
                pageNumber += 1

    def loadPage(self, url, verifier):
        self.webDriver.loadPage(url, 'class name', verifier)
        self.webDriver.driver.execute_script('policy_review.setReview();')  # Gets rid of cookie agreement
        self.webDriver.driver.execute_script('document.getElementById("ad-aegon-side").remove()') # Removes QR code
    
    def getCategories(self):
        cats = requestHTML(self.siteUrl + '/app')(class_="index-category")
        [[self.categoryLinks.append(cat['href']) for cat in sect(href=True)] for sect in cats]

    def getAppsOnPage(self, url):
        apps = requestHTML(url)(class_='category-template-title')
        for app in apps:
            self.currUrl = self.siteUrl + app.find('a', href=True)['href']
            self.scrapeAppData(requestHTML(self.currUrl))

            if self.AppName:
                self.currUrl += '/versions'
                self.collectAllVersions()
                # self.collectAllReviews()

        return None if apps.__len__() is 0 else not None

    def scrapeAppData(self, soup):
        try:
            self.AppName = soup.find(class_='title-like').find('h1').text.strip()
        except AttributeError:
            self.AppName = None

        pureData = GetPureData(self.currUrl, soup).getAll()

        id = writeAppDB('ApkPure', self.AppName, pureData.metaData)
        print(id)

    def collectAllVersions(self):
        soup = requestHTML(self.currUrl)
        versionList = soup.find(class_='ver')('li')
        self.scrapeVersions(versionList) if 'Page Deleted' not in soup.title.text else logToFile('versions.txt', self.currUrl + '\n')

    def scrapeVersions(self, versionList):
        index = 0
        self.loadPage(self.currUrl, 'ver')

        for v in versionList:
            if v.find(class_="ver-whats-new"):
                v = self.webDriver.clickPopUp("ver-item-m", "mfp-close", index=index)
                while 'loading..' in v.find(class_='ver-whats-new').text:
                    v = self.webDriver.fetchPage()
                self.webDriver.clickAway("mfp-close", "class name")
                v = v.find(class_='ver-wrap')('li')[index]
                
            version = v.find('span').text.lstrip('V')
            pureVersion = GetPureVersion(self.currUrl, v).getAll()
            writeVersionDB('ApkPure', self.AppName, version, pureVersion.metaData)

            index += 1
            # self.scrapeApk(self.siteUrl + v.find(href=True)['href'], './apks/')  # TODO Uncomment when collecting APKs

    def collectAllReviews(self):
        groupName = removeSpecialChars(self.AppName.lower()).replace(' ', '-')
        reviewsUrl = self.siteUrl + '/group/' + groupName + '?reviews=1&page='
        self.currUrl = self.siteUrl + '/group/' + groupName + '/'

        pageNumber = 1
        while self.scrapeReviews(reviewsUrl + pageNumber.__str__()):
            pageNumber += 1

    def scrapeReviews(self, url):
        reviews = requestHTML(url)('li', class_='cmt-root')
        for review in reviews:
            self.loadPage(self.currUrl + review['id'].lstrip('c'), 'bread-crumbs')
            self.webDriver.loadMore('cmt-more-btn')
            soup = self.webDriver.fetchPage()

            reviewData = GetPureReview(url, soup.select_one('.author')).getAll()
            reviewData.tryCollection('Rating', lambda: review.select_one('.cmt-icon-s-stars')['data-score'], True)
            reviewData.tryCollection('Responses', lambda: self.scrapeResponses(soup.find(id="cmt-reply-data"), []))
            print(reviewData.getJSON())

            # TODO Get rid of once it writes to DB or keep???
            publishDate, user = reviewData.metaData.get('Publish Date'), reviewData.metaData.get('User').replace('/', '')
            destination = './reviews/' + publishDate + '~' + user + '.txt'  # TODO Better naming convention???
            writeOutput(destination=destination, dataDict=reviewData.metaData)

        return None if reviews.__len__() is 0 else not None

    def scrapeResponses(self, soup, responses):
        soup = soup.find('ul', recursive=False)
        if not soup:
            return []
        for response in soup(id=True, recursive=False):
            data = GetPureReview(soup=requestHTML(self.currUrl + response['id'].lstrip('c'))).getAll()
            data.tryCollection('Responses', lambda: self.scrapeResponses(response, []))
            responses.append(data.metaData)
        return responses

    @staticmethod
    def scrapeApk(downloadUrl, savePath):
        soup = requestHTML(url=downloadUrl)

        downloadLink = soup.find(id="download_link")
        if downloadLink:
            fileName = soup.find(class_="file").text.strip()  # TODO Change to better naming convention

            fullPath = createPath(fileName, savePath)
            downloadApk(downloadLink.get('href'), fullPath, fileName, savePath.split('/')[-1])
        else:
            logToFile('APKCheck.txt', downloadUrl + '\n')


def main():
    ApkPure().crawl()


if __name__ == '__main__':
    main()
