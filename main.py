import requests
from bs4 import BeautifulSoup
import time
import winsound

def getDevPages(url):
    time.sleep(1)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers
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



def getDataTitle(url):
    time.sleep(1)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers
    headerContents = soup.find("div", {"class": "site-header-contents"})

    t = headerContents.find("h1", {"class": "marginZero wrapText app-title fontBlack noHover"})
    return t.text







def seeMoreUploads(url):
    time.sleep(1)
    r = requests.get(url)
    urlforPaste = "https://www.apkmirror.com"
    soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers
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

def openPages(url):
    time.sleep(1)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers
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

def main():
    url = "https://www.apkmirror.com/developers/"

    f = open("ApkMirror Crawler Output.txt", "w")
    f.write("")
    f.close()
    outFile = "ApkMirror Crawler Output.txt"
    f = open(outFile, "a")
    i=1
    pagesToVisit = []
    while i<28:
        if i == 1:
            pagesToVisit = getDevPages(url)
        else:
            istr = str(i)
            pagesToVisit = getDevPages(url+"page/"+istr+"/")
        for link in pagesToVisit:
            o = openPages(link)
            for l in o:
                tit = getDataTitle(l)
                f.write(tit)
                f.write("\n")
        i+=1
        duration = 1000  # millisecond
        freq = 440  # Hz
        winsound.Beep(freq, duration)
    f.close()



if __name__ == '__main__':
    main()
