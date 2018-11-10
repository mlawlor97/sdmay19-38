from utils import *
from SupportFiles.crawlerBase import CrawlerBase
from SupportFiles.fDroidData import FDroidData


class FDroid(CrawlerBase):

    def crawl(self):
        getAllPages(self.siteUrl)


def getAllPages(url):
    pageNumber = 1
    while getAppsOnPage(url, pageNumber, '/en/packages/'):
        pageNumber += 1


def getAppsOnPage(url, pageNumber, extension):
    if pageNumber is not 1:
        extension = extension + pageNumber.__str__()
    soup = requestHTML(url + extension + '/index.html')
    try:
        appList = soup.find('div', {'id': 'full-package-list'})
        appList = appList.find_all('a', {'class': 'package-header'})
    except AttributeError:
        return False

    for app in appList:
        link = app.get('href')
        link = url + link
        appName = scrapeAppData(link)
        if appName is None:
            continue

        savePath = makeDirectory('apks/')
        collectAllVersions(url, link, savePath + 'apks/', appName)

    return True


def scrapeAppData(appPage):
    soup = requestHTML(appPage)

    dataSite = FDroidData(appPage, soup)
    metaData = dataSite.getAll()
    if not metaData:
        return None

    writeOutput('DB',
                Name=metaData.get('Name'),
                Developer=metaData.get('Developer'),
                Description=metaData.get('Description'))

    return metaData.get('Name')


def collectAllVersions(url, appPage, savePath, appName):
    soup = requestHTML(appPage)
    versionList = soup.find('ul', {'class': 'package-versions-list'})
    versionList = versionList.find_all('li', {'class': 'package-version'})
    for version in versionList:
        # Get Version Number
        versionNum = version.find('a').get('name').strip()

        # Get Publish Date
        pubDate = version.find('div', {'class': 'package-version-header'})
        pubDate = pubDate.text.strip().split(' ')[-1]

        # Get Permissions
        permissions = []
        permissionList = version.find('ul', {'class': 'package-version-permissions-list'}).find_all('li')
        for perm in permissionList:
            permissions.append(perm.text.strip())

        writeOutput('DB',
                    Version=versionNum,
                    PublishDate=pubDate,
                    Permissions=permissions)

        # Get Apk
        fullPath = createPath(savePath, appName + '-' + versionNum)
        downloadLink = version.find('p', {'class': 'package-version-download'})
        downloadLink = downloadLink.find('a').get('href')
        downloadApk(downloadLink, fullPath)


def main():
    limiter = RateLimiter(1, 0.5)
    url = 'https://f-droid.org'
    FDroid(url, limiter).crawl()


if __name__ == '__main__':
    main()
