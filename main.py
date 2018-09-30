import requests
import os.path
from bs4 import BeautifulSoup



def getDevPages(url):
    r = requests.get(url + "/developers/")
    soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers

    pagesToVisit = []

    headers = soup.find_all("div", {"class": "widget_appmanager_developerlistingwidget"})

    for elements in headers:
        h = elements.find("h5", {"class": "widgetHeader"})
        if h.text == "All Developers":
            for innerel in elements.find_all("h5", {"class": "appRowTitle wrapText marginZero block-on-mobile"}):
                a = innerel.find("a", {"class": "fontBlack"})
                goHere = a.get('href')
                pagesToVisit.append(url + goHere)
    return pagesToVisit


def openPages(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers
    morePagesToVisit = []
    version = soup.find_all("div", {"id": "primary"})

    for elements in version:
        for w in elements.find_all("div", {"class": "listWidget"}):
            for d in w.find_all("div", {"class": "widgetHeader"}):
                if d.text == "All versions ":
                    for innerel in w.find_all("h5", {"class": "appRowTitle wrapText marginZero block-on-mobile"}):
                        a = innerel.find("a", {"class": "fontBlack"})
                        goHere = a.get('href')
                        morePagesToVisit.append(url + goHere)
    return morePagesToVisit

def main():
    url = "https://www.apkmirror.com"

    f = open("ApkMirror Crawler Output.txt", "w")
    f.write("")
    f.close()

    pagesToVisit = getDevPages(url)
    outFile = "ApkMirror Crawler Output.txt"
    f = open(outFile, "a")
    for link in pagesToVisit:
        o = openPages(link)
        for l in o:
            f.write(l)
            f.write("\n")

    f.close()



if __name__ == '__main__':
    main()
