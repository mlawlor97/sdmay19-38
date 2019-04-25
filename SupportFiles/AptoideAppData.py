from SupportFiles.metaDataBase import DataCollectionBase
from utils import logToFile
from bs4 import Tag, NavigableString



class GetAptoideAppData(DataCollectionBase):

    def getDeveloper(self):
        dev = ""
        try:
            detail_rows = self.soup.find_all("div", {"class": "app-detailed-info__row"})
            index = 0
            for d in detail_rows:
                if index == 1:
                    dev = d.find("span", {"itemprop": "publisher"}).text
                    dev = dev.replace('\n', '').replace('\r', '').replace('\t', '')
                    break
                else:
                    index += 1

        except AttributeError:
            dev = None
            logToFile('DeveloperCheck.txt', self.url)
        self.metaData.update(Developer=dev)


    def getDescription(self):
        desc = ""
        try:
            desc = self.soup.find("p", {"itemprop": "description"}).text
            desc = desc.replace('\n', '').replace('\r', '').replace('\t', '')
        except AttributeError:
            desc = None
            logToFile('DeveloperCheck.txt', self.url)
        self.metaData.update(Description=desc)


    def getCategory(self):
        cat = ""
        try:
            cat = self.soup.find("span", {"itemprop": "applicationSubCategory"}).text
            cat = cat.replace('\n', '').replace('\r', '').replace('\t', '')
        except AttributeError:
            cat = None
            logToFile('DeveloperCheck.txt', self.url)
        self.metaData.update(Category=cat)


