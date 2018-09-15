
import requests
from bs4 import BeautifulSoup

url = "https://apkpure.com"

r = requests.get(url + "/app")
soup = BeautifulSoup(r.content, "html5lib") #there are faster parsers

linksToVisit = []

apps = soup.find_all("div", {"class": "category-template-title"})
for links in apps:
    linksToVisit.append(url + links.contents[0].get("href"))

name = []
author = []
version = []
publishDate = []
reviews = []
ratings = []
apk = []

for items in linksToVisit:
    r = requests.get(items)
    soup = BeautifulSoup(r.content, "html5lib")  # there are faster parsers
    
    # individual info #
    
    # Name
    # name.append(soup.find("h1").text)
    previousPages = soup.find("div", {"class": "title bread-crumbs"})
    name.append(previousPages.find("span").text);
    
    # Author
    author.append(soup.find("p", {"itemtype": "http://schema.org/Organization"}).text)
    
    # Version
    #
    # for versions in soup.find("ul", {"class": "version-ul"}):
    #     v = versions.contents[3].find_all("p")
    #     version.append(v[1].contents[0])

    v = soup.find("ul", {"class": "version-ul"})
    vAlt = soup.find("div", {"class": "details-sdk"})
    if v:   # Standard Format for latest version
        vSub = v.contents[3]
        version.append(vSub.contents[3].text)
    elif vAlt:  # Version Format that is sometimes used
        vAltSub = vAlt.contents[0]
        version.append(vAltSub.contents[0])
    else:   # Case where multiple versions can be selected from another page
        versionLink = soup.find("a", {"class", "ny-versions"})
        if versionLink:
            versionRequest = requests.get(url + versionLink.attrs['href'])
            vSoup = BeautifulSoup(versionRequest.content, "html5lib")
            currentVersion = vSoup.find("span", {"class", "ver-item-n"})
            version.append(currentVersion.contents[0])

# Publish Date
#
    pub = v
    if pub:  # Standard Format for publish date
        pubSub = pub.contents[5]
        publishDate.append(pubSub.contents[3].text)
    else:
        publishDate.append("TODO")

# Reviews
#


# Rating (number / 10)
#
    rating = soup.find("span", {"class": "average"})
    if rating:
        ratings.append(rating.contents[0])
    else:   # Does not execute (Error Catching)
        ratings.append("rating is not standart format")

# APk
#
# i = 0
# while i < len(name):
#     print("Name: " + name[i] + ".", "Author: " + author[i])
#     i += 1


# write to file - text for now
outFile = "ApkPure Crawler Output.txt"
f = open(outFile, "w")
i = 0
while i < len(name):
    f.write(("Name: " + name[i] +
             "\n\tAuthor: " + author[i] +
             "\n\tVersion: " + version[i] +
             "\n\tPublish Date: " + publishDate[i] +
             "\n\tRating: " + ratings[i] + " / 10.0" +
             "\n"))
    i += 1

f.close()

