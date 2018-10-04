import requests
import os.path
from bs4 import BeautifulSoup


def logErrorApps(outputFile, line):
    f = open(outputFile, "a")
    f.write(line + "\n")
    f.close()


def getCategories(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers

    categoriesToVisit = []

    categories = soup.find_all("div", {"class": "unit"})

    for links in categories:
        for a in links.find_all("a", href=True):
            if a.text == "Family":
                continue
            elif a.text:
                categoriesToVisit.append(url + a["href"])

    print(categoriesToVisit)
    return categoriesToVisit


def getApps(url, baseURL):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers

    apps = soup.find_all("div", {"class": "category-template-title"})
    for links in apps:  # Runs 20 apps at a time
        linkToVisit = baseURL + links.contents[0].get("href")
        getAppData(linkToVisit)
        getAllVersions(url, linkToVisit)

    if not apps:
        return False
    else:
        return True


def getAllVersions(url, appPage):
    r = requests.get(appPage)
    soup = BeautifulSoup(r.content, "lxml")
    versionList = soup.find("ul", {"class": "ver-wrap"})  # format 1
    versionListAlt = soup.find("div", {"class": "faq_cat"})  # format 2
    if versionList:
        versionList = versionList.findAll("li")
        for version in versionList:
            writeAllVersions(version.contents[3].contents[1].contents[1].split(' ')[1],
                             version.contents[3].contents[3].contents[1].contents[1],
                             version.contents[3].contents[3].contents[7].contents[1])
            getAPK(url + version.contents[1].attrs['href'])
    elif versionListAlt:
        versionListAlt = versionListAlt.findAll("dd")
        for version in versionListAlt:
            downloadLink = version.find("a", {"class": " down"})
            writeAllVersions(version.contents[1].contents[1].split(' ')[0],
                             version.contents[3].contents[1],
                             version.contents[7].contents[1])
            getAPK(url + downloadLink.attrs['href'])
    else:
        logErrorApps("versions.txt", appPage)


def getAppData(appPage):
    r = requests.get(appPage)
    soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers
    flag = 0
    name = ""
    author = ""
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
        logErrorApps("NameCheck.txt", appPage)

    # Author -- good
    authorSoup = soup.find("p", {"itemtype": "http://schema.org/Organization"})
    if authorSoup:
        author = authorSoup.text
    else:
        logErrorApps("AuthorCheck.txt", appPage)

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
        logErrorApps("DescriptionCheck.txt", appPage)

    # Rating -- good
    ratingSoup = soup.find("span", {"class": "average"})
    if ratingSoup:
        ratings = ratingSoup.contents[0]
    elif flag == 1:
        ratings = "0.0"
    else:
        logErrorApps("RatingCheck.txt", appPage)

    # getAPK(linksToVisit)

    # write to db when available
    writeOutput(name, author, reviews, ratings, description)


def getAPK(url):
    savePath = "./apks"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html5lib")  # there are faster parsers

    if soup.find("a", {"class": " da"}):
        linkToDownload = soup.find("a", {"class": " da"}).get("href")
        newRequest = requests.get("https://apkpure.com" + linkToDownload)
        newSoup = BeautifulSoup(newRequest.content, "html5lib")
        if newSoup.find("a", {"id": "download_link"}):
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


def writeOutput(name, author, reviews, ratings, description):
    # write to file - text for now
    outFile = "ApkPure Crawler Output.txt"
    f = open(outFile, "a")
    f.write(("Name: " + name +
             "\n\tAuthor: " + author +
             "\n\tRating: " + ratings + " / 10.0" +
             "\n\tVersions:"
             "\n"))
    f.close()


def writeAllVersions(version, publishDate, shaValue):
    # write to file - text for now
    outFile = "ApkPure Crawler Output.txt"
    f = open(outFile, "a")
    f.write(("\t\tVersion: " + version +
             "\n\t\tPublish Date: " + publishDate +
             "\n\t\tSha Value: " + shaValue +
             "\n"))
    f.close()


def main():
    url = "https://en.uptodown.com/android"

    f = open("UpToDown Crawler Output.txt", "w")
    f.write("")
    f.close()

    categoriesToVisit = getCategories(url)
    for categories in categoriesToVisit:

        pageNumber = 1
        while getApps((categories + "?page=" + pageNumber.__str__()), url):
            pageNumber += 1


if __name__ == '__main__':
    main()
