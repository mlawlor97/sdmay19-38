import requests
import os.path
from bs4 import BeautifulSoup


def logErrorApps(outputFile, line):
    f = open(outputFile, "a")
    f.write(line + "\n")
    f.close()


def logReview(savePath, user, message, rating, publishDate, messageRating):
    outputFile = savePath + '/' + user + '~' + publishDate + '.txt'
    f = open(outputFile, "w")
    f.write("Message: " + message +
            "\nRating: " + rating +
            "\nPublish Date: " + publishDate +
            "\nMessage Rating: " + messageRating.__str__())
    f.close()


def makeDirectory(appName):
    savePath = os.getcwd() + "/"

    try:
        os.mkdir(savePath + "reviews/")
        os.mkdir(savePath + "apks/")
    except OSError:
        print("Failed to create directory %s " % savePath)
    else:
        print("Successfully created the directory %s " % savePath)

    try:
        os.mkdir(savePath + "reviews/" + appName)
        os.mkdir(savePath + "apks/" + appName)
    except OSError:
        print("Failed to create directory %s " % savePath)
    else:
        print("Successfully created the directory %s " % savePath)

    return savePath


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


def getApps(url, baseURL):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers

    apps = soup.find_all("div", {"class": "category-template-title"})
    for links in apps:  # Runs 20 apps at a time
        linkToVisit = baseURL + links.contents[0].get("href")
        appName = getAppData(linkToVisit)
        savePath = makeDirectory(appName)
        getAllVersions(baseURL, linkToVisit, savePath + "apks/" + appName)
        getAllReviews(baseURL, appName, savePath + "reviews/" + appName)

    if apps:
        return True
    else:
        return False


def getAllVersions(url, appPage, savePath):
    r = requests.get(appPage)
    soup = BeautifulSoup(r.content, "lxml")
    moreVersions = soup.find("div", {"class": "ver-title"})

    if moreVersions and moreVersions.contents[3]:
        versionPage = appPage + '/versions'
        r = requests.get(versionPage)
        soup = BeautifulSoup(r.content, "lxml")
    versionList = soup.find("ul", {"class": "ver-wrap"})  # format 1
    versionListAlt = soup.find("div", {"class": "faq_cat"})  # format 2
    if versionList:
        versionList = versionList.findAll("li")
        for version in versionList:
            downloadLink = version.contents[1].attrs['href']
            version = version.contents[3]
            writeAllVersions(version.contents[1].contents[1].split(' ')[1],
                             version.contents[3].contents[1].contents[1],
                             version.contents[3].contents[7].contents[1])
            getAPK(url + downloadLink, savePath)

    elif versionListAlt:
        versionListAlt = versionListAlt.findAll("dd")
        for version in versionListAlt:
            downloadLink = version.find("a", {"class": " down"}).attrs['href']
            writeAllVersions(version.contents[1].contents[1].split(' ')[0],
                             version.contents[3].contents[1],
                             version.contents[7].contents[1])
            getAPK(url + downloadLink, savePath)

    else:
        logErrorApps("versions.txt", appPage)


def getPageReviews(savePath, url, pageNumber):
    url = url + pageNumber.__str__()
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")

    reviews = soup.find_all("li", {"class": "cmt-root"})

    for review in reviews:
        review = review.contents[1]
        user = review.contents[1].contents[3].contents[1].text.strip()
        message = review.contents[1].contents[5].text.strip()
        rating = review.contents[1].contents[3].contents[1].contents[3].get("data-score")
        publishDate = review.contents[3].contents[1].contents[1].text.strip()

        try:
            messageRating = int(review.contents[3].contents[1].contents[7].text.strip())
        except ValueError:
            messageRating = 0

        logReview(savePath, user, message, rating, publishDate, messageRating)

    if reviews:
        return True
    else:
        return False


def getAllReviews(url, appName, savePath):
    groupName = appName.lower().replace(' ', '-')
    pageNumber = 1
    reviewsUrl = url + '/group/' + groupName + "?reviews=1&page="

    while getPageReviews(savePath, reviewsUrl, pageNumber):
        pageNumber += 1
    return


def getAppData(appPage):
    r = requests.get(appPage)
    soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers
    flag = 0
    name = ""
    author = ""
    ratings = ""
    description = ""
    packageName = ""
    category = ""

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

    # Category -- good
    categorySoup = soup.find("div", {"class": "additional"})
    if categorySoup:
        categorySoup = categorySoup.find("a")
        category = categorySoup.contents[2].text
    else:
        logErrorApps("CategoryCheck.txt", appPage)

    # Description -- good
    descriptionSoup = soup.find("div", {"class": "description"})
    if descriptionSoup:
        description = descriptionSoup.contents[3].text
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

    # Package Name
    if appPage.split('/').__len__() >= 5:
        packageName = appPage.split("/")[4]

    # write to db when available
    writeOutput(name, author, ratings, description, packageName, category)

    return name


def getAPK(url, savePath):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers
    linkToDownload = soup.find("a", {"id": "download_link"})

    if linkToDownload:
        apk = linkToDownload.get("href")
        fileName = soup.find("span", {"class": "file"}).contents[0]

        session = requests.Session()
        s = session.get(apk)

        completeName = os.path.join(savePath, fileName)
        file = open(completeName, "wb")
        file.write(s.content)
        file.close()
    else:
        logErrorApps("APKCheck.txt", url)


def writeOutput(name, author, ratings, description, packageName, category):
    # write to file - text for now
    outFile = "ApkPure Crawler Output.txt"
    f = open(outFile, "a")
    f.write(("Name: " + name +
             "\n\tAuthor: " + author +
             "\n\tCategory: " + category +
             "\n\tRating: " + ratings + " / 10.0" +
             "\n\tPackage Name: " + packageName +
             "\n\tDescription: " + description +
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
    url = "https://apkpure.com"

    f = open("ApkPure Crawler Output.txt", "w")
    f.write("")
    f.close()

    categoriesToVisit = getCategories(url)
    for categories in categoriesToVisit:

        pageNumber = 1
        while getApps((categories + "?page=" + pageNumber.__str__()), url):
            pageNumber += 1


if __name__ == '__main__':
    main()
