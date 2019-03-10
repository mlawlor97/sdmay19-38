from abc import ABC, abstractmethod
from utils import setRateLimit


class CrawlerBase(ABC):

    def __init__(self, siteUrl, rateLimiter):
        self.siteUrl = siteUrl
        setRateLimit(rateLimiter.rate, rateLimiter.timeOut)

    @abstractmethod
    def crawl(self):
        pass
