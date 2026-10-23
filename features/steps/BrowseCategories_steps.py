from urllib.parse import unquote

from behave import given, when, then
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from helper.helper_shop import amounts, first_visible, xpath_literal

# ---------- Locators (OpenCart 3 default theme): adjust here if the DOM changes ----------
PAGE_HEADING = (By.CSS_SELECTOR, "#content h2")
BREADCRUMB = (By.CSS_SELECTOR, "ul.breadcrumb")
PRODUCT_CARDS = (By.CSS_SELECTOR, "#content .product-layout")
PRODUCT_PRICE = (By.CSS_SELECTOR, ".price")

TOP_MENU_ITEMS = "//*[@id='menu']//ul[contains(@class,'nav')]/li"


def top_menu_link(name):
    """Top-level main navigation entry, e.g. 'Components'."""
    return (By.XPATH, f"{TOP_MENU_ITEMS}/a[normalize-space()={xpath_literal(name)}]")


def top_menu_link_containing(sub_name):
    """Top-level entry whose dropdown holds a subcategory (link text looks like 'Monitors (2)')."""
    return (By.XPATH, f"{TOP_MENU_ITEMS}[.//a[starts-with(normalize-space(.), {xpath_literal(sub_name + ' (')})]]/a")


def sub_link(sub_name, scope):
    """Subcategory link; the product count is part of the text, e.g. 'Monitors (2)'."""
    return (By.XPATH, f"{scope}//a[starts-with(normalize-space(.), {xpath_literal(sub_name + ' (')})]")


def hover(context, locator):
    h = context.helper
    target = h.wait().until(EC.visibility_of_element_located(locator))
    ActionChains(h.driver).move_to_element(target).perform()


def click_menu_link(context, text):
    """Click a visible link in the main navigation by its exact text (e.g. 'Show All Components')."""
    h = context.helper
    locator = (By.XPATH, f"//*[@id='menu']//a[normalize-space()={xpath_literal(text)}]")
    link = h.wait().until(lambda d: first_visible(d, *locator))
    h.click_element(link)


def displayed_prices(context):
    cards = [c for c in context.helper.driver.find_elements(*PRODUCT_CARDS) if c.is_displayed()]
    assert cards, "No products were displayed"
    prices = []
    for card in cards:
        # first amount is the current price (a special price is rendered before the old one)
        found = amounts(card.find_element(*PRODUCT_PRICE).text)
        assert found, f"Cannot parse a price from: {card.text!r}"
        prices.append(found[0])
    return prices


# ---------- Steps ----------
@given('I am on the OpenCart homepage')
def step_open_homepage(context):
    context.helper.open_homepage()
    context.helper.wait_for_page_load()


@when('I select the category "{category}" from the main navigation')
def step_select_category_from_nav(context, category):
    # Hovering opens the category's dropdown (desktop layout), exposing "Show All <category>"
    hover(context, top_menu_link(category))


@when('I select the "{link_text}"')
def step_select_nav_link(context, link_text):
    click_menu_link(context, link_text)


@then('I should be on the "{category}" category page')
def step_assert_category_page(context, category):
    h = context.helper
    h.wait().until(lambda d: "route=product/category" in unquote(d.current_url))
    heading = h.wait().until(EC.visibility_of_element_located(PAGE_HEADING)).text.strip()
    assert category.lower() in heading.lower(), (
        f"Expected heading to contain '{category}' but was '{heading}'"
    )


@given('I am on the "{category}" category page')
def step_goto_category_page(context, category):
    step_open_homepage(context)
    step_select_category_from_nav(context, category)
    step_select_nav_link(context, f"Show All {category}")
    step_assert_category_page(context, category)


@given('I am on the "{subcategory}" subcategory page')
def step_goto_subcategory_page(context, subcategory):
    step_open_homepage(context)
    hover(context, top_menu_link_containing(subcategory))
    link = context.helper.wait().until(
        lambda d: first_visible(d, *sub_link(subcategory, "//*[@id='menu']"))
    )
    context.helper.click_element(link)
    step_assert_subcategory_page(context, subcategory)


@when('I select the subcategory "{subcategory}"')
def step_select_subcategory(context, subcategory):
    h = context.helper
    scope = "//*[@id='content' or @id='column-left']"  # "Refine Search" links or the left category list
    link = h.wait().until(lambda d: first_visible(d, *sub_link(subcategory, scope)))
    h.click_element(link)


@then('I should be on the "{subcategory}" subcategory page')
def step_assert_subcategory_page(context, subcategory):
    h = context.helper
    h.wait().until(lambda d: "route=product/category" in unquote(d.current_url))
    breadcrumb = h.wait().until(EC.visibility_of_element_located(BREADCRUMB)).text
    assert subcategory.lower() in breadcrumb.lower(), (
        f"Breadcrumb '{breadcrumb}' does not contain '{subcategory}'"
    )


@then('the page heading should contain "{text}"')
def step_assert_heading_contains(context, text):
    heading = context.helper.wait().until(EC.visibility_of_element_located(PAGE_HEADING)).text
    assert text.lower() in heading.lower(), f"Heading '{heading}' does not contain '{text}'"


@then('at least one product should be displayed')
def step_assert_products_displayed(context):
    cards = [c for c in context.helper.driver.find_elements(*PRODUCT_CARDS) if c.is_displayed()]
    assert cards, "No products were displayed"


@when('I sort the products by "{option}"')
def step_sort_products(context, option):
    h = context.helper
    Select(h.find_by_id("input-sort")).select_by_visible_text(option)
    # the select navigates to the same page with sort=...&order=...
    h.wait().until(lambda d: "sort=" in unquote(d.current_url))
    h.wait_for_page_load()


@then('the products should be listed in ascending price order')
def step_assert_ascending(context):
    prices = displayed_prices(context)
    assert len(prices) >= 2, f"Need at least 2 products to check the order, found {prices}"
    assert prices == sorted(prices), f"Prices are not ascending: {prices}"


@then('the products should be listed in descending price order')
def step_assert_descending(context):
    prices = displayed_prices(context)
    assert len(prices) >= 2, f"Need at least 2 products to check the order, found {prices}"
    assert prices == sorted(prices, reverse=True), f"Prices are not descending: {prices}"