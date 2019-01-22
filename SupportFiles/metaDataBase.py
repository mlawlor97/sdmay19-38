from types import FunctionType
from utils import logToFile
import json


class DataCollectionBase:

    def __init__(self, appUrl, soup, **moreSoup):
        self.url = appUrl
        self.soup = soup
        self.additionalSoups = moreSoup
        self.validApplication = False
        self.metaData = {}

    def getName(self):
        pass

    def getDeveloper(self):
        pass

    def getPackage(self):
        pass

    def getCategory(self):
        pass

    def getDescription(self):
        pass

    def getRating(self):
        pass

    def getTags(self):
        pass

    def getNumDownloads(self):
        pass

    def getPrice(self):
        pass

    def getContentRating(self):
        pass

    def getVersion(self):
        pass

    def getSize(self):
        pass

    def getPatchNotes(self):
        pass

    def getRequirements(self):
        pass

    def getUpdatedOn(self):
        pass

    def getAll(self):
        """Calls all methods and returns value retrieved

        :return: metaData Map of all the collected information
        """
        for x, y in self.__class__.__dict__.items():
            if type(y) == FunctionType and x is not 'getAll' and x is not 'tryCollection':
                func = getattr(self.__class__, x)
                func(self)
        if self.validApplication is False:
            return False
        else:
            return json.dumps(self.metaData, indent=4)

    def tryCollection(self, data, func):
        try:
            self.metaData.update({data: func()})
        except AttributeError:
            logToFile('AppCheck.txt', data + ': ' + self.url + '\n')
