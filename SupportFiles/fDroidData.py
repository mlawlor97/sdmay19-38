from SupportFiles.metaDataBase import DataCollectionBase
from utils import logToFile


class FDroidData(DataCollectionBase):

    def getName(self):
        try:
            name = self.soup.find('h3', {'class': 'package-name'})
            name = name.text.strip()
        except AttributeError:
            name = None
            logToFile('NameCheck.txt', self.url)
        self.metaData.update(Name=name)

    def getDeveloper(self):
        try:
            dev = None
            devs = self.soup.find_all('li', {'class': 'package-link'})
            for d in devs:
                if d.text.strip() == 'Source Code':
                    dev = d.find('a').get('href').split('/')[-2]
                    break
        except AttributeError:
            dev = None
            logToFile('DeveloperCheck.txt', self.url)
        self.metaData.update(Developer=dev)

    def getDescription(self):
        try:
            desc = self.soup.find('div', {'class': 'package-description'})
            desc = desc.text.strip()
        except AttributeError:
            desc = None
            logToFile('DescriptionCheck.txt', self.url)
        self.metaData.update(Description=desc)



