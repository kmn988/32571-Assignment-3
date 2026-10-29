from urllib.parse import unquote
from behave import given, when, then
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from helper.helper_shop import CATEGORY_URL, HOME_URL, SUBCATEGORY_URL, amounts, xpath_literal

# --- Locators ---
PAGE_HEADING = (By.CSS_SELECTOR, "#content h2")
TOP_MENU_ITEMS = "//*[@id='menu']//ul[contains(@class,'nav')]/li"
SUBMENU_ITEMS = "//*[@id='content']//ul/li"

# --- Steps ---
@given('I am on the OpenCart homepage')
def step_open_homepage(context):
    context.helper.open(HOME_URL)

@when('I select the category "{category}" from the main navigation')
def step_select_category_from_nav(context, category):
    helper = context.helper
    category = helper.find_by_xpath(f"{TOP_MENU_ITEMS}/a[normalize-space()={xpath_literal(category)}]")
    helper.click_element(category)    


@when('I select the "{link_text}"')
def select_link(context, link_text):
    helper = context.helper
    link = helper.find_by_xpath(f"//*[@id='menu']//a[normalize-space()={xpath_literal(link_text)}]")
    helper.wait().until(EC.element_to_be_clickable(link))
    helper.click_element(link)

@then('I should be on the "{category}" category page')
def go_to_page(context, category):
    helper = context.helper
    helper.wait().until(lambda d: 'route=product/category' in d.current_url )
    assert helper.driver.current_url == CATEGORY_URL, f"Expected URL '{CATEGORY_URL}', but got '{helper.driver.current_url}'"

@then('the page heading should contain "{category}"')
def verify_page_heading(context, category):
    helper = context.helper
    heading = helper.find_by_css("#content h2").text.strip()
    assert category in heading, f"Expected page heading containing '{category}', but got '{heading}'"

@given('I am on the "{category}" category page')
def step_open_category_page(context, category):
    helper = context.helper
    helper.open(CATEGORY_URL)

@when('I select the subcategory "{subcategory}"')
def step_select_subcategory(context, subcategory):
    helper = context.helper
    subcategory_link = helper.find_by_xpath(f"{SUBMENU_ITEMS}//a[starts-with(normalize-space(.), {xpath_literal(subcategory + ' (')})]")
    helper.wait().until(EC.element_to_be_clickable(subcategory_link))
    helper.click_element(subcategory_link)

@then('I should be on the "{subcategory}" subcategory page')
def step_verify_subcategory_page(context, subcategory):
    helper = context.helper
    helper.wait().until(lambda d: 'route=product/category' in d.current_url)
    assert helper.driver.current_url == SUBCATEGORY_URL, f"Expected URL '{SUBCATEGORY_URL}', but got '{helper.driver.current_url}'"

@then('I should see a list of products in the subcategory')
def step_verify_product_list(context):
    helper = context.helper
    product_cards = helper.find_all_by_css("#content .product-layout")
    assert product_cards, "Expected to see a list of products, but none were found"

@given('I am on the "{subcategory}" subcategory page')
def step_open_subcategory_page(context, subcategory):
    helper = context.helper
    helper.open(SUBCATEGORY_URL)

@when('I sort the products by "{sort_option}"')
def step_sort_products(context, sort_option):
    helper = context.helper
    sort_dropdown = helper.find_by_id("input-sort")
    Select(sort_dropdown).select_by_visible_text(sort_option)

@then('the products should be listed in {order} price order')
def step_verify_sorted_products(context, order):
    helper = context.helper
    cards = helper.find_all_by_css("#content .product-layout")
    prices = [amounts(card.find_element(By.CSS_SELECTOR, ".price").text)[0] for card in cards]
    assert len(prices) >= 2, f"Need at least 2 products to check the order, found {prices}"

    if order == "ascending":
        expected = sorted(prices)
    elif order == "descending":
        expected = sorted(prices, reverse=True)
    else:
        raise ValueError(f"Unknown order: {order}")
    assert prices == expected, f"Prices are not {order}: {prices}"