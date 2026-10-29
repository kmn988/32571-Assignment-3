import time
from urllib.parse import quote_plus
from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from helper.helper_shop import CART_URL, CHECKOUT_URL, SEARCH_URL, any_visible, billing_error, continue_to, displayed, select_when_ready, xpath_literal

# --- Locators ---
BILLING_CONTINUE = "#button-payment-address"
BILLING_EXISTING = "input[name='payment_address'][value='existing']"
BILLING_NEW = "input[name='payment_address'][value='new']"
SHIPPING_ADDRESS_CONTINUE = "#button-shipping-address"
SHIPPING_EXISTING = "input[name='shipping_address'][value='existing']"
SHIPPING_METHOD_CONTINUE = "#button-shipping-method"
PAYMENT_METHOD_CONTINUE = "#button-payment-method"



# --- Steps ---
@given('my cart contains "{product_name}"')
def step_cart_contains_product(context, product_name):
    helper = context.helper
    helper.open(CART_URL)
    if helper.find_all_by_xpath(f"//div[@id='content']//a[normalize-space()={xpath_literal(product_name)}]"):
        return

    # Find the product through search
    helper.open(f"{SEARCH_URL}{quote_plus(product_name)}")
    link = helper.find_by_xpath(
        f"//div[@id='content']//div[contains(@class,'caption')]//a[normalize-space()={xpath_literal(product_name)}]"
    )
    helper.click_element(link)

    # Add to cart on the product page
    helper.click_element(helper.find_by_id("button-cart"))
    alert = helper.find_by_css(".alert-success, .alert-danger")
    assert "success" in alert.text.lower(), f"Could not add '{product_name}' to the cart: {alert.text!r}"


@when('I proceed to checkout')
def step_proceed_to_checkout(context):
    helper = context.helper
    helper.open(CHECKOUT_URL)


@when('I fill out my billing details')
def step_fill_billing_details(context):
    helper = context.helper
    helper.find_by_css(BILLING_CONTINUE)  # billing step is open

    existing = displayed(helper, BILLING_EXISTING)
    if existing:
        # The account already has an address from an earlier run: reuse it
        if not existing.is_selected():
            helper.click_element(existing)
    else:
        for field_id, value in [
            ("input-payment-firstname", "QA"),
            ("input-payment-lastname", "Tester"),
            ("input-payment-address-1", "123 Test St"),
            ("input-payment-city", "Testville"),
        ]:
            field = helper.find_by_id(field_id)
            field.clear()
            field.send_keys(value)

        postcode = displayed(helper, "#input-payment-postcode")
        if postcode:
            postcode.clear()
            postcode.send_keys("90001")

        select_when_ready(helper, "input-payment-country", "United States")
        select_when_ready(helper, "input-payment-zone", "California")

    continue_to(helper, "#button-payment-address", "#collapse-shipping-address.in, #collapse-shipping-method.in")
    time.sleep(2)  # wait for the next step to be ready


@when('I fill out my delivery details')
def step_fill_delivery_details(context):
    helper = context.helper
    helper.wait().until(
        lambda d: any_visible(d, By.CSS_SELECTOR, SHIPPING_ADDRESS_CONTINUE)
        or any_visible(d, By.CSS_SELECTOR, SHIPPING_METHOD_CONTINUE)
    )
    if displayed(helper, SHIPPING_ADDRESS_CONTINUE):
        existing = displayed(helper, SHIPPING_EXISTING)
        if existing and not existing.is_selected():
            helper.click_element(existing)
        continue_to(helper, SHIPPING_ADDRESS_CONTINUE, "#collapse-shipping-method.in")
    time.sleep(2)  # wait for the next step to be ready


@when('I select a delivery method')
def step_select_delivery_method(context):
    helper = context.helper
    flat_shipping_radio = helper.find_by_css("input[name='shipping_method'][value='flat.flat']")
    if not flat_shipping_radio.is_selected():
        helper.click_element(flat_shipping_radio)
    continue_to(helper, "#button-shipping-method", "#collapse-payment-method.in")
    time.sleep(2)  # wait for the next step to be ready

@when('I select a payment method')
def step_select_payment_method(context):
    helper = context.helper
    helper.find_by_css("#collapse-payment-method.in")
    cod_radio = helper.find_by_css("input[name='payment_method'][value='cod']")
    if not cod_radio.is_selected():
        helper.click_element(cod_radio)
    terms_checkbox = helper.find_by_css("#collapse-payment-method input[name='agree']")
    if not terms_checkbox.is_selected():
        helper.click_element(terms_checkbox)
    continue_to(helper, "#button-payment-method", "#collapse-checkout-confirm.in")
    time.sleep(2)  # wait for the next step to be ready


@when('I confirm the order')
def step_confirm_order(context):
    helper = context.helper
    helper.click_element(helper.find_by_css("input[value='Confirm Order']"))
    time.sleep(2)  # wait for the next step to be ready


@then('I should be on the order confirmation page')
def step_verify_order_confirmation(context):
    helper = context.helper
    helper.wait().until(lambda d: "checkout/success" in d.current_url)
    confirmation_message = helper.find_by_css("#content h1").text.strip()
    assert "Your order has been placed!" in confirmation_message, (
        f"Expected order confirmation message, but got '{confirmation_message}'"
    )


@when('I leave the mandatory billing fields empty')
def step_leave_mandatory_billing_fields_empty(context):
    helper = context.helper
    helper.find_by_css(BILLING_CONTINUE)  

    new_address_radio = displayed(helper, BILLING_NEW)
    if new_address_radio:
        if not new_address_radio.is_selected():
            helper.click_element(new_address_radio)

    for field_id in [
        "input-payment-firstname",
        "input-payment-lastname",
        "input-payment-address-1",
        "input-payment-city",
    ]:
        helper.find_by_id(field_id).clear()

    helper.click_element(helper.find_by_css(BILLING_CONTINUE))


@then('I should see validation feedback for the missing required fields')
def step_verify_validation_feedback(context):
    helper = context.helper
    first_name_feedback = billing_error(helper, "firstname")
    last_name_feedback = billing_error(helper, "lastname")
    address_feedback = billing_error(helper, "address-1")
    city_feedback = billing_error(helper, "city")

    assert "First Name must be between 1 and 32 characters!" in first_name_feedback, (
        f"Expected validation feedback for First Name, but got '{first_name_feedback}'"
    )
    assert "Last Name must be between 1 and 32 characters!" in last_name_feedback, (
        f"Expected validation feedback for Last Name, but got '{last_name_feedback}'"
    )
    
    assert "must be between 3 and 128 characters" in address_feedback, (
        f"Expected validation feedback for Address, but got '{address_feedback}'"
    )
    assert "City must be between 2 and 128 characters!" in city_feedback, (
        f"Expected validation feedback for City, but got '{city_feedback}'"
    )


@given('my cart is empty')
def step_empty_cart(context):
    helper = context.helper
    helper.open(CART_URL)
    
    while True:
        remove_buttons = helper.find_all_by_css("#content .table-responsive .btn-danger")
        if not remove_buttons:
            break
        helper.click_element(remove_buttons[0])
        helper.wait().until(EC.staleness_of(remove_buttons[0]))


@when('I navigate to the checkout page')
def step_navigate_to_checkout(context):
    helper = context.helper
    helper.open(CHECKOUT_URL)


@then('the page should show my cart is empty')
def step_verify_empty_cart(context):
    helper = context.helper
    assert "checkout/checkout" not in helper.driver.current_url, "Checkout page opened with an empty cart"
    assert "checkout/cart" in helper.driver.current_url, (
        f"Expected to be redirected to the cart page, but was on {helper.driver.current_url}"
    )
    message = helper.find_by_xpath("//div[@id='content']//p[contains(.,'Your shopping cart is empty')]").text.strip()
    assert "Your shopping cart is empty!" in message, f"Expected empty cart message, but got '{message}'"