from utils import logToFile
import json


# noinspection PyCompatibility
class DataCollectionBase:

    def __init__(self, url='', soup=None, **moreSoup):
        self.url = url
        self.soup = soup
        self.additionalSoups = moreSoup
        self.metaData = dict({})
        self.methods = [_ for _, y in self.__class__.__dict__.items() if isinstance(y, tuple)]
        self.JSON = lambda: json.dumps(self.metaData, indent=4)

    def getAll(self):
        for m in self.methods:
            res = getattr(self.__class__, m)
            Name, Func, Log = res if res.__len__() == 3 else (res[0], res[1], None)
            self.tryCollection(Name, Func, Log)
        return self

    def tryCollection(self, data, func, log=None):
        try:
            self.metaData.update({data: func(self)})
        except:
            logToFile(f"{self.__class__.__name__}Check.txt", f"{data}:\t{self.url}\n") if log else None
