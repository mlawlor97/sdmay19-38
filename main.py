
import requests
import os.path
from bs4 import BeautifulSoup


def logErrorApps(outputFile, line):
    f = open(outputFile, "a")
    f.write(line + "\n")
    f.close()


def getCategories(url):
    r = requests.get(url + "/app")
    soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers

    categoriesToVisit = []

    categories = soup.find_all("ul", {"class": "index-category cicon"})

    for links in categories:
        for a in links.find_all("a", href=True):
            if a.text == "Family":
                continue
            elif a.text:
                categoriesToVisit.append(url + a["href"])

    return categoriesToVisit


def getApps(url, appsToVisit, baseURL):  # also get versions TODO
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers

    apps = soup.find_all("div", {"class": "category-template-title"})
    for links in apps:  # Runs 20 apps at a time
        # appsToVisit.append("https://apkpure.com" + links.contents[0].get("href"))
        getAppData(baseURL, baseURL + links.contents[0].get("href"))

    if not apps:
        return False
    else:
        return True


def getAppData(url, linksToVisit):
    r = requests.get(linksToVisit)
    soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers
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
    breadCrumbs = soup.find("div", {"class": "title bread-crumbs"})
    if breadCrumbs:
        apkName = breadCrumbs.find("span").text
        apkName = apkName.replace("\n", "").replace("/", "_").lstrip().rstrip()
        name = apkName
        flag = 1
    else:
        logErrorApps("NameCheck.txt", linksToVisit)

    # Author -- good
    authorSoup = soup.find("p", {"itemtype": "http://schema.org/Organization"})
    if authorSoup:
        author = authorSoup.text
    else:
        logErrorApps("AuthorCheck.txt", linksToVisit)

    # Version -- good
    versionSoup = soup.find("ul", {"class": "version-ul"})
    versionSoupAlt = soup.find("div", {"class": "details-sdk"})
    if versionSoup:
        version = versionSoup.contents[3].contents[3].text.split(" ", 1)[0]
    elif versionSoupAlt:
        version = versionSoupAlt.text.split(" ", 1)[0]
    else:
        logErrorApps("VersionCheck.txt", linksToVisit)

    # Publish Date -- good
    publishSoup = versionSoup
    publishSoupAlt = soup.find("div", {"class", "additional"})
    if publishSoup:
        publishDate = publishSoup.contents[5].contents[3].text
    elif publishSoupAlt:
        publishDate = publishSoupAlt.contents[1].contents[5].contents[3].text
    else:
        logErrorApps("PublishCheck.txt", linksToVisit)

    # Reviews -- TODO
    #
    # Current idea is to create a folder pertaining to each app
    # then store the reviews there using a filepath to navigate
    # back to them
    #

    # Description -- good
    descriptionSoup = soup.find("div", {"class": "description"})
    if descriptionSoup:
        description = descriptionSoup
    else:
        logErrorApps("DescriptionCheck.txt", linksToVisit)

    # Rating -- good
    ratingSoup = soup.find("span", {"class": "average"})
    if ratingSoup:
        ratings = ratingSoup.contents[0]
    elif flag == 1:
        ratings = "0.0"
    else:
        logErrorApps("RatingCheck.txt", linksToVisit)

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

    f = open("ApkPure Crawler Output.txt", "w")
    f.write("")
    f.close()

    categoriesToVisit = getCategories(url)
    for categories in categoriesToVisit:

        pageNumber = 1
        while getApps((categories + "?page=" + pageNumber.__str__()), appsToVisit, url):
            pageNumber += 1

        # print(categories + ":\t" + len(appsToVisit).__str__())
        # for app in appsToVisit:
        #     getAppData(url, app)


if __name__ == '__main__':
    main()
