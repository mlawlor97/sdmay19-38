from utils import RateLimiter, mkStoreDirs, requestHTML, checkAppDB, safeExecute
from SupportFiles.crawlerBase import CrawlerBase
from SupportFiles.webDriverUtils import WebDriver

class SlideMe(CrawlerBase):
    siteUrl = "http://slideme.org"
    rateLimiter = RateLimiter(0, 0)

    def __init__(self, siteUrl=siteUrl, rateLimiter=rateLimiter):
        super().__init__(siteUrl, rateLimiter)
        # self.webDriver = WebDriver()
        # mkStoreDirs(storeName="slideme")

    def crawl(self):
        soup = requestHTML(f"{self.siteUrl}/applications")
        categories = self.getCategories(soup)

        crawlableCats = []

        for cat in categories[-1:]:
            subs = self.getCategories(requestHTML(cat))
            crawlableCats += subs if subs.__len__() > 0 else [cat]
            break
        
        print(crawlableCats.__len__())

        for cat in crawlableCats[:1]:
            page = 0
            while(True):
                apps = self.getApps(requestHTML(f"{cat}&page={page}"))
                if not apps:
                    break
                
                page += 1
                [self.scrapeAppData(app) for app in apps[:1]]
                break

    def getCategories(self, soup):
        cats = []
        [cats.append(self.siteUrl + cat['href']) for cat in soup(class_="apachesolr-facet")]
        return cats

    def getApps(self, soup):
        return [self.siteUrl + app.find('a')['href'] for app in soup(class_="node-mobileapp")]

    def scrapeAppData(self, url):
        entry = checkAppDB(appUrl=url)
        if entry:
            return (entry.get('app_name'), entry.get('_id'))

        soup = safeExecute(requestHTML, url)
        appName = safeExecute(soup.find(class_='title').find('span'))
        print(appName)

def main():
    sm = SlideMe()
    sm.crawl()

if __name__ == "__main__":
    main()