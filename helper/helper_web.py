from selenium import webdriver
from helper.helper_base import HelperBase

def get_browser(browser):
    if browser == "chrome":
        return webdriver.Chrome()
    elif browser == "firefox":
        return webdriver.Firefox()
    else:
        raise ValueError(f"Unsupported browser: {browser}")

def get_helper(browser):
    driver = get_browser(browser)
    return HelperBase(driver)