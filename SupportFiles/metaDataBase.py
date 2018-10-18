from types import FunctionType


class DataCollectionBase:

    def __init__(self, ErrorUrl, Soup):
        self.url = ErrorUrl
        self.soup = Soup
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

    def getAll(self):
        """Calls all methods and returns value retrieved

        :return: metaData Map of all the collected information
        """
        for x, y in self.__class__.__dict__.items():
            if type(y) == FunctionType and x is not 'getAll':
                func = getattr(self.__class__, x)
                func(self)
        if self.metaData.get('Name') is None:
            return False
        else:
            return self.metaData
