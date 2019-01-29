from abc import ABC, abstractmethod
from utils import setRateLimit


class ThreadHelper():

    def __init__(self, driver=None, url=None, app=None):
        self.driver = driver
        self.url    = url
        self.app    = app


class CrawlerBase(ABC):

    def __init__(self, siteUrl, rateLimiter):
        self.siteUrl = siteUrl
        setRateLimit(rateLimiter.rate, rateLimiter.timeOut)

    @abstractmethod
    def crawl(self):
        pass
