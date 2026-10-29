from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class HelperBase(object):
    __TIMEOUT = 10

    def __init__(self, driver):
        super(HelperBase, self).__init__()
        self._driver_wait = WebDriverWait(driver, self.__TIMEOUT)
        self._driver = driver

    # --- access ---
    @property
    def driver(self):
        return self._driver

    def wait(self, timeout=15):
        return WebDriverWait(self._driver, timeout)

    # --- navigation ---
    def open(self, url):
        self._driver.get(url)

    def close(self):
        self._driver.quit()

    # --- finders (wait until visible) ---
    def find_by_name(self, name):
        return self._driver_wait.until(EC.visibility_of_element_located((By.NAME, name)))

    def find_by_id(self, id):
        return self._driver_wait.until(EC.visibility_of_element_located((By.ID, id)))

    def find_by_css(self, css_selector):
        return self._driver_wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))

    def find_by_xpath(self, xpath):
        return self._driver_wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))

    # --- finders (no waiting, may return an empty list) ---
    def find_all_by_css(self, css_selector):
        return self._driver.find_elements(By.CSS_SELECTOR, css_selector)

    def find_all_by_xpath(self, xpath):
        return self._driver.find_elements(By.XPATH, xpath)

    # --- clicking ---
    def scroll_into_view(self, element):
        self._driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

    def js_click(self, element):
        self._driver.execute_script("arguments[0].click();", element)

    def click_element(self, element):
        self._driver_wait.until(EC.element_to_be_clickable(element))
        self.scroll_into_view(element)
        try:
            element.click()
        except ElementClickInterceptedException:
            self.js_click(element)
