"""OpenCart-specific page flows shared by several step files
(login/registration, product page, cart, wishlist)."""
import re
import time
from urllib.parse import quote_plus, unquote

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

SITE = "https://opencart.abstracta.us/index.php?route="
ACCOUNT_URL = SITE + "account/account"
LOGIN_URL = SITE + "account/login"
REGISTER_URL = SITE + "account/register"
WISHLIST_URL = SITE + "account/wishlist"
CART_URL = SITE + "checkout/cart"
CHECKOUT_URL = SITE + "checkout/checkout"
SEARCH_URL = SITE + "product/search&search="

PRICE_RE = re.compile(r"\$\s*([0-9][0-9,]*\.[0-9]{2})")


# ---------- small utilities ----------
def amounts(text):
    """All dollar amounts found in a text, as floats."""
    return [float(m.replace(",", "")) for m in PRICE_RE.findall(text or "")]


def xpath_literal(value):
    """Safely quote a string for XPath (handles ' and \" in product names, e.g. Apple Cinema 30\")."""
    if '"' not in value:
        return f'"{value}"'
    if "'" not in value:
        return f"'{value}'"
    return "concat(" + ", '\"', ".join(f'"{part}"' for part in value.split('"')) + ")"


def current_url(helper):
    return unquote(helper.driver.current_url)


def go(helper, url):
    helper.open(url)
    helper.wait_for_page_load()


def any_visible(driver, by, value):
    return any(el.is_displayed() for el in driver.find_elements(by, value))


def first_visible(driver, by, value):
    for el in driver.find_elements(by, value):
        if el.is_displayed():
            return el
    return None


# ---------- account ----------
def register_new_user(helper):
    """Register a brand-new account (unique e-mail) and return its details.
    OpenCart logs the customer in automatically after registration."""
    user = {
        "first_name": "QA",
        "last_name": "Tester",
        "email": f"qa.tester.{int(time.time())}@example.com",
        "telephone": "0400000000",
        "password": "Test@1234",
    }
    go(helper, REGISTER_URL)
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


def login(helper, user):
    go(helper, LOGIN_URL)
    helper.find_by_id("input-email").send_keys(user["email"])
    helper.find_by_id("input-password").send_keys(user["password"])
    helper.click_element(helper.find_by_css("input[type='submit'][value='Login']"))
    helper.wait().until(lambda d: "account/account" in unquote(d.current_url))


def ensure_logged_in(context):
    """Reuse the session if already logged in, else log in / register.
    The user is kept in context.session (created in before_all) so it survives between scenarios."""
    h = context.helper
    go(h, ACCOUNT_URL)
    if "account/login" not in current_url(h):
        return  # account page opened -> already logged in
    user = context.session.get("user")
    if user:
        login(h, user)
    else:
        context.session["user"] = register_new_user(h)


# ---------- product page ----------
def open_product_page(helper, name):
    """Find the product through the site search and open its page.
    Returns {'name', 'price', 'model'} as displayed on the product page."""
    go(helper, SEARCH_URL + quote_plus(name) + "&limit=100")
    links = helper.find_all_by_xpath(
        "//div[@id='content']//div[contains(@class,'product-layout')]"
        f"//h4/a[normalize-space()={xpath_literal(name)}]"
    )
    assert links, f"Product '{name}' was not found through the store search"
    helper.click_element(links[0])
    helper.find_by_id("button-cart")  # product page is ready

    price_text = helper.find_by_css("#content ul.list-unstyled h2").text
    model = None
    for li in helper.find_all_by_css("#content ul.list-unstyled li"):
        found = re.search(r"(?:Product Code|Model):\s*(.+)", li.text)
        if found:
            model = found.group(1).strip()
            break
    return {
        "name": helper.find_by_css("#content h1").text.strip(),
        "price": amounts(price_text)[0],
        "model": model,
    }


# ---------- cart ----------
def empty_cart(helper):
    go(helper, CART_URL)
    while True:
        buttons = helper.find_all_by_css("#content button[onclick^='cart.remove']")
        if not buttons:
            return
        helper.click_element(buttons[0])
        helper.wait().until(EC.staleness_of(buttons[0]))
        helper.wait_for_page_load()


def add_current_product_to_cart(helper):
    helper.click_element(helper.find_by_id("button-cart"))
    alert = helper.find_by_css(".alert-success, .alert-danger")
    assert alert.text.strip().lower().startswith("success"), f"Add to cart failed: {alert.text!r}"


def cart_total_amount(helper):
    text = helper.find_by_id("cart-total").text
    found = amounts(text)
    assert found, f"Cannot parse the cart total from {text!r}"
    return found[-1]


# ---------- wishlist ----------
def wishlist_rows(helper):
    """Open the wishlist page and return one dict per product row."""
    go(helper, WISHLIST_URL)
    rows = []
    for tr in helper.find_all_by_css("#content table tbody tr"):
        cells = tr.find_elements(By.TAG_NAME, "td")
        if len(cells) < 6:
            continue
        price = amounts(cells[4].text)
        rows.append({
            "row": tr,
            "name": cells[1].text.strip(),
            "model": cells[2].text.strip(),
            "stock": cells[3].text.strip(),
            "price": price[-1] if price else None,
        })
    return rows


def empty_wishlist(helper):
    go(helper, WISHLIST_URL)
    while True:
        links = helper.find_all_by_css("#content a[href*='wishlist&remove=']")
        if not links:
            return
        helper.click_element(links[0])
        helper.wait().until(EC.staleness_of(links[0]))
        helper.wait_for_page_load()


def add_current_product_to_wishlist(helper):
    """Click the heart button on a product page; returns the alert text."""
    helper.click_element(helper.find_by_css("button[onclick^='wishlist.add']"))
    return helper.find_by_css(".alert-success, .alert-danger").text