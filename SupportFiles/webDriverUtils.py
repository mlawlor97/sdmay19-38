from utils import createPath, requestHTML

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from time import sleep


class WebDriver:

    def __init__(self):
        print('creating driver')
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')

        self.driver = webdriver.Chrome(
            chrome_options=options,
            executable_path=createPath('SupportFiles', 'chromedriver'))

        self.Url = None

        # Shorthand functions
        self.present    = EC.presence_of_element_located
        self.visible    = EC.visibility_of_element_located
        self.invisible  = EC.invisibility_of_element_located

        self.find       = lambda by='class name', tag='': self.driver.find_element(by, tag)
        self.find_all   = lambda by='class name', tag='': self.driver.find_elements(by, tag)

        self.scrollTo   = lambda element: ActionChains(self.driver).move_to_element(element).perform()
        self.fetchPage  = lambda: requestHTML(self.Url, self.driver.page_source)

    def __del__(self):
        print('destroying driver')
        self.driver.quit()

    def waitFor(self, condition):
        try:
            WebDriverWait(self.driver, 1).until(condition)
        except TimeoutException:
            return TimeoutException
        sleep(0.01)

    def clickAway(self, target, selector=None):
        target = target if not selector else self.find(selector, target)
        target.click()
        self.waitFor(self.invisible(target))

    def clickPopUp(self, target, verifier, index=0, getSoup=True):
        self.waitFor(self.visible(('class name', target)))

        self.find_all(tag=target)[index].click()
        self.waitFor(self.visible(('class name', verifier)))

        return self.fetchPage() if getSoup == True else None

    def oldClick(self, tag, index=0):
        self.waitFor(self.visible(('class name', tag)))

        element = self.find_all(tag=tag)[index]
        self.scrollTo(element)
        element.click()
        sleep(0.25)

        return self.fetchPage()

    def loadPage(self, url, searchBy, validator, getSoup=None):
        self.Url = url
        self.driver.get(self.Url)
        return self.waitFor(self.present((searchBy, validator))) if not getSoup else self.fetchPage()

    # Very specific task
    # Should probable change
    def googleScroller(self):
        def bounce():
            self.scrollTo(footer)
            self.scrollTo(heading)
            self.waitFor(self.invisible(loader))

        footer  = self.find(tag='footer')
        loader  = self.find(tag='bottom-loading')
        heading = self.find(tag='cluster-heading')
        end     = self.find(tag='contains-text-link')
        more    = self.find(by='id', tag='show-more-button')

        bounce()
        while end.is_displayed():
            bounce() if not more.is_displayed() else self.clickAway(more)

        return self.fetchPage()

    def loadMore(self, tag, selector='class name'):
        element = self.find(selector, tag)
        while element.is_displayed():
            self.clickAway(element)
        return self.fetchPage()
