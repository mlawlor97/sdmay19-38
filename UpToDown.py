from utils import *

# these are for testing purposes only, delete later
maxCategories = 1
maxApps = 4
maxVersions = 2

downloadPath = "./APK Files"

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
            getAppData(linkToVisit)
            # try:
            getAllVersions(linkToVisit)
            # except:
                # getSingleVersion(linkToVisit)
            if counter >= maxApps - 1: # limit for testing - delete this
                return False
            counter += 1

    if not apps:
        return False
    else:
        return True

def getSingleVersion(appPage):
    r = requests.get(appPage)
    soup = BeautifulSoup(r.content, "lxml")

    versionBox = soup.find("a", {"class": "data download"})
    versionName = versionBox.find("p", {"class": "version"}).text

    r2 = requests.get(appPage + "/download")
    soup2 = BeautifulSoup(r2.content, "lxml")

    # Languages - good
    languages = ""
    languageSoup = soup2.find("dt", {"class": "left"}, text="Language")
    if languageSoup:
        languages = languageSoup.parent.find("span").text
        moreLanguageSoup = languageSoup.parent.parent.find("ul", {"class": "list-language"})
        if moreLanguageSoup:
            moreLanguages = moreLanguageSoup.find_all("li")
            for ml in moreLanguages:
                languages += ", " + ml.text

    # Permissions - good
    permissions = []
    permissionsBoxSoup = click(appPage + "/download", "clickable")
    if permissionsBoxSoup:
        permissionBox = permissionsBoxSoup.find("div", {"id": "jbox"})
        permissionList = permissionBox.find_all("div")
        for p in permissionList:
            permissions.append(p.text)

    writeVersion(versionName, languages, permissions)

    downloadLink = soup2.find("a", {"class": "data download"})["href"]
    downloadApk(downloadLink, downloadPath)

def getAllVersions(appPage):
    r = requests.get(appPage + "/old")
    soup = BeautifulSoup(r.content, "lxml")
    versionList = soup.find_all("div", {"class": "item"})

    counter = 0

    for version in versionList:
        if counter == 0:
            getSingleVersion(appPage)
            counter += 1
            continue
        if counter < maxVersions: # limit for testing - delete this
            versionName = version.find("span", {"class": "app_card_version"}).text
            downloadPageName = "http:" + version.find("a")["href"]
            try:
                r2 = requests.get(downloadPageName)
            except:
                return
            downloadPage = BeautifulSoup(r2.content, "lxml")

            # Languages - good
            languages = ""
            languageSoup = downloadPage.find("dt", {"class": "left"}, text="Language")
            if languageSoup:
                languages = languageSoup.parent.find("span").text
                moreLanguageSoup = languageSoup.parent.parent.find("ul", {"class": "list-language"})
                if moreLanguageSoup:
                    moreLanguages = moreLanguageSoup.find_all("li")
                    for ml in moreLanguages:
                        languages += ", " + ml.text

            # Permissions - good
            permissions = []
            permissionsBoxSoup = click(downloadPageName, "clickable")
            if permissionsBoxSoup:
                permissionBox = permissionsBoxSoup.find("div", {"id": "jbox"})
                permissionList = permissionBox.find_all("div")
                for p in permissionList:
                    permissions.append(p.text)

            writeVersion(versionName, languages, permissions)
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
    languages = ""
    size = ""
    permissionCount = ""
    # permissions = []
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

    # Language -- good
    languageSoup = soup.find("dt", {"class": "left"}, text="Language")
    if languageSoup:
        languages = languageSoup.parent.find("span").text
        moreLanguageSoup = languageSoup.parent.parent.find("ul", {"class": "list-language"})
        if moreLanguageSoup:
            moreLanguages = moreLanguageSoup.find_all("li")
            for ml in moreLanguages:
                languages += ", " + ml.text

    # Size -- good
    sizeSoup = soup.find("dt", {"class": "left"}, text="Size")
    if sizeSoup:
        size = sizeSoup.parent.find("dd").text

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

    # Permissions -- good
    permissionsSoup = soup.find("dt", {"class": "left"}, text="Permissions")
    if permissionsSoup:
        permissionCount = permissionsSoup.parent.find("dd").text

    # write to db when available
    writeOutput(name, author, category, rating, packageName, license, operatingSystem, requiresAndroid, languages, size, downloads, date, signatureMD5, description, permissionCount)

def writeOutput(name, author, category, rating, packageName, license, operatingSystem, requiresAndroid, languages, size, downloads, date, signatureMD5, description, permissionCount):
    # write to file - text for now
    outFile = "UpToDown Crawler Output.txt"
    f = open(outFile, "a", encoding="utf-8")
    f.write(("Name: " + name +
             "\n\tAuthor: " + author +
             "\n\tCategory: " + category +
             "\n\tRating: " + rating + " / 5.0" +
             "\n\tPackage Name: " + packageName +
             "\n\tLicense: " + license +
             "\n\tOperating System: " + operatingSystem +
             "\n\tRequires Android: " + requiresAndroid +
             "\n\tLanguages: " + languages +
             "\n\tSize: " + size +
             "\n\tDownloads: " + downloads +
             "\n\tDate: " + date +
             "\n\tSignature (MD5): " + signatureMD5 +
             "\n\tDescription: " + description +
             "\n\tPermissions: " + permissionCount + "\n"))
    f.write(("\tVersions:\n"))
    f.close()


def writeVersion(version, languages, permissions):
    # write to file - text for now
    outFile = "UpToDown Crawler Output.txt"
    f = open(outFile, "a")
    f.write(("\t\t" + version + "\n"))
    if languages:
        f.write(("\t\t\tLanguages: " + languages + "\n"))
    if permissions:
        f.write(("\t\t\tPermissions: " + str(len(permissions)) + "\n"))
        for permission in permissions:
            f.write(("\t\t\t" + permission + "\n"))
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
            return # limit categories for testing - delete
        counter += 1


if __name__ == '__main__':
    main()
