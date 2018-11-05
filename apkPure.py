from utils import *
from SupportFiles.apkPureData import GetPureData
from SupportFiles.crawlerBase import CrawlerBase


class ApkPure(CrawlerBase):

    def crawl(self):
        categories = getCategories(self.siteUrl)
        for category in categories:
            pageNumber = 1
            while getAppsOnPage(category + '?page=' + pageNumber.__str__(), self.siteUrl):
                pageNumber += 1


def getCategories(url):
    """Gets list of all categories on ApkPure

    :param url: Url to search
    :return: List of Categories
    """
    soup = requestHTML(url + '/app')

    categoriesToVisit = []
    categories = soup.find_all('ul', {'class': 'index-category'})

    for section in categories:
        sectionList = section.find_all('a', href=True)
        for category in sectionList:
            if category.text != 'Family':
                categoriesToVisit.append(url + category['href'])

    return categoriesToVisit


def getAppsOnPage(url, baseUrl):
    """Gets of list of the apps displayed on a page and visits each one

    :param url: Url of the page to search
    :param baseUrl: Url of ApkPure
    :return: False if the page has no applications, True otherwise
    """
    soup = requestHTML(url)

    apps = soup.find_all('div', {'class': 'category-template-title'})
    for app in apps:
        link = app.find('a', href=True)
        link = baseUrl + link.get('href')
        appName = scrapeAppData(link)
        if not appName:
            continue

        collectAllVersions(baseUrl, link, './apks/')
        collectAllReviews(baseUrl, appName, './reviews/')

    return apps is not None


def scrapeAppData(appPage):
    """Scrapes all information from the given page that pertains to the application

    :param appPage: Url of the application to scrape
    :return: The name of the application
    """
    soup = requestHTML(appPage)

    dataSite = GetPureData(appPage, soup)
    metaData = dataSite.getAll()
    if not metaData:
        return False
    # print(metaData.items())

    # Want to change to somehow work with list of value pairs
    writeOutput('DB',
                Name=metaData.get('Name'),
                Developer=metaData.get('Developer'),
                Rating=metaData.get('Rating'),
                Description=metaData.get('Description'),
                Package=metaData.get('Package'),
                Category=metaData.get('Category'),
                Tags=metaData.get('Tags'))

    return metaData.get('Name')


def collectAllVersions(url, appPage, savePath):
    """Collects all versions of the specified application

    :param url: Url of ApkPure
    :param appPage: Url of the application
    :param savePath: Where to save apk files
    """
    soup = requestHTML(appPage)
    moreVersions = soup.find('div', {'class': 'ver-title'})

    if moreVersions and moreVersions.contents[3]:
        soup = requestHTML(appPage + '/versions')

    format1 = soup.find('ul', {'class': 'ver-wrap'})
    format2 = soup.find('div', {'class': 'faq_cat'})

    if format1:
        scrapeVersionsA(url, format1, savePath, appPage)
    elif format2:
        scrapeVersionsB(url, format2, savePath)
    else:
        logToFile('versions.txt', appPage + '\n')


def scrapeVersionsA(url, versionList, savePath, appPage):
    """Collects all versions of the specified application that has formatA

    :param url: Url of ApkPure
    :param versionList: list of all versions
    :param appPage: Url of the application
    :param savePath: Where to save apk files
    """
    versionList = versionList.find_all('li')
    index = 0
    for v in versionList:
        downloadLink = v.contents[1].attrs['href']
        v = v.contents[3]
        version = v.contents[1].contents[1].split(' ')[1]
        v = v.contents[3]

        soup = click(appPage + '/versions', 'ver-item-m', index)

        try:
            changelog = soup.find_all('div', {'class': 'ver-whats-new'})[0].text
        except IndexError:
            changelog = 'NO CHANGELOG PRESENT'
        index += 1

        writeOutput('DB', 'a',
                    Version=version,
                    FileSize=v.contents[9].contents[1],
                    Requirements=v.contents[3].contents[1],
                    PublishDate=v.contents[1].contents[1],
                    Signature=v.contents[5].contents[1].strip(),
                    SHA=v.contents[7].contents[1],
                    Changelog=changelog)

        scrapeApk(url + downloadLink, savePath)


def scrapeVersionsB(url, versionList, savePath):
    """Collects all versions of the specified application that is in formatB

        :param url: Url of ApkPure
        :param versionList: list of all versions
        :param savePath: Where to save apk files
        """
    versionList = versionList.find_all('dd')
    for v in versionList:
        downloadLinks = v.find_all('a', {'class': 'down'})
        v = v.find_all('strong')
        tags = []
        index = 0

        for tag in v:
            try:
                tag.parent.contents[1].text
            except AttributeError:
                tags.append(tag.parent.contents[1].strip())

        try:
            changelog = v[-1].parent.contents[1].text
        except AttributeError:
            changelog = ''

        for link in downloadLinks:
            size = link.contents[1].text.replace('(', '').replace(')', '')
            sha = tags[3] if tags.__len__() == 4 else tags[3 + index]

            writeOutput('DB', 'a',
                        Version=tags[0].split(' ')[0],
                        FileSize=size,
                        Requirements=tags[0].split('for ')[1],
                        PublishDate=tags[1],
                        Signature=tags[2],
                        SHA=sha,
                        Changelog=changelog)

            scrapeApk(url + link.attrs['href'], savePath)


def collectAllReviews(url, appName, savePath):
    """Collects all reviews for specified application

    :param url: Url for ApkPure
    :param appName: Url for the application
    :param savePath: Where to save the reviews
    """
    groupName = removeSpecialChars(appName.lower())
    groupName = groupName.replace(' ', '-')

    pageNumber = 1
    reviewsUrl = url + '/group/' + groupName + '?reviews=1&page='

    while scrapeReviewsOnPage(reviewsUrl, pageNumber, savePath):
        pageNumber += 1


def scrapeReviewsOnPage(url, pageNumber, savePath):
    """Gets all reviews on the specified page

    :param url: Url for application's reviews
    :param pageNumber: Page to scrape
    :param savePath: Where to save reviews
    :return: False if there are no reviews present, True otherwise
    """
    url = url + pageNumber.__str__()
    soup = requestHTML(url)

    reviews = soup.find_all('li', {'class': 'cmt-root'})

    for review in reviews:
        publishDate = review.contents[1].contents[3].contents[1].contents[1].text.strip()

        try:
            msgRating = int(review.contents[1].contents[3].contents[1].contents[7].text.strip())
        except ValueError:
            msgRating = 0
        review = review.contents[1].contents[1]
        user = review.contents[3].contents[1].text.strip()

        destination = savePath + '/' + publishDate + '~' + user.replace('/', '') + '.txt'
        # writeOutput(destination,
        #             User=user,
        #             Message=review.contents[5].text.strip(),
        #             Rating=review.contents[3].contents[1].contents[3].attrs['data-score'],
        #             PublishDate=publishDate,
        #             MessageRating=msgRating)

    if reviews:
        return True
    else:
        return False


def scrapeApk(url, savePath):
    """Finds download link for the apk file and downloads it

    :param url: Url of download page
    :param savePath: Where to save the apk file
    """
    soup = requestHTML(url)

    downloadLink = soup.find('a', {'id': 'download_link'})
    if downloadLink:
        apk = downloadLink.get('href')
        fileName = soup.find('span', {'class': 'file'}).contents[0].lstrip().rstrip()

        fullPath = createPath(savePath, fileName)
        downloadApk(apk, fullPath, fileName, savePath.split('/')[-1])
    else:
        logToFile('APKCheck.txt', url + '\n')


def main():
    limiter = RateLimiter(0, 0)
    url = 'https://apkpure.com'
    ApkPure(url, limiter).crawl()


if __name__ == '__main__':
    main()
