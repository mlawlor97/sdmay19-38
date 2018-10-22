from utils import *

maxCategories = 5
maxApps = 1
maxVersions = 3

downloadPath = "C:/CrawlerDownloads/"

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

    counter = 0

    for links in apps:  # Runs 20 apps at a time
        for a in links.find_all("a", href=True):
            linkToVisit = a["href"]
            appName = getAppData(linkToVisit)
            getAllVersions(linkToVisit + "/old", appName)
            if counter >= maxApps - 1: # limit for testing - delete this
                return False
            counter += 1

    if not apps:
        return False
    else:
        return True

def getPermissions(soup):
    soup = 'x'

def getAllVersions(appPage, appName):
    r = requests.get(appPage)
    soup = BeautifulSoup(r.content, "lxml")
    versionList = soup.find_all("div", {"class": "item"})

    counter = 0

    for version in versionList:
        versionName = version.find("span", {"class": "app_card_version"}).text
        writeVersion(versionName, '', '')
        if counter < maxVersions: # limit for testing - delete this
            r2 = requests.get("http:" + version.find("a")["href"])
            downloadPage = BeautifulSoup(r2.content, "lxml")
            downloadLink = downloadPage.find("a", {"class": "data download"})["href"]
            downloadApk(downloadLink, downloadPath)
        counter += 1


def getAppData(appPage):
    r = requests.get(appPage + "/download")
    soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers
    name = ""
    author = ""
    category = ""
    rating = ""
    packageName = ""
    license = ""
    operatingSystem = ""
    requiresAndroid = ""
    language = ""
    size = ""
    permissions = ""
    downloads = ""
    date = ""
    signatureMD5 = ""
    description = ""

    # Name -- good
    breadCrumbs = soup.find("h1", {"class": "name"})
    if breadCrumbs:
        name = breadCrumbs.text
    else:
        logErrorApps("NameCheck.txt", appPage)

    # Author -- good
    authorSoup = soup.find("dt", {"class": "left"}, text="Author")
    if authorSoup:
        author = authorSoup.parent.find("span").text

    # Category -- good
    categorySoup = soup.find("dt", {"class": "left"}, text="Category")
    if categorySoup:
        category = categorySoup.parent.find("a").text

    # Rating -- good
    ratingSoup = soup.find("p", {"class": "star"})
    if ratingSoup:
        rating = ratingSoup.get_text()
    else:
        logErrorApps("RatingCheck.txt", appPage)

    # Package Name -- good
    packageNameSoup = soup.find("li", {"class": "top_li packagename last"})
    if packageNameSoup:
        packageName = packageNameSoup.find("dd").text

    # License -- good
    licenseSoup = soup.find("dt", {"class": "left"}, text="License")
    if licenseSoup:
        license = licenseSoup.parent.find("dd").text

    # OperatingSystem -- good
    operatingSystemSoup = soup.find("dt", {"class": "left"}, text="Op. System")
    if operatingSystemSoup:
        operatingSystem = operatingSystemSoup.parent.find("span").text

    # Requires Android -- good
    requiresAndroidSoup = soup.find("dt", {"class": "left"}, text="Requires Android")
    if requiresAndroidSoup:
        requiresAndroid = requiresAndroidSoup.parent.find("dd").text

    # Language -- TODO
    languageSoup = soup.find("dt", {"class": "left"}, text="Language")
    if languageSoup:
        language = languageSoup.parent.find("span").text
        moreLanguages = languageSoup.parent.find("a")
        if moreLanguages:
            language += " " + moreLanguages.text

    # Size -- good
    sizeSoup = soup.find("dt", {"class": "left"}, text="Size")
    if sizeSoup:
        size = sizeSoup.parent.find("dd").text

    # Permissions -- TODO
    permissionsSoup = soup.find("dt", {"class": "left"}, text="Permissions")
    if permissionsSoup:
        permissions = permissionsSoup.parent.find("dd").text

    # Downloads -- good
    downloadsSoup = soup.find("dt", {"class": "left"}, text="Downloads")
    if downloadsSoup:
        downloads = downloadsSoup.parent.find("dd").text

    # Date -- good
    dateSoup = soup.find("dt", {"class": "left"}, text="Date")
    if dateSoup:
        date = dateSoup.parent.find("dd").text

    # SignatureMD5 -- good
    signatureMD5Soup = soup.find("dt", {"class": "left"}, text="Signature (MD5)")
    if signatureMD5Soup:
        signatureMD5 = signatureMD5Soup.parent.find("dd").text.replace('\n', '')




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

    # write to db when available
    writeOutput(name, author, category, rating, packageName, license, operatingSystem, requiresAndroid, language, size, permissions, downloads, date, signatureMD5, description)

    return name

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


def writeOutput(name, author, category, rating, packageName, license, operatingSystem, requiresAndroid, language, size, permissions, downloads, date, signatureMD5, description):
    # write to file - text for now
    outFile = "UpToDown Crawler Output.txt"
    f = open(outFile, "a")
    f.write(("Name: " + name +
             "\n\tAuthor: " + author +
             "\n\tCategory: " + category +
             "\n\tRating: " + rating + " / 5.0" +
             "\n\tPackage Name: " + packageName +
             "\n\tLicense: " + license +
             "\n\tOperating System: " + operatingSystem +
             "\n\tRequires Android: " + requiresAndroid +
             "\n\tLanguage: " + language +
             "\n\tSize: " + size +
             "\n\tPermissions: " + permissions +
             "\n\tDownloads: " + downloads +
             "\n\tDate: " + date +
             "\n\tSignature (MD5): " + signatureMD5 +
             "\n\tDescription: " + description +
             "\n"))
    f.close()


def writeVersion(version, publishDate, shaValue):
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
        if (counter >= maxCategories - 1):
            return # only do 5 categories for testing - delete
        counter += 1


if __name__ == '__main__':
    main()
