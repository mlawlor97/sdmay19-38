from utils import *


def getCategories(url):
    soup = requestHTML(url + '/app')

    categoriesToVisit = []
    categories = soup.find_all('ul', {'class': 'index-category'})

    for section in categories:
        sectionList = section.find_all('a', href=True)
        for category in sectionList:
            if category.text != 'Family':
                categoriesToVisit.append(url + category['href'])

    return categoriesToVisit


def getAppsOnPage(url, baseUrl):
    soup = requestHTML(url)

    apps = soup.find_all('div', {'class': 'category-template-title'})
    for app in apps:
        # Test Data
        # link = 'https://apkpure.com/frontline-commando-d-day/com.glu.flcn_new'
        # link = 'https://apkpure.com/call-of-duty-black-ops-iii/com.waqardev.shooting3'
        # link = 'https://apkpure.com/dealspure/com.dealspure.wild'

        link = baseUrl + app.contents[0].get('href')
        appName = scrapeAppData(link)
        savePath = makeDirectory(appName)

        collectAllVersions(baseUrl, link, savePath + 'apks/' + appName)
        collectAllReviews(baseUrl, appName, savePath + 'reviews/' + appName)

    if apps:
        return True
    else:
        return False


def scrapeAppData(appPage):
    soup = requestHTML(appPage)
    flag = 0
    name = author = ratings = description = packageName = category = ''
    tags = []

    # Name -- good
    breadCrumbs = soup.find("div", {"class": "title bread-crumbs"})
    if breadCrumbs:
        name = breadCrumbs.find("span").text.replace("/", "_").strip()
        flag = 1
    else:
        logToFile("NameCheck.txt", appPage + '\n')

    # Author -- good
    authorSoup = soup.find("p", {"itemtype": "http://schema.org/Organization"})
    if authorSoup:
        author = authorSoup.text
    else:
        logToFile("AuthorCheck.txt", appPage + '\n')

    # Category -- good
    categorySoup = soup.find("div", {"class": "additional"})
    if categorySoup:
        category = categorySoup.find("a").contents[2].text
    else:
        logToFile("CategoryCheck.txt", appPage + '\n')

    # Description -- good
    descriptionSoup = soup.find("div", {"class": "description"})
    if descriptionSoup:
        description = descriptionSoup.contents[3].text
    else:
        logToFile("DescriptionCheck.txt", appPage + '\n')

    # Rating -- good
    ratingSoup = soup.find("span", {"class": "average"})
    if ratingSoup:
        ratings = ratingSoup.contents[0]
    elif flag == 1:
        ratings = "0.0"
    else:
        logToFile("RatingCheck.txt", appPage + '\n')

    # Package Name
    if appPage.split('/').__len__() >= 5:
        packageName = appPage.split("/")[4]

    # Application Tags
    tagList = soup.find("ul", {"class": "tag_list"})
    if tagList:
        tagList = tagList.find_all("li")
        for tag in tagList:
            if tag.text:
                tags.append(tag.text)

    writeOutput('DB',
                Name=name,
                Developer=author,
                Rating=ratings,
                Description=description,
                Package=packageName,
                Category=category,
                Tags=tags)

    return name


def collectAllVersions(url, appPage, savePath):
    soup = requestHTML(appPage)
    moreVersions = soup.find('div', {'class': 'ver-title'})

    if moreVersions and moreVersions.contents[3]:
        soup = requestHTML(appPage + '/versions')

    format1 = soup.find('ul', {'class': 'ver-wrap'})
    format2 = soup.find('div', {'class': 'faq_cat'})

    if format1:
        scrapeVersionsA(url, format1, savePath, appPage)
    elif format2:
        scrapeVersionsB(url, format2, savePath)
    else:
        logToFile('versions.txt', appPage + '\n')


def scrapeVersionsA(url, versionList, savePath, appPage):
    versionList = versionList.find_all('li')
    index = 0
    for v in versionList:
        downloadLink = v.contents[1].attrs['href']
        v = v.contents[3]
        version = v.contents[1].contents[1].split(' ')[1]
        v = v.contents[3]

        soup = click(appPage, 'ver-item-m', index)

        try:
            changelog = soup.find_all('div', {'class': 'ver-whats-new'})[0].text
        except IndexError:
            changelog = ''
        index += 1

        writeOutput('DB', 'a',
                    Version=version,
                    FileSize=v.contents[9].contents[1],
                    Requirements=v.contents[3].contents[1],
                    PublishDate=v.contents[1].contents[1],
                    Signature=v.contents[5].contents[1].strip(),
                    SHA=v.contents[7].contents[1],
                    Changelog=changelog)

        # TODO I want to thread this
        scrapeApk(url + downloadLink, savePath)


def scrapeVersionsB(url, versionList, savePath):
    versionList = versionList.find_all('dd')
    for v in versionList:
        downloadLinks = v.find_all('a', {'class': 'down'})
        v = v.find_all('strong')
        tags = []
        index = 0

        for tag in v:
            try:
                tag.parent.contents[1].text
            except AttributeError:
                tags.append(tag.parent.contents[1].strip())

        try:
            changelog = v[-1].parent.contents[1].text
        except AttributeError:
            changelog = ''

        for link in downloadLinks:
            size = link.contents[1].text.replace('(', '').replace(')', '')

            sha = tags[3] if tags.__len__() == 4 else tags[3 + index]
            index += 1

            writeOutput('DB', 'a',
                        Version=tags[0].split(' ')[0],
                        FileSize=size,
                        Requirements=tags[0].split('for ')[1],
                        PublishDate=tags[1],
                        Signature=tags[2],
                        SHA=sha,
                        Changelog=changelog)

            scrapeApk(url + link.attrs['href'], savePath)


def collectAllReviews(url, appName, savePath):
    groupName = removeSpecialChars(appName.lower())
    groupName = groupName.replace(' ', '-')

    pageNumber = 1
    reviewsUrl = url + '/group/' + groupName + '?reviews=1&page='

    while scrapeReviewsOnPage(reviewsUrl, pageNumber, savePath):
        pageNumber += 1


def scrapeReviewsOnPage(url, pageNumber, savePath):
    url = url + pageNumber.__str__()
    soup = requestHTML(url)

    reviews = soup.find_all('li', {'class': 'cmt-root'})

    for review in reviews:
        review = review.contents[1]
        user = review.contents[1].contents[3].contents[1].text.strip()
        message = review.contents[1].contents[5].text.strip()
        rating = review.contents[1].contents[3].contents[1].contents[3].attrs['data-score']
        publishDate = review.contents[3].contents[1].contents[1].text.strip()

        try:
            msgRating = int(review.contents[3].contents[1].contents[7].text.strip())
        except ValueError:
            msgRating = 0

        destination = savePath + '/' + publishDate + '~' + user.replace('/', '') + '.txt'
        writeOutput(destination,
                    User=user,
                    Message=message,
                    Rating=rating,
                    PublishDate=publishDate,
                    MessageRating=msgRating)

    if reviews:
        return True
    else:
        return False


def scrapeApk(url, savePath):
    soup = requestHTML(url)

    downloadLink = soup.find('a', {'id': 'download_link'})
    if downloadLink:
        apk = downloadLink.get('href')
        fileName = soup.find('span', {'class': 'file'}).contents[0]

        s = downloadApk(apk)

        fullPath = createPath(savePath, fileName)
        logToFile(fullPath, s, 'wb')
    else:
        logToFile('APKCheck.txt', url + '\n')


def main():
    siteURL = 'https://apkpure.com'
    outputDestination = 'ApkPure Crawler Output.txt'

    logToFile(outputDestination, '', 'w')

    categories = getCategories(siteURL)
    for category in categories:
        pageNumber = 1
        while getAppsOnPage(category + '?page=' + pageNumber.__str__(), siteURL):
            pageNumber += 1


if __name__ == '__main__':
    main()
