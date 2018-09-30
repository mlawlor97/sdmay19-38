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
                f.write(l)
                f.write("\n")
        i+=1
        duration = 1000  # millisecond
        freq = 440  # Hz
        winsound.Beep(freq, duration)
    f.close()



if __name__ == '__main__':
    main()
