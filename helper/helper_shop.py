import re
from urllib.parse import quote_plus, unquote
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By

SITE = "https://opencart.abstracta.us/index.php?route="
HOME_URL = SITE + "common/home"
ACCOUNT_URL = SITE + "account/account"
LOGIN_URL = SITE + "account/login"
REGISTER_URL = SITE + "account/register"
WISHLIST_URL = SITE + "account/wishlist"
CART_URL = SITE + "checkout/cart"
CHECKOUT_URL = SITE + "checkout/checkout"
SEARCH_URL = SITE + "product/search&search="
CATEGORY_URL = SITE + "product/category&path=25"
SUBCATEGORY_URL = SITE + "product/category&path=25_28"

PRICE_RE = re.compile(r"\$\s*([0-9][0-9,]*\.[0-9]{2})")
TEST_USER = {
    "first_name": "QA",
    "last_name": "Tester",
    "email": "qa.tester@example.com",
    "telephone": "0400000000",
    "password": "Test@1234",
}

# --- small utilities ---
def amounts(text):
    return [float(m.replace(",", "")) for m in PRICE_RE.findall(text or "")]


def xpath_literal(value):
    if '"' not in value:
        return f'"{value}"'
    if "'" not in value:
        return f"'{value}'"
    return "concat(" + ", '\"', ".join(f'"{part}"' for part in value.split('"')) + ")"


def current_url(helper):
    return unquote(helper.driver.current_url)

def any_visible(driver, by, value):
    return any(el.is_displayed() for el in driver.find_elements(by, value))


def first_visible(driver, by, value):
    for el in driver.find_elements(by, value):
        if el.is_displayed():
            return el
    return None


# --- account ---
def register_new_user(helper, user):
    helper.open(REGISTER_URL)
    helper.find_by_id("input-firstname").send_keys(user["first_name"])
    helper.find_by_id("input-lastname").send_keys(user["last_name"])
    helper.find_by_id("input-email").send_keys(user["email"])
    helper.find_by_id("input-telephone").send_keys(user["telephone"])
    helper.find_by_id("input-password").send_keys(user["password"])
    helper.find_by_id("input-confirm").send_keys(user["password"])
    for box in helper.find_all_by_css("form input[name='agree']"):  # privacy policy
        if not box.is_selected():
            helper.click_element(box)
    helper.click_element(helper.find_by_css("input[type='submit'][value='Continue']"))
    helper.wait().until(lambda d: "account/success" in unquote(d.current_url))
    return user


def try_login(helper, user):
    helper.open(LOGIN_URL)
    helper.find_by_id("input-email").send_keys(user["email"])
    helper.find_by_id("input-password").send_keys(user["password"])
    helper.click_element(helper.find_by_css("input[type='submit'][value='Login']"))
    helper.wait().until(
        lambda d: "account/account" in unquote(d.current_url) or d.find_elements(By.CSS_SELECTOR, ".alert-danger")
    )
    return "account/account" in current_url(helper)

def ensure_logged_in(context):
    h = context.helper
    h.open(ACCOUNT_URL)
    if "account/login" not in current_url(h):
        return                                  # already logged in
    if try_login(h, TEST_USER):
        return                                  # account exists: reuse it
    register_new_user(h, TEST_USER)             # first run: create it 



# --- Checkout ---
def displayed(helper, css):
    for el in helper.find_all_by_css(css):
        if el.is_displayed():
            return el
    return None

def billing_error(helper, field):
    return helper.find_by_css(f"#input-payment-{field} + .text-danger").text.strip()

def select_when_ready(helper, element_id, text):
    def attempt(driver):
        try:
            Select(driver.find_element(By.ID, element_id)).select_by_visible_text(text)
            return True
        except (StaleElementReferenceException, NoSuchElementException, NotImplementedError):
            return False   # being rebuilt, not there yet, or still disabled: try again
    helper.wait().until(attempt)

def continue_to(helper, button_css, next_panel_css):
    helper.click_element(helper.find_by_css(button_css))
    helper.find_by_css(next_panel_css)
