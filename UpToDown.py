from utils import *
import unittest
# import mock
import six
import filecmp

sampleDataDirectory = "sample_data"

class UpToDown():

    baseUrl = None
    outFile = None
    testFlag = None

    categoryLimit = None
    appLimitPerCategory = None
    versionLimit = None

    downloadPath = "./APK Files/"

    def __init__(self, baseUrl, outFile, categoryLimit=-1, appLimitPerCategory=-1, versionLimit=-1, testFlag=False):
        self.baseUrl = baseUrl
        self.outFile = outFile
        self.categoryLimit = categoryLimit
        self.appLimitPerCategory = appLimitPerCategory
        self.versionLimit = versionLimit
        self.testFlag = testFlag

    def logErrorApps(self, outputFile, line):
        f = open(outputFile, "a")
        f.write(line + "\n")
        f.close()


    def getCategories(self):
        soup = None
        if (self.testFlag):
            soup = self.readFromLocal(self.baseUrl)
        else:  
            soup = self.readFromOnline(self.baseUrl)

        categoriesToVisit = []

        generalCategories = soup.find_all("div", {"class": "unit"})

        f = open(self.outFile, "a")
        f.write("Categories:\n")

        for links in generalCategories:
            for a in links.find_all("a", href=True, title=True):
                f.write("\t" + a["href"].split('/')[len(a["href"].split('/')) - 1] + "\n")

                # r2 = requests.get(a["href"])
                # soup2 = BeautifulSoup(r2.content, "lxml")
                soup2 = None
                if (self.testFlag):
                    soup2 = self.readFromLocal(a["href"])
                else:  
                    soup2 = self.readFromOnline(a["href"])

                categories = soup2.find_all("div", {"class": "unit"})

                for links2 in categories:
                    for a2 in links2.find_all("a", href=True):
                        f.write("\t\t" + a2["href"].split('/')[len(a2["href"].split('/')) - 1] + "\n")

                        categoriesToVisit.append(a2["href"])

        f.write("\n\n")
        f.close()

        return categoriesToVisit


    def getApps(self, url):
        # r = requests.get(url)
        # soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers
        soup = None
        if (self.testFlag):
            soup = self.readFromLocal(url)
        else:  
            soup = self.readFromOnline(url)

        apps = soup.find_all("div", {"class": "app_card_tit"})

        counter = 0

        for links in apps:  # Runs 20 apps at a time
            for a in links.find_all("a", href=True):
                linkToVisit = a["href"]
                self.getAppData(linkToVisit)
                # try:
                self.getAllVersions(linkToVisit)
                # except:
                    # getSingleVersion(linkToVisit)
                if counter >= self.appLimitPerCategory - 1:
                    return False
                counter += 1

        if not apps:
            return False
        else:
            return True

    def getSingleVersion(self, appPage):
        # r = requests.get(appPage)
        # soup = BeautifulSoup(r.content, "lxml")
        soup = None
        if (self.testFlag):
            soup = self.readFromLocal(appPage)
        else:  
            soup = self.readFromOnline(appPage)

        versionBox = soup.find("a", {"class": "data download"})
        versionName = versionBox.find("p", {"class": "version"}).text

        # r2 = requests.get(appPage + "/download")
        # soup2 = BeautifulSoup(r2.content, "lxml")
        soup2 = None
        if (self.testFlag):
            soup2 = self.readFromLocal(appPage + "/download")
        else:  
            soup2 = self.readFromOnline(appPage + "/download")

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

        self.writeVersion(versionName, languages, permissions)

        downloadLink = soup2.find("a", {"class": "data download"})["href"]
        if (not self.testFlag):
            downloadApk(downloadLink, self.downloadPath)

    def getAllVersions(self, appPage):
        # r = requests.get(appPage + "/old")
        # soup = BeautifulSoup(r.content, "lxml")
        soup = None
        if (self.testFlag):
            soup = self.readFromLocal(appPage + "/old")
        else:  
            soup = self.readFromOnline(appPage + "/old")

        versionList = soup.find_all("div", {"class": "item"})

        counter = 0

        for version in versionList:
            if counter == 0:
                self.getSingleVersion(appPage)
                counter += 1
                continue
            if counter < self.versionLimit:
                versionName = version.find("span", {"class": "app_card_version"}).text
                downloadPageName = "http:" + version.find("a")["href"]
                downloadPage = None
                try:
                    # r2 = requests.get(downloadPageName)
                    downloadPage = None
                    if (self.testFlag):
                        downloadPage = self.readFromLocal(downloadPageName)
                    else:  
                        downloadPage = self.readFromOnline(downloadPageName)
                except:
                    return
                # downloadPage = BeautifulSoup(r2.content, "lxml")

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

                self.writeVersion(versionName, languages, permissions)
                downloadLink = downloadPage.find("a", {"class": "data download"})["href"]
                if (not self.testFlag):
                    downloadApk(downloadLink, self.downloadPath)
            counter += 1


    def getAppData(self, appPage):
        # r = requests.get(appPage + "/download")
        # soup = BeautifulSoup(r.content, "lxml")  # there are faster parsers
        soup = None
        if (self.testFlag):
            soup = self.readFromLocal(appPage + "/download")
        else:  
            soup = self.readFromOnline(appPage + "/download")

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
            self.logErrorApps("NameCheck.txt", appPage)

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
            self.logErrorApps("RatingCheck.txt", appPage)

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
        # r2 = requests.get(appPage)
        # soup2 = BeautifulSoup(r2.content, "lxml")
        soup2 = None
        if (self.testFlag):
            soup2 = self.readFromLocal(appPage)
        else:  
            soup2 = self.readFromOnline(appPage)
        descriptionSoup = soup2.find("div", {"class": "text-description"})
        if descriptionSoup:
            for child in descriptionSoup:
                if child.name != "div" and child.name != "br":
                    description += str(child).replace('\n', ' ')
        else:
            self.logErrorApps("DescriptionCheck.txt", appPage)

        # Permissions -- good
        permissionsSoup = soup.find("dt", {"class": "left"}, text="Permissions")
        if permissionsSoup:
            permissionCount = permissionsSoup.parent.find("dd").text

        # write to db when available
    #     self.writeOutput(outFile, name, author, category, rating, packageName, license, operatingSystem, requiresAndroid, languages, size, downloads, date, signatureMD5, description, permissionCount)

    # def writeOutput(self, outFile, name, author, category, rating, packageName, license, operatingSystem, requiresAndroid, languages, size, downloads, date, signatureMD5, description, permissionCount):
        # write to file - text for now
        # outFile = "UpToDown Crawler Output.txt"
        f = open(self.outFile, "a", encoding="utf-8")
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


    def writeVersion(self, version, languages, permissions):
        # write to file - text for now
        # outFile = "UpToDown Crawler Output.txt"
        f = open(self.outFile, "a")
        f.write(("\t\t" + version + "\n"))
        if languages:
            f.write(("\t\t\tLanguages: " + languages + "\n"))
        if permissions:
            f.write(("\t\t\tPermissions: " + str(len(permissions)) + "\n"))
            for permission in permissions:
                f.write(("\t\t\t" + permission + "\n"))
        f.close()

    def crawl(self):
        
        counter = 0

        categoriesToVisit = self.getCategories()
        for categories in categoriesToVisit:

            if (self.appLimitPerCategory != 0):
                while self.getApps(categories + "/free"):
                    pass
            if (counter == self.categoryLimit - 1):
                return
            counter += 1

    def readFromOnline(self, url):
        r = requests.get(url)
        return BeautifulSoup(r.content, "lxml")  # there are faster parsers

    def readFromLocal(self, fileName):
        fileName = fileName.replace("/", ".")
        fileName = fileName.replace(":", ".")
        f = open("./" + sampleDataDirectory + "/" + fileName + ".html", encoding = "utf8")
        soup = BeautifulSoup(f, "lxml")
        f.close()
        return soup

def main():
    url = "https://en.uptodown.com/android"
    outFile = "UpToDown Crawler Output.txt"

    f = open(outFile, "w")
    f.write("")
    f.close()

    crawler = UpToDown(url, outFile, categoryLimit=3, appLimitPerCategory=1, versionLimit=2, testFlag=False)
    crawler.crawl()

class TestCrawler(unittest.TestCase):

    # with mock.patch('UpToDown.UpToDown.getApps', return_value=False):

    def setUp(self):
        self.outFile = "./" + sampleDataDirectory + "/UpToDown Test Output.txt"
        self.url = "https://en.uptodown.com/android"

    def tearDown(self):
        os.remove(self.outFile)

    def test_categories(self):

        sampleOutputFile = "./" + sampleDataDirectory + "/UpToDown Category Sample.txt"

        f = open(self.outFile, "w")
        f.write("")
        f.close()

        crawler = UpToDown(self.url, self.outFile, categoryLimit=-1, appLimitPerCategory=0, versionLimit=0, testFlag=True)
        crawler.crawl()

        assert filecmp.cmp(self.outFile, sampleOutputFile, shallow=False)


    def test_metadata(self):
        sampleOutputFile = "./" + sampleDataDirectory + "/UpToDown Metadata Sample.txt"

        f = open(self.outFile, "w")
        f.write("")
        f.close()

        crawler = UpToDown(self.url, self.outFile, categoryLimit=3, appLimitPerCategory=1, versionLimit=1, testFlag=True)
        crawler.crawl()

        assert filecmp.cmp(self.outFile, sampleOutputFile, shallow=False)

if __name__ == '__main__':
    unittest.main(exit=False)
    main()
