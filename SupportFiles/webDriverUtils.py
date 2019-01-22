from utils import createPath, requestHTML

from selenium import webdriver
from selenium.webdriver.common.by import By
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
            executable_path=createPath("HOME", 'SupportFiles', 'chromedriver'))

        # Shorthand functions
        self.present = EC.presence_of_element_located
        self.visible = EC.visibility_of_element_located
        self.invisible = EC.invisibility_of_element_located
        self.find_class = self.driver.find_element_by_class_name
        self.find_id = self.driver.find_element_by_id

    def __del__(self):
        print('destroying driver')
        self.driver.quit()

    def scrollTo(self, element):
        ActionChains(self.driver).move_to_element(element).perform()

    def waitFor(self, condition):
        try:
            WebDriverWait(self.driver, 5).until(condition)
        except TimeoutException:
            return TimeoutException
        sleep(0.01)

    def clickAway(self, target):
        target.click()
        self.waitFor(self.invisible(target))

    def clickPopUp(self, url, target, verifier, *index):
        elementIndex = 0 if not index else index[0]
        self.waitFor(self.visible((By.CLASS_NAME, target)))

        element = self.find_class(target)[elementIndex]
        element.click()
        self.waitFor(self.present((By.CLASS_NAME, verifier)))

        return requestHTML(url, self.driver.page_source)

    def oldClick(self, url, tag, *index):
            elementIndex = 0 if not index else index[0]
            self.waitFor(self.visible((By.CLASS_NAME, tag)))

            element = self.find_class(tag)[elementIndex]
            element.click()
            sleep(0.25)

            return requestHTML(url, self.driver.page_source)

    def loadPage(self, url, validator):
        self.driver.get(url)
        self.waitFor(self.present((By.XPATH, validator)))
        return requestHTML(url, self.driver.page_source)

    # Very specific task
    # Should probable change
    def googleScroller(self, url):
        def bounce():
            self.scrollTo(footer)
            self.scrollTo(heading)
            self.waitFor(self.invisible(loader))

        self.driver.get(url)
        self.waitFor(self.present((By.CLASS_NAME, 'loaded')))

        footer = self.find_class('footer')
        loader = self.find_class('bottom-loading')
        heading = self.find_class('cluster-heading')
        end = self.find_class('contains-text-link')
        more = self.find_id('show-more-button')

        bounce()
        while end.get_attribute('style').strip() == '':
            bounce()
            if more.is_displayed():
                print("clicking")
                self.clickAway(more)

        return requestHTML(url, self.driver.page_source)
