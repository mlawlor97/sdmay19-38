
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
stars = []
apk = []

for items in linksToVisit:
    r = requests.get(items)
    soup = BeautifulSoup(r.content, "html5lib")  # there are faster parsers
    
    # individual info #
    
    # Name
    name.append(soup.find("h1").text)
    
    # Author
    author.append(soup.find("p", {"itemtype": "http://schema.org/Organization"}).text)
    
    # Version
    #
    for version in soup.find_all("ul", {"class": "version-ul"}):
        v = version.contents[3].find_all("p")
#print(v[1].text)

# Publish Date
#

# Reviews
#

# Stars (number / 10)
#

# APk
#
i = 0
while i < len(name):
    print("name: " +name[i], "author: " + author[i])
    i += 1


# write to file - text for now

