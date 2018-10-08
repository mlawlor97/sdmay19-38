import requests
import os.path
from bs4 import BeautifulSoup


def logErrorApps(outputFile, line):
    f = open(outputFile, "a")
    f.write(line + "\n")
    f.close()


def getCategories(url):
    outFile = "UpToDown Crawler Output.txt"

    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers

    categoriesToVisit = []

    generalCategories = soup.find_all("div", {"class": "unit"})

    f = open(outFile, "a")
    f.write("Categories:\n")

    for links in generalCategories:
        for a in links.find_all("a", href=True, title=True):
            f.write("\t" + a["href"].split('/')[len(a["href"].split('/')) - 1] + "\n")

            r2 = requests.get(a["href"])
            soup2 = BeautifulSoup(r2.content, "lxml")

            categories = soup2.find_all("div", {"class": "unit"})

            for links2 in categories:
                for a2 in links2.find_all("a", href=True):
                    f.write("\t\t" + a2["href"].split('/')[len(a2["href"].split('/')) - 1] + "\n")

                    categoriesToVisit.append(a2["href"])

    f.write("\n\n")
    f.close()

    return categoriesToVisit


def getApps(url, baseURL):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers

    apps = soup.find_all("div", {"class": "app_card_tit"})
    for links in apps:  # Runs 20 apps at a time
        for a in links.find_all("a", href=True):
            linkToVisit = a["href"]
            getAppData(linkToVisit)
            getAllVersions(linkToVisit + "/old")
            return False # limit to one for testing - delete this

    if not apps:
        return False
    else:
        return True


def getAllVersions(appPage):
    r = requests.get(appPage)
    soup = BeautifulSoup(r.content, "lxml")
    versionList = soup.find_all("span", {"class": "app_card_version"})
    for version in versionList:
        writeAllVersions(version.get_text(), '', '')
    # versionList = soup.find("ul", {"class": "ver-wrap"})  # format 1
    # versionListAlt = soup.find("div", {"class": "faq_cat"})  # format 2
    # if versionList:
    #     versionList = versionList.findAll("li")
    #     for version in versionList:
    #         writeAllVersions(version.contents[3].contents[1].contents[1].split(' ')[1],
    #                          version.contents[3].contents[3].contents[1].contents[1],
    #                          version.contents[3].contents[3].contents[7].contents[1])
    #         getAPK(version.contents[1].attrs['href'])
    # elif versionListAlt:
    #     versionListAlt = versionListAlt.findAll("dd")
    #     for version in versionListAlt:
    #         downloadLink = version.find("a", {"class": " down"})
    #         writeAllVersions(version.contents[1].contents[1].split(' ')[0],
    #                          version.contents[3].contents[1],
    #                          version.contents[7].contents[1])
    #         getAPK(downloadLink.attrs['href'])
    # else:
    #     logErrorApps("versions.txt", appPage)


def getAppData(appPage):
    r = requests.get(appPage + "/download")
    soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers
    flag = 0
    name = ""
    author = ""
    reviews = ""
    ratings = ""
    description = ""

    # Name -- good
    breadCrumbs = soup.find("h1", {"class": "name"})
    if breadCrumbs:
        name = breadCrumbs.text
        flag = 1
    else:
        logErrorApps("NameCheck.txt", appPage)

    # Author -- good
    authorSoup = soup.find("div", {"class": "author"})
    if authorSoup:
        authorSpan = authorSoup.find("span")
        author = authorSpan.text
    else:
        logErrorApps("AuthorCheck.txt", appPage)

    # Reviews -- TODO
    #
    # Current idea is to create a folder pertaining to each app
    # then store the reviews there using a filepath to navigate
    # back to them
    #

    # Description -- good
    r2 = requests.get(appPage)
    soup2 = BeautifulSoup(r2.content, "lxml")
    descriptionSoup = soup2.find("div", {"class": "text-description"})
    if descriptionSoup:
        for child in descriptionSoup:
            if child.name != "div" and child.name != "br":
                description += str(child).replace('\n', ' ')
    else:
        logErrorApps("DescriptionCheck.txt", appPage)

    # Rating -- good
    ratingSoup = soup.find("p", {"class": "star"})
    if ratingSoup:
        ratings = ratingSoup.get_text()
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
    outFile = "UpToDown Crawler Output.txt"
    f = open(outFile, "a")
    f.write(("Name: " + name +
             "\n\tAuthor: " + author +
             "\n\tRating: " + ratings + " / 5.0" +
             "\n\tDescription: " + description +
             "\n"))
    f.close()


def writeAllVersions(version, publishDate, shaValue):
    # write to file - text for now
    outFile = "UpToDown Crawler Output.txt"
    f = open(outFile, "a")
    f.write(("\t\tVersion: " + version +
            #  "\n\t\tPublish Date: " + publishDate +
            #  "\n\t\tSha Value: " + shaValue +
             "\n"))
    f.close()


def main():
    url = "https://en.uptodown.com/android"

    outFile = "UpToDown Crawler Output.txt"
    f = open(outFile, "w")
    f.write("")
    f.close()

    counter = 0

    categoriesToVisit = getCategories(url)
    for categories in categoriesToVisit:

        while getApps(categories + "/free", url):
            print("")
        if (counter >= 4):
            return # only do 5 categories for testing - delete
        counter += 1


if __name__ == '__main__':
    main()
