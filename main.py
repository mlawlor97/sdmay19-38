import requests
import os.path
from bs4 import BeautifulSoup


def getCategories(url):
    r = requests.get(url + "/app")
    soup = BeautifulSoup(r.content, "html5lib")  # there are faster parsers

    categoriesToVisit = []

    categories = soup.find_all("ul", {"class": "index-category cicon"})

    for links in categories:
        for a in links.find_all("a", href=True):
            if a.text == "Family":
                continue
            elif a.text:
                categoriesToVisit.append(url + a["href"])

    return categoriesToVisit


# also get versions TODO
def getApps(url, appsToVisit):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html5lib")  # there are faster parsers

    apps = soup.find_all("div", {"class": "category-template-title"})
    for links in apps:
        appsToVisit.append("https://apkpure.com" + links.contents[0].get("href"))

    if (soup.find("a", {"class": "loadmore"})):
        link = soup.find("a", {"class": "loadmore"})
        getApps("https://apkpure.com" + link.get("href"), appsToVisit)


def getAppData(url, linksToVisit):
    r = requests.get(linksToVisit)
    soup = BeautifulSoup(r.content, "html5lib")  # there are faster parsers
    flag = 0
    apkName = ""
    name = ""
    author = ""
    version = ""
    publishDate = ""
    reviews = ""
    ratings = ""
    description = ""

    # Name -- good
    if (soup.find("div", {"class": "title-like"})):
        apkName = soup.find("div", {"class": "title-like"}).text
        apkName = apkName.replace("\n", "").replace("/", "_").lstrip().rstrip()
        name = apkName
        flag = 1
    else:
        outFile = "NameCheck.txt"
        f = open(outFile, "a")
        f.write(linksToVisit + "\n")
        f.close()

    # Author -- good
    if (soup.find("p", {"itemtype": "http://schema.org/Organization"})):
        author= soup.find("p", {"itemtype": "http://schema.org/Organization"}).text
    else:
        outFile = "AuthorCheck.txt"
        f = open(outFile, "a")
        f.write(linksToVisit + "\n")
        f.close()

    # Version -- good
    if (soup.find("div", {"class": "details-sdk"})):
        version = soup.find("div", {"class": "details-sdk"}).text.split(" ", 1)[0]
    elif (soup.find("ul", {"class": "version-ul"})):
        version = soup.find("ul", {"class": "version-ul"}).contents[3].contents[3].text.split(" ", 1)[0]
    else:
        outFile = "VersionCheck.txt"
        f = open(outFile, "a")
        f.write(linksToVisit + "\n")
        f.close()

    # Publish Date -- good
    if (soup.find("ul", {"class": "version-ul"})):
        pubSub = soup.find("ul", {"class": "version-ul"}).contents[5]
        publishDate = pubSub.contents[3].text
    elif (soup.find("div", {"class", "additional"})):
        publishDate = soup.find("div", {"class", "additional"}).contents[1].contents[5].contents[3].text
    else:
        outFile = "PublishCheck.txt"
        f = open(outFile, "a")
        f.write(linksToVisit + "\n")
        f.close()

    # Reviews -- TODO
    #

    # Description -- good
    if (soup.find("div", {"class": "description"})):
        description = soup.find("div", {"class": "description"})
    else:
        outFile = "DescriptionCheck.txt"
        f = open(outFile, "a")
        f.write(linksToVisit + "\n")
        f.close()

    # Rating -- good
    if (soup.find("span", {"class": "average"})):
        ratings = soup.find("span", {"class": "average"}).contents[0]
    elif (flag == 1):
        ratings = "0"
    else:
        outFile = "RatingCheck.txt"
        f = open(outFile, "a")
        f.write(linksToVisit + "\n")
        f.close()

    getAPK(linksToVisit, apkName)

    # write to db when available
    writeOutput(name, author, version, publishDate, reviews, ratings, description)


# APk -- sha info TODO
def getAPK(url, name):
    savePath = "./apks"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html5lib")  # there are faster parsers

    if (soup.find("a", {"class": " da"})):
        linkToDownload =  soup.find("a", {"class": " da"}).get("href")
        newRequest = requests.get("https://apkpure.com" + linkToDownload)
        newSoup = BeautifulSoup(newRequest.content, "html5lib")
        if (newSoup.find("a", {"id": "download_link"})):
            apk = newSoup.find("a", {"id": "download_link"})["href"]
            fileName = newSoup.find("span", {"class": "file"}).contents[0]

            session = requests.Session()
            s = session.get(apk)

            completeName = os.path.join(savePath, fileName)
            file = open(completeName, "wb")
            file.write(s.content)
            file.close()
    else:
        outFile = "APKCheck.txt"
        f = open(outFile, "a")
        f.write(url + "\n")
        f.close()


def writeOutput(name, author, version, publishDate, reviews, ratings, description):
    # write to file - text for now
    outFile = "ApkPure Crawler Output.txt"
    f = open(outFile, "a")
    f.write(("Name: " + name +
            "\n\tAuthor: " + author +
            "\n\tVersion: " + version +
            "\n\tPublish Date: " + publishDate +
            "\n\tRating: " + ratings + " / 10.0" +
            "\n"))
    f.close()


def main():
    url = "https://apkpure.com"
    appsToVisit = []

    categoriesToVisit = getCategories(url)
    for categories in categoriesToVisit:
        getApps(categories, appsToVisit)
        for app in appsToVisit:
            getAppData(url, app)


if __name__ == '__main__':
    main()
