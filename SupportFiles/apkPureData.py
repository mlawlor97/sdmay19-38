from SupportFiles.metaDataBase import DataCollectionBase
from utils import logToFile


class GetPureData(DataCollectionBase):

    def getName(self):
        try:
            name = self.soup.find('div', {'class': 'title'})
            name = name.find('span').text.replace('/', '').strip()
            self.validApplication = True
        except AttributeError:
            name = None
            logToFile('NameCheck.txt', self.url)
        self.metaData.update(Name=name)

    def getDeveloper(self):
        try:
            dev = self.soup.find('p', {'itemtype': 'http://schema.org/Organization'})
            dev = dev.find('span').text.strip()
        except AttributeError:
            dev = None
            logToFile('DeveloperCheck.txt', self.url)
        self.metaData.update(Developer=dev)

    def getPackage(self):
        try:
            pkg = self.url.split('/')[-1]
        except IndexError:
            pkg = None
            logToFile('PackageCheck.txt', self.url)
        self.metaData.update(Package=pkg)

    def getCategory(self):
        try:
            cat = self.soup.find('div', {'class': 'additional'})
            cat = cat.find_all('span')[-1].text.strip()
        except AttributeError:
            cat = None
            logToFile('CategoryCheck.txt', self.url)
        self.metaData.update(Category=cat)

    def getDescription(self):
        try:
            desc = self.soup.find('div', {'class': 'description'})
            desc = desc.find('div').text
        except AttributeError:
            desc = None
            logToFile('DescriptionCheck.txt', self.url)
        self.metaData.update(Description=desc)

    def getRating(self):
        try:
            rating = self.soup.find('span', {'class': 'rating'})
            rating = rating.text
        except AttributeError:
            if self.validApplication:
                rating = '0.0'
            else:
                rating = None
                logToFile('RatingCheck.txt', self.url)
        self.metaData.update(Rating=rating)

    def getTags(self):
        tags = []
        try:
            tagList = self.soup.find('ul', {'class': 'tag_list'})
            tagList = tagList.find_all('li')
            for tag in tagList:
                if tag.text:
                    tags.append(tag.text)
        except AttributeError:
            tags = None
            logToFile('TagCheck.txt', self.url)
        self.metaData.update(Tags=tags)
