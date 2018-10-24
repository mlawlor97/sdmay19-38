import requests
import os.path
from bs4 import BeautifulSoup, Tag, NavigableString
import time
import winsound

def getDevPages(url):
    time.sleep(5)
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
    time.sleep(5)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers

    urlforPaste = "https://www.apkmirror.com"

    linkToDownloadLater = soup.find("a", {"class": "btn btn-flat downloadButton variantsButton"})

    if linkToDownloadLater:
        appDetails = soup.find("div", {"class": "table topmargin variants-table"})
        if appDetails:
            newPage = appDetails.find("a", {"class": None}).get("href")
            r = requests.get(url + newPage)
            soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers

    headerContents = soup.find("div", {"class": "site-header-contents"})
    info = []


    if headerContents.find("h1", {"class": "marginZero wrapText app-title fontBlack noHover"}):
        t = headerContents.find("h1", {"class": "marginZero wrapText app-title fontBlack noHover"})
        info.append(t.text)

    if headerContents.find("h3", {"class": "marginZero dev-title wrapText"}):
        n = headerContents.find("h3", {"class": "marginZero dev-title wrapText"})
        a = n.find("a", {"class": None})
        info.append(a.text)



    metaData = soup.find_all("div", {"class": "appspec-value"})

    if metaData:
        for m in metaData:
            if isinstance(m, NavigableString):
                info.append(m)
            else:
                info.append(m.text)

    shaAndSig = soup.find_all("div", {"class": "modal-body"})
    check = 0;
    if shaAndSig:
        for s in shaAndSig[1]:
            if isinstance(s, NavigableString):
                info.append(s)
            else:
                info.append(s.text)
    #linkToDownloadNow = soup.find("a", {"class": "btn btn-flat downloadButton"})



    # if linkToDownloadNow:
    #     apk = linkToDownloadNow.get("href")
    #     session = requests.Session()
    #     testURl = urlforPaste+apk
    #     s = session.get(urlforPaste+apk)
    #
    #     filename = info[0]
    #     file = open(filename, "wb")
    #     file.write(s.content)
    #     file.close()



    # else:
    #     outFile = "APKCheck.txt"
    #     f = open(outFile, "a")
    #     f.write(url + "\n")
    #     f.close()
    return info

def seeMoreUploads(url):
    time.sleep(5)
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
    time.sleep(5)
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

    f = open("ApkMirror Crawler OutputNew.txt", "w")
    f.write("")
    f.close()
    outFile = "ApkMirror Crawler OutputNew.txt"
    i=0
    j=1
    pagesToVisit = []
    info = []
    while i<2:
        if i == 1:
            pagesToVisit = getDevPages(url)
        else:
            istr = str(i)
            pagesToVisit = getDevPages(url+"page/"+istr+"/")
        if (i==1):
            #for link in pagesToVisit:
            #o = openPages(link)
            o = openPages(pagesToVisit[0])
            for l in o:
                infoTemp = getDataTitle(l)
                for it in infoTemp:
                     info.append(it)
        i+=1
        duration = 1000  # millisecond
        freq = 440  # Hz
        winsound.Beep(freq, duration)

        counter = 1
        f = open(outFile, "a")
        for idx, item in enumerate(info):
            item = item.replace("\n", "")
            if "Supports" in item:
                continue
            # f.write(item + "\n")
            if counter == 1:
                f.write("Application Name: " + item + "\n")
                counter+=1
            elif counter == 2:
                f.write("\tAuthor: " + item + "\n")
                counter += 1
            elif counter == 3:
                index = item.index('P')
                item = item[:index] + "\n\t" + item[index:]
                indexNew = 0;
                itemNew = item[index:]
                for j, c in enumerate(itemNew):
                    if c.isdigit():
                        indexNew = j
                        break
                item = item[:index+indexNew] +"\n\t" +item[index+indexNew:]
                f.write("\t" + item + "\n")
                counter += 1
            elif counter == 4:
                f.write("\tSize: " + item + "\n")
                counter += 1
            elif counter == 5:
                f.write("\t" + item + "\n")
                counter += 1
            elif counter == 6:
                f.write("\tSupported DPIs: " + item + "\n")
                counter += 1
            elif counter == 7:
                counter += 1
                continue
            elif counter == 8:
                f.write("\t" + item + "\n")
                counter += 1
            elif counter == 9 or counter == 10 or counter==11 or counter ==12:
                counter += 1
                continue
            elif counter == 13:
                f.write("\t" + item + " ")
                counter += 1
            elif counter == 14:
                f.write(item + "\n")
                counter += 1
            elif counter == 15:
                counter+=1
                continue
            elif counter == 16:
                f.write("\t" + item + " ")
                counter += 1
            elif counter == 17:
                f.write(item + "\n")
                counter += 1
            elif counter == 18 or counter == 19 or counter == 20 or counter == 21 or counter == 24 or counter == 27 or counter == 30 or counter == 31:
                counter+=1
                continue
            elif counter == 22:
                f.write("\t" + item + " ")
                counter += 1
            elif counter == 23:
                f.write(item + "\n")
                counter += 1
            elif counter == 25:
                f.write("\t" + item + " ")
                counter += 1
            elif counter == 26:
                f.write(item + "\n")
                counter += 1
            elif counter == 28:
                f.write("\t" + item + " ")
                counter += 1
            elif counter == 29:
                f.write(item + "\n\n")
                counter += 1
            else:
                counter = 1
                continue



            #item = item.replace("\n", "")
            # if (idx == 0):
            #     f.write("Name: " + item + "\n")
            # elif (idx == 1):
            #     f.write("\t" + "Author: " + item + "\n")
            # else:
            #     if (idx % 2 == 0):
            #         f.write("Name: " + item + "\n")
            #     else:
            #         f.write("\t" + "Author: " + item + "\n")

        f.close()





if __name__ == '__main__':
    main()
