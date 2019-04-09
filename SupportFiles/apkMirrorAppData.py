from SupportFiles.metaDataBase import DataCollectionBase
from utils import logToFile
from bs4 import Tag, NavigableString


class GetMirrorAppData(DataCollectionBase):

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


    def getDescription(self):
        desc = []
        try:
            tabPane = self.soup.find_all("div", {"class": "notes"})
            if tabPane:
                for note in tabPane:
                    desc.append(note.text)
            descStr = " "
            for d in desc:
                d = d.replace('\n', '').replace('\r', '')
                if d == "" or d == " ":
                    continue
                descStr = descStr + d
        except AttributeError:
            desc = None
            logToFile('DeveloperCheck.txt', self.url)
        self.metaData.update(Description=descStr)
