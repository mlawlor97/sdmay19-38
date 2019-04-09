from utils import *
from SupportFiles.apkMirrorData import GetMirrorData
from SupportFiles.crawlerBase import CrawlerBase
from SupportFiles.metaDataBase import DataCollectionBase
from SupportFiles.apkMirrorAppData import GetMirrorAppData




class MirrorData(DataCollectionBase):

    def Dev(self):
        price = self.soup.find(itemprop='price', content=True)['content']
        return price if price != "0" else "$0.00"

class GoogleVersion(DataCollectionBase):

    def Dev(self):
        price = self.soup.find(itemprop='price', content=True)['content']
        return price if price != "0" else "$0.00"



class APKMirror(CrawlerBase):

    def crawl(self):
        url = self.siteUrl
        counter = 0
        i = 1
        # For every developer page
        while i < 27:
            # The first url does not use a numerical indicator
            if i == 1:
                pagesToVisit = getDevPages(url)
            # Otherwise, append the number to the url
            else:
                istr = str(i)
                pagesToVisit = getDevPages(url + "page/" + istr + "/")

            appName = ""
            # For every link on the given page
            for link in pagesToVisit:
                # Check if it's a link or an app name
                if "https://" not in link:
                    appName = link
                else:
                    # Open the link and get link to every version of app, this is doing most of the heavy lifting
                    o = openPages(link, appName)
                    doAppData = True
                    # For every version
                    for l in o:
                        counter += 1
                        # print("Version link: " + l)
                        # click(l, 'downloadButton')
                        # Get meta data
                        getmetaData(l, appName, doAppData, link)
                        if doAppData is True:
                            doAppData = False




            i += 1


# This function will go through the list of developers and get links to all of their apps
def getDevPages(url):
    soup = requestHTML(url)
    urlforPaste = "https://www.apkmirror.com"

    pagesToVisit = []

    headers = soup.find_all("div", {"class": "widget_appmanager_developerlistingwidget"})

    for elements in headers:
        h = elements.find("h5", {"class": "widgetHeader"})
        if h.text == "All Developers":
            for innerel in elements.find_all("h5", {"class": "appRowTitle wrapText marginZero block-on-mobile"}):
                a = innerel.find("a", {"class": "fontBlack"})
                goHere = a.get('href')
                # Add the name of the base app
                pagesToVisit.append(a.text)
                # Add the link to the app's versions page
                pagesToVisit.append(urlforPaste + goHere)
    return pagesToVisit


# This function will open the apps and look to find the link to the page where the app can be downloaded
def openPages(url, appName):
    soup = requestHTML(url)
    urlforPaste = "https://www.apkmirror.com"
    morePagesToVisit = []
    version = soup.find_all("div", {"id": "primary"})

    for elements in version:
        for w in elements.find_all("div", {"class": "listWidget"}):
            for d in w.find_all("div", {"class": "widgetHeader"}):
                if "All" in d.text:
                    for innerel in w.find_all("h5", {"class": "appRowTitle wrapText marginZero block-on-mobile"}):
                        a = innerel.find("a", {"class": "fontBlack"})
                        goHere = a.get('href')
                        correctedLinks = ensureCorrectPage(urlforPaste + goHere)
                        if isinstance(correctedLinks, str):
                            morePagesToVisit.append(correctedLinks)
                        else:
                            for c in correctedLinks:
                                morePagesToVisit.append(c)

                    for innerel2 in w.find_all("a", {"class": "fontBlack"}):
                        if innerel2.text == "See more uploads...":
                            moreuploads = innerel2.get("href")
                            uArr = seeMoreUploads(urlforPaste+moreuploads)
                            for u in uArr:
                                correctedLinks = ensureCorrectPage(u)
                                if isinstance(correctedLinks, str):
                                    morePagesToVisit.append(correctedLinks)
                                else:
                                    for c in correctedLinks:
                                        morePagesToVisit.append(c)
    return morePagesToVisit


# This function is called by openPages() if it detects a "See More Uploads" button,
# meaning there are more versions still to find
def seeMoreUploads(url):
    urlforPaste = "https://www.apkmirror.com"
    soup = requestHTML(url)
    morePagesToVisit = []
    i = 1
    version = soup.find_all("div", {"id": "primary"})
    for elements in version:
        for w in elements.find_all("div", {"class": "listWidget"}):
            for d in w.find_all("div", {"class": "appRow"}):
                if i > 11:
                    if d.find("a", {"class": "fontBlack"}):
                        a = d.find("a", {"class": "fontBlack"})
                        hr = a.get('href')
                        morePagesToVisit.append(urlforPaste+hr)
                i+=1
    return morePagesToVisit


# This function ensures that the page found in openPAges() is a page with a download link
# If not, that indicates the version itself has multiple variants
# If multiple variants are found, the function returns a list of all the variants
# If the page does have a download link, the function will return the original url
def ensureCorrectPage(url):
    urlforPaste = "https://www.apkmirror.com"
    soup = requestHTML(url)

    if soup.find("a", {"class": "btn btn-flat downloadButton"}):
        downloadButton = soup.find("a", {"class": "btn btn-flat downloadButton"}).text

    if soup.find("a", {"class": "btn btn-flat downloadButton variantsButton"}):
        downloadButton = soup.find("a", {"class": "btn btn-flat downloadButton variantsButton"}).text

    if "Download APK" in downloadButton:
        return url

    correctedLinks = []
    variant = soup.find("div", {"class": "variants-table"})

    d = variant.find_all("div", {"class": "table-row headerFont"})

    if len(d) == 2:
        varSearch = d[1].find("a", {"class": None})
        aText = varSearch.get("href")
        correctedLinks.append(urlforPaste + aText)

    else:
        for i in d:
            if i.find("a", {"class": None}):
                aText = i.find("a", {"class": None}).get("href")
                correctedLinks.append(urlforPaste + aText)

    return correctedLinks


# This function will create an instance of the GetMirrorData class to find
# all of the metadata on the page
def getmetaData(url, appName, doAppData, appLink):
    soup = requestHTML(url)
    # soupDesc = requestHTML(url + '#description')
    dataSite = GetMirrorData(url, soup).getAll()

    vname = metaData.get("Name")
    dev = metaData.get("Developer")
    pkg = metaData.get("Package")


    if doAppData is True:
        soupApp = requestHTML(appLink)
        appDataSite = GetMirrorAppData(appLink, soupApp).getAll()
        idApp = writeAppDB("APKMirror", appName, url, pkg, appDataSite.metaData)

    idVersion = writeVersionDB("APKMirror", appName, idApp, vname, dataSite.metaData)



    if not metaData:
        return False


# Returns list of hashes in order:
# Certificate SHA-1, Certificate SHA-256, File MD5, File SHA-1, File SHA-256
def splitSecurity(sec):
    cert_sha1_index = sec.find('SHA-1')
    cert_sha2_index = sec.find('SHA-256')
    end_cert = sec.find('The cryptographic')

    split_sec = sec[end_cert:]

    file_md5_index = split_sec.find('MD5')
    file_sha1_index = split_sec.find('SHA-1')
    file_sha2_index = split_sec.find('SHA-256')
    end_file = split_sec.find('Verify the file')

    cert_sha1 = sec[cert_sha1_index+7:cert_sha2_index]
    cert_sha2 = sec[cert_sha2_index+9:end_cert]

    file_md5 = split_sec[file_md5_index+5:file_sha1_index]
    file_sha1 = split_sec[file_sha1_index+7:file_sha2_index]
    file_sha2 = split_sec[file_sha2_index + 9:end_file]

    security_data = [cert_sha1, cert_sha2, file_md5, file_sha1, file_sha2]
    return security_data


# Returns app specs in order:
# Version number, Architecture, Package, Number of Downloads, File Size,
# Minimum Android Version, Target Android Version, and Upload Date
def splitSpecs(spec):
    find_architecture = False
    version_index = spec.find(')')
    package_index = spec.find('Package')
    if package_index - version_index > 1:
        architecture_index = spec.find('arm')
        find_architecture = True

    downloads_index = spec.find('downloads')
    size_index = spec.find('bytes)')
    min_android_index = spec.find('Min:')
    target_android_index = spec.find('Target:')

    version = spec[10:version_index+1]

    if find_architecture is True:
        architecture = spec[architecture_index:package_index-1]
    else:
        architecture = "No architecture found"

    download_sub = spec[package_index:downloads_index]
    real_downloads_index = 0

    for i, c in enumerate(reversed(download_sub)):
        if c.isalpha():
            real_downloads_index = i-1
            break
    package = spec[package_index+9:package_index+len(download_sub)-real_downloads_index-1]
    downloads = spec[package_index+len(download_sub)-real_downloads_index-1:downloads_index-1]

    size = spec[downloads_index+10:size_index+6]

    min_android = spec[min_android_index+5:target_android_index-1]

    target_android_temp_sub = spec[target_android_index:]
    target_android_end_index = target_android_temp_sub.find(')')
    target_android = target_android_temp_sub[8:target_android_end_index+1]

    uploaded_date_index = target_android_temp_sub.find('Uploaded')

    uploaded_end_index = target_android_temp_sub.find(' at ')

    uploaded_date = target_android_temp_sub[uploaded_date_index+9:uploaded_end_index]

    spec_data = [version, architecture, package, downloads, size, min_android, target_android, uploaded_date]
    return spec_data


def main():
   limiter = RateLimiter(1, 10)
   url = 'https://www.apkmirror.com/developers/'
   APKMirror(url, limiter).crawl()


if __name__ == '__main__':
    main()
