from SupportFiles.metaDataBase import DataCollectionBase
from utils import logToFile
from bs4 import Tag, NavigableString


class GetMirrorData(DataCollectionBase):

    def getName(self):
        try:
            headerContents = self.soup.find("div", {"class": "site-header-contents"})
            if headerContents.find("h1", {"class": "marginZero wrapText app-title fontBlack noHover"}):
                t = headerContents.find("h1", {"class": "marginZero wrapText app-title fontBlack noHover"})
                name = t.text
        except AttributeError:
            name = None
            logToFile('NameCheck.txt', self.url)
        self.metaData.update(Name=name)

    def getDeveloper(self):
        try:
            headerContents = self.soup.find("div", {"class": "site-header-contents"})
            if headerContents.find("h3", {"class": "marginZero dev-title wrapText"}):
                n = headerContents.find("h3", {"class": "marginZero dev-title wrapText"})
                a = n.find("a", {"class": None})
                dev = a.text
        except AttributeError:
            dev = None
            logToFile('DeveloperCheck.txt', self.url)
        self.metaData.update(Developer=dev)

    # def getPackage(self):
    #     try:
    #         pkg = self.url.split('/')[-1]
    #     except IndexError:
    #         pkg = None
    #         logToFile('PackageCheck.txt', self.url)
    #     self.metaData.update(Package=pkg)


    def getDescription(self):
        desc = []
        try:
            tabPane = self.soup.find_all("div", {"class": "notes"})
            if tabPane:
                for note in tabPane:
                    desc.append(note.text)
        except AttributeError:
            desc = None
            logToFile('DeveloperCheck.txt', self.url)
        self.metaData.update(Description=desc)


    # def getRating(self):
    #     try:
    #         rating = self.soup.find('span', {'class': 'rating'})
    #         rating = rating.text
    #     except AttributeError:
    #         if self.validApplication:
    #             rating = '0.0'
    #         else:
    #             rating = None
    #             logToFile('RatingCheck.txt', self.url)
    #     self.metaData.update(Rating=rating)
    #
    # def getTags(self):
    #     tags = []
    #     try:
    #         tagList = self.soup.find('ul', {'class': 'tag_list'})
    #         tagList = tagList.find_all('li')
    #         for tag in tagList:
    #             if tag.text:
    #                 tags.append(tag.text)
    #     except AttributeError:
    #         tags = None
    #         logToFile('TagCheck.txt', self.url)
    #     self.metaData.update(Tags=tags)

    def getSecurity(self):
        sec = []
        try:
            shaAndSig = self.soup.find_all("div", {"class": "modal-body"})
            if shaAndSig:
                for s in shaAndSig[1]:
                    if isinstance(s, NavigableString):
                        sec.append(s)
                    else:
                        sec.append(s.text)
        except AttributeError:
            sec = None
            logToFile('SecurityCheck.txt', self.url)
        self.metaData.update(Security=sec)

    def getSpecs(self):
        specs = []
        try:
            author = self.soup.find_all("div", {"class": "appspec-value"})
            if author:
                for m in author:
                    if isinstance(m, NavigableString):
                        specs.append(m)
                    else:
                        specs.append(m.text)
        except AttributeError:
            specs = None
            logToFile('SpecsCheck.txt', self.url)
        self.metaData.update(Specs=specs)



