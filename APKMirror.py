from utils import *
from SupportFiles.apkMirrorData import GetMirrorData
from SupportFiles.crawlerBase import CrawlerBase


class APKMirror(CrawlerBase):

    def crawl(self):
        url = self.siteUrl
        counter = 0
        i = 1
        # For every developer page
        while i < 27:
            # The first url does not use a numerical indicator
            if i == 1:
                pagesToVisit = getDevPages(url)
            # Otherwise, append the number to the url
            else:
                istr = str(i)
                pagesToVisit = getDevPages(url + "page/" + istr + "/")

            # For every link on the given page
            for link in pagesToVisit:
                # Open the link and get link to every version of app
                o = openPages(link)
                # For every version
                for l in o:
                    counter += 1
                    print("Downloading " + l)
                    # click(l, 'downloadButton')
                    # Get meta data
                    # getmetaData(l)
            i += 1


# This function will go through the list of developers and get links to all of their apps
def getDevPages(url):
    soup = requestHTML(url)
    urlforPaste = "https://www.apkmirror.com"

    pagesToVisit = []

    headers = soup.find_all("div", {"class": "widget_appmanager_developerlistingwidget"})

    for elements in headers:
        h = elements.find("h5", {"class": "widgetHeader"})
        if h.text == "All Developers":
            for innerel in elements.find_all("h5", {"class": "appRowTitle wrapText marginZero block-on-mobile"}):
                a = innerel.find("a", {"class": "fontBlack"})
                goHere = a.get('href')
                pagesToVisit.append(urlforPaste + goHere)
    return pagesToVisit


# This function will open the apps and look to find the link to the page where the app can be downloaded
def openPages(url):
    soup = requestHTML(url)
    urlforPaste = "https://www.apkmirror.com"
    morePagesToVisit = []
    version = soup.find_all("div", {"id": "primary"})

    for elements in version:
        for w in elements.find_all("div", {"class": "listWidget"}):
            for d in w.find_all("div", {"class": "widgetHeader"}):
                if "All" in d.text:
                    for innerel in w.find_all("h5", {"class": "appRowTitle wrapText marginZero block-on-mobile"}):
                        a = innerel.find("a", {"class": "fontBlack"})
                        goHere = a.get('href')
                        correctArr = []
                        correctedLinks = ensureCorrectPage(urlforPaste + goHere)
                        if isinstance(correctedLinks, str):
                            morePagesToVisit.append(correctedLinks)
                        else:
                            for c in correctedLinks:
                                morePagesToVisit.append(c)

                    for innerel2 in w.find_all("a", {"class": "fontBlack"}):
                        if innerel2.text == "See more uploads...":
                            moreuploads = innerel2.get("href")
                            uArr = seeMoreUploads(urlforPaste+moreuploads)
                            for u in uArr:
                                correctedLinks = ensureCorrectPage(u)
                                if isinstance(correctedLinks, str):
                                    morePagesToVisit.append(correctedLinks)
                                else:
                                    for c in correctedLinks:
                                        morePagesToVisit.append(c)
    return morePagesToVisit


# This function is called by openPages() if it detects a "See More Uploads" button,
# meaning there are more versions still to find
def seeMoreUploads(url):
    urlforPaste = "https://www.apkmirror.com"
    soup = requestHTML(url)
    morePagesToVisit = []
    i = 1
    version = soup.find_all("div", {"id": "primary"})
    for elements in version:
        for w in elements.find_all("div", {"class": "listWidget"}):
            for d in w.find_all("div", {"class": "appRow"}):
                if i > 11:
                    if d.find("a", {"class": "fontBlack"}):
                        a = d.find("a", {"class": "fontBlack"})
                        hr = a.get('href')
                        morePagesToVisit.append(urlforPaste+hr)
                i+=1
    return morePagesToVisit


# This function ensures that the page found in openPAges() is a page with a download link
# If not, that indicates the version itself has multiple variants
# If multiple variants are found, the function returns a list of all the variants
# If the page does have a download link, the function will return the original url
def ensureCorrectPage(url):
    urlforPaste = "https://www.apkmirror.com"
    soup = requestHTML(url)

    if soup.find("a", {"class": "btn btn-flat downloadButton"}):
        downloadButton = soup.find("a", {"class": "btn btn-flat downloadButton"}).text

    if soup.find("a", {"class": "btn btn-flat downloadButton variantsButton"}):
        downloadButton = soup.find("a", {"class": "btn btn-flat downloadButton variantsButton"}).text

    if "Download APK" in downloadButton:
        return url

    correctedLinks = []
    variant = soup.find("div", {"class": "variants-table"})

    d = variant.find_all("div", {"class": "table-row headerFont"})

    if len(d) == 2:
        varSearch = d[1].find("a", {"class": None})
        aText = varSearch.get("href")
        correctedLinks.append(urlforPaste + aText)

    else:
        for i in d:
            if i.find("a", {"class": None}):
                aText = i.find("a", {"class": None}).get("href")
                correctedLinks.append(urlforPaste + aText)

    return correctedLinks


# This function will find all the metadata on the given app page
def getmetaData(url):
    soup = requestHTML(url)

    urlforPaste = "https://www.apkmirror.com"


    linkToDownloadLater = soup.find("a", {"class": "btn btn-flat downloadButton variantsButton"})

    if linkToDownloadLater:
        appDetails = soup.find("div", {"class": "table topmargin variants-table"})
        if appDetails:
            newPage = appDetails.find("a", {"class": None}).get("href")
            url = url+newPage
            soup = requestHTML(url + newPage)

    soupDesc = requestHTML(url + '#description')
    dataSite = GetMirrorData(url, soup, DSoup=soupDesc)
    metaData = dataSite.getAll()
    if not metaData:
        return False


def main():
    limiter = RateLimiter(1, 10)
    url = 'https://www.apkmirror.com/developers/'
    APKMirror(url, limiter).crawl()


if __name__ == '__main__':
    main()
