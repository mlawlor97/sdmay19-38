from utils import *
from SupportFiles.apkMirrorData import GetMirrorData
from SupportFiles.crawlerBase import CrawlerBase
from bs4 import Tag, NavigableString
import winsound


class APKMirror(CrawlerBase):

    def crawl(self):
        url = self.siteUrl
        i = 1
        info = []

        #For every developer page
        while i < 27:
            #The first url does not use a numerical indicator
            if i == 1:
                pagesToVisit = getDevPages(url)
            #Otherwise, append the number to the url
            else:
                istr = str(i)
                pagesToVisit = getDevPages(url + "page/" + istr + "/")

            #For every link on the given page
            for link in pagesToVisit:
                #Open the link and get link to every version of app
                o = openPages(link)
                #For every version
                for l in o:
                    print(l)
                    #Get meta data
                    getmetaData(l)
            i += 1
            duration = 1000  # millisecond
            freq = 440  # Hz
            winsound.Beep(freq, duration)



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
    dataSiteDesc = GetMirrorData(url+'#description', soupDesc)
    metaDesc = dataSiteDesc.getDescription()

    dataSite = GetMirrorData(url, soup)
    metaData = dataSite.getAll()
    if not metaData:
        return False
    print(metaData.items())


def openPages(url):
    soup = requestHTML(url)
    urlforPaste = "https://www.apkmirror.com"
    morePagesToVisit = []
    version = soup.find_all("div", {"id": "primary"})

    for elements in version:
        for w in elements.find_all("div", {"class": "listWidget"}):
            for d in w.find_all("div", {"class": "widgetHeader"}):
                if d.text == "All versions ":
                    for innerel in w.find_all("h5", {"class": "appRowTitle wrapText marginZero block-on-mobile"}):
                        a = innerel.find("a", {"class": "fontBlack"})
                        goHere = a.get('href')
                        morePagesToVisit.append(urlforPaste + goHere)
                    for innerel2 in w.find_all("a", {"class": "fontBlack"}):
                        if innerel2.text == "See more uploads...":
                            moreuploads = innerel2.get("href")
                            uArr = seeMoreUploads(urlforPaste+moreuploads)
                            for u in uArr:
                                morePagesToVisit.append(u)
    return morePagesToVisit

def seeMoreUploads(url):
    urlforPaste = "https://www.apkmirror.com"
    soup = requestHTML(url)
    morePagesToVisit = []
    i = 1
    version = soup.find_all("div", {"id": "primary"})
    for elements in version:
        for w in elements.find_all("div", {"class": "listWidget"}):
            for d in w.find_all("div", {"class": "appRow"}):
                if i > 10:
                    if d.find("a", {"class": "fontBlack"}):
                        a = d.find("a", {"class": "fontBlack"})
                        hr = a.get('href')
                        morePagesToVisit.append(urlforPaste+hr)
                i+=1
    return morePagesToVisit


def main():
    limiter = RateLimiter(2, 10)
    url = 'https://www.apkmirror.com/developers/'
    APKMirror(url, limiter).crawl()


if __name__ == '__main__':
    main()
