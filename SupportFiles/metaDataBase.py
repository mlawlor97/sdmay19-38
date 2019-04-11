from types import FunctionType
from utils import logToFile, writeOutput
import json


class DataCollectionBase:

    def __init__(self, appUrl='', soup=None, **moreSoup):
        self.url = appUrl
        self.soup = soup
        self.additionalSoups = moreSoup
        self.metaData = {}
        self.methods = [_ for _, y in self.__class__.__dict__.items() if type(y) == FunctionType]

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

    def getPublishDate(self):
        pass

    def getAll(self):
        """Calls all methods and returns value retrieved

        :return: metaData Map of all the collected information
        """
        for x in self.methods:
            try:
                getattr(self.__class__, x)(self)
            except TypeError:
                print(x + ': Failed')
                return Exception
        return self

    def tryCollection(self, data, func, *noLog):
        try:
            self.metaData.update({data: func()})
        except:
            logToFile(self.__class__.__name__ + 'Check.txt', data + ':\t' + self.url + '\n') if not noLog else None

    def getJSON(self):  # Temp function
        return json.dumps(self.metaData, indent=4)
