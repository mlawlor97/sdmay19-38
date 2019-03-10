from utils import logToFile
import json


# noinspection PyCompatibility
class DataCollectionBase:
    """Used to collect metadata

    When collecting information, it goes through all the tuples
    defined in the class. Each tuple is structured as:
        ('stored_key', lambda function that returns the data)

    Example Tuple:
        _getDev = ('developer', lambda _: _.soup.find(class_='developer').text.strip())

    In the example above the _ is equivalent to self.
    For value processing that takes multiple lines, a function can
    be defined seperately and called from the lambda function as:
        def dev(self):
            # Pretend there is processing done here

        _getDev = ('developer', lambda _: _.dev())
    """

    def __init__(self, url='', soup=None, **moreSoup):
        """Creates new metaDataCollection instance

        :param url: url of the current page (Optional)
        :param soup: Beatiful Soup object for the page 
            that data is being pulled from
        :param moreSoup: Dictionary of additional BS objects
            for if not all the data is on one page (Optional)
        """

        self.url = url
        self.soup = soup
        self.additionalSoups = moreSoup
        # Dictionary of all the metaData in (key, value) format
        self.metaData = dict({})
        # List of all the defined tuples that will need to be processed
        self.methods = [_ for _, y in self.__class__.__dict__.items() if isinstance(y, tuple)]
        # JSON formatted version of the metaData 
        self.JSON = lambda: json.dumps(self.metaData, indent=4)

    def getAll(self):
        """Processes all tuples in the class"""
        for m in self.methods:
            res = getattr(self.__class__, m)
            Name, Func, Log = res if res.__len__() == 3 else (res[0], res[1], None)
            self.tryCollection(Name, Func, Log)
        return self

    def tryCollection(self, data, func, log=None):
        """Attempts collection of metaData values and stores them into the data dictionary
        
        :param data: key for the dictionary
        :param func: function that will return the data value
        :param log: Defaults to None, if not None will write failing function to file 
        """
        try:
            self.metaData.update({data: func(self)})
        except:
            logToFile(f"{self.__class__.__name__}Check.txt", f"{data}:\t{self.url}\n") if log else None
