import time
from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from helper.helper_shop import LOGIN_URL, amounts, ensure_logged_in, xpath_literal

# ---------- Steps ----------
@given('I am logged in as a registered user')
def step_logged_in_user(context):
    helper = context.helper
    helper.open(LOGIN_URL)
    helper.wait_for_page_load()
    ensure_logged_in(context)

@given('my wishlist is empty')
def step_empty_wishlist(context):
    helper = context.helper
    helper.open("https://opencart.abstracta.us/index.php?route=account/wishlist")
    helper.wait_for_page_load()
    # If there are items in the wishlist, remove them
    remove_buttons = helper.find_all_by_css(".btn-danger")
    for button in remove_buttons:
        button.click()
        time.sleep(0.5)  # Wait a bit for the item to be removed

@given('I am on the product page for "{product_name}"')
def step_on_product_page(context, product_name):
    helper = context.helper
    search_url = f"https://opencart.abstracta.us/index.php?route=product/search&search={product_name}"
    helper.open(search_url)
    helper.wait_for_page_load()
    product_link = helper.find_by_xpath(f"//div[@class='caption']//a[normalize-space()={xpath_literal(product_name)}]")
    product_link.click()
    helper.wait_for_page_load()

@when('I add the product to my wishlist')
def step_add_to_wishlist(context):
    helper = context.helper
    add_to_wishlist_button = helper.find_by_xpath("//button[@data-original-title='Add to Wish List']")
    add_to_wishlist_button.click()
    helper.wait_for_page_load()

@then('I should see a confirmation that the product was added to the wishlist')
def step_verify_wishlist_confirmation(context):
    helper = context.helper
    confirmation_message = helper.find_by_css(".alert-success").text
    assert "Success: You have added" in confirmation_message and "to your wish list!" in confirmation_message, f"Expected confirmation message, but got: '{confirmation_message}'"

@then('the wishlist should contain "{product_name}"')
def step_verify_wishlist_contains_product(context, product_name):
    helper = context.helper
    helper.open("https://opencart.abstracta.us/index.php?route=account/wishlist")
    helper.wait_for_page_load()
    wishlist_items = helper.find_all_by_css(".table-responsive .text-left a")
    product_names = [item.text for item in wishlist_items]
    assert product_name in product_names, f"Expected '{product_name}' to be in wishlist, but got: {product_names}"

@given('product "{product_name}" is in my wishlist')
def step_product_in_wishlist(context, product_name):
    helper = context.helper
    # Check if the product is already in the wishlist
    helper.open("https://opencart.abstracta.us/index.php?route=account/wishlist")
    helper.wait_for_page_load()
    wishlist_items = helper.find_all_by_css(".table-responsive .text-left a")
    product_names = [item.text for item in wishlist_items]
    if product_name not in product_names:
        # If not, add it to the wishlist
        search_url = f"https://opencart.abstracta.us/index.php?route=product/search&search={product_name}"
        helper.open(search_url)
        helper.wait_for_page_load()
        product_link = helper.find_by_xpath(f"//div[@class='caption']//a[normalize-space()={xpath_literal(product_name)}]")
        product_link.click()
        helper.wait_for_page_load()
        add_to_wishlist_button = helper.find_by_xpath("//button[@data-original-title='Add to Wish List']")
        add_to_wishlist_button.click()
        helper.wait_for_page_load()

@when('I open the wishlist page')
def step_open_wishlist_page(context):
    helper = context.helper
    helper.open("https://opencart.abstracta.us/index.php?route=account/wishlist")
    helper.wait_for_page_load()

@when('I add product "{product_name}" to my cart')
def step_add_product_to_cart_from_wishlist(context, product_name):
    helper = context.helper
    helper.open("https://opencart.abstracta.us/index.php?route=account/wishlist")
    helper.wait_for_page_load()
    wishlist_items = helper.find_all_by_css(".table-responsive .text-left a")
    for item in wishlist_items:
        if item.text.strip() == product_name:
            row = item.find_element(By.XPATH, "./ancestor::tr")
            add_to_cart_button = row.find_element(By.CSS_SELECTOR, "button[onclick^='cart.add']")
            helper.click_element(add_to_cart_button)
            alert = helper.find_by_css(".alert-success, .alert-danger")
            assert "added" in alert.text.lower(), f"Could not add '{product_name}' to the cart: {alert.text!r}"
            return
    raise AssertionError(f"'{product_name}' was not found in the wishlist")

@then('the cart should contain "{product_name}"')
def step_verify_cart_contains_product(context, product_name):
    helper = context.helper
    helper.open("https://opencart.abstracta.us/index.php?route=checkout/cart")
    helper.wait_for_page_load()
    cart_items = helper.find_all_by_css(".table-responsive .text-left a")
    product_names = [item.text for item in cart_items]
    assert product_name in product_names, f"Expected '{product_name}' to be in cart, but got: {product_names}"

@when('I remove "{product_name}" from my wishlist')
def step_remove_product_from_wishlist(context, product_name):
    helper = context.helper
    helper.open("https://opencart.abstracta.us/index.php?route=account/wishlist")
    helper.wait_for_page_load()
    remove_buttons = helper.find_all_by_css(".btn-danger")
    for button in remove_buttons:
        row = button.find_element(By.XPATH, "./ancestor::tr")
        name_cell = row.find_element(By.CSS_SELECTOR, "td.text-left a")
        if name_cell.text.strip() == product_name:
            button.click()
            helper.wait().until(EC.staleness_of(row))
            break

@then('I should see a confirmation that the product was removed from the wishlist')
def step_verify_wishlist_removal_confirmation(context):
    helper = context.helper
    confirmation_message = helper.find_by_css(".alert-success").text
    assert "Success: You have modified your wish list!" in confirmation_message, f"Expected removal confirmation message, but got: '{confirmation_message}'"

@then('the wishlist should not contain "{product_name}"')
def step_verify_wishlist_excludes_product(context, product_name):
    helper = context.helper
    wishlist_items = helper.find_all_by_css(".table-responsive .text-left a")
    product_names = [item.text for item in wishlist_items]
    assert product_name not in product_names, f"Expected '{product_name}' to be removed from wishlist, but got: {product_names}"