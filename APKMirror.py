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

            appName = ""
            # For every link on the given page
            for link in pagesToVisit:
                if "https://" not in link:
                    appName = link
                else:
                    # Open the link and get link to every version of app, this is doing most of the heavy lifting
                    o = openPages(link)
                    # For every version
                    for l in o:
                        counter += 1
                        # print("Version link: " + l)
                        # click(l, 'downloadButton')
                        # Get meta data
                        getmetaData(l, appName)
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
                # Add the name of the base app
                pagesToVisit.append(a.text)
                # Add the link to the app's versions page
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


# This function will create an instance of the GetMirrorData class to find
# all of the metadata on the page
def getmetaData(url, appName):
    soup = requestHTML(url)
    # soupDesc = requestHTML(url + '#description')
    dataSite = GetMirrorData(url, soup)
    metaData = dataSite.getAll()

    print("App Name: " + appName)

    # returns string
    vname = metaData.get("Name")
    print("\tVersion Name: " + vname)

    # returns string
    dev = metaData.get("Developer")
    print("\tDeveloper: " + dev)

    # returns list
    desc = metaData.get("Description")
    print("\tDescription: ")
    for d in desc:
        d = d.replace('\n', '').replace('\r', '')
        if d == "" or d == " ":
            continue
        print("\t\t" + d)

    # returns list
    sec = metaData.get("Security")
    print("\tSecurity: ")
    for s in sec:
        s = s.replace('\n', '').replace('\r', '')
        if s == "" or s == " ":
            continue
        print("\t\t" + s)

    # returns list
    specs = metaData.get("Specs")
    print("\tSpecs: ")
    for sp in specs:
        sp = sp.replace('\n', '').replace('\r', '')
        if sp == "" or sp == " ":
            continue
        print("\t\t" + sp)
    print("\n\n")


    if not metaData:
        return False


def main():
    limiter = RateLimiter(1, 10)
    url = 'https://www.apkmirror.com/developers/'
    APKMirror(url, limiter).crawl()


if __name__ == '__main__':
    main()
