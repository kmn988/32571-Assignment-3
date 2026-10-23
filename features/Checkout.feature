Feature: Checkout
    As a logged-in user
    I want to progress through the checkout process
    So that I can place an order with valid details and see validation feedback when information is missing or invalid

Background:
    Given I am logged in as a registered user

Scenario: Complete checkout with valid details
    Given my cart contains "HTC Touch HD"
    And my cart total is greater than 0
    When I proceed to checkout
    Then my billing details should be pre-filled or accepted as valid
    When I continue through the delivery details step
    And I select a delivery method
    And I select a payment method
    And I confirm the order
    Then the checkout summary should show the correct product and order total
    And if the demo permits order completion, I should be on the order confirmation page

Scenario: Checkout with missing required details
    Given my cart contains "HTC Touch HD"
    When I proceed to checkout
    And I leave the mandatory billing fields empty
    And I attempt to continue
    Then I should see validation feedback for the missing required fields
    And I should remain on the current checkout step
    And the order should not be completed

Scenario: Attempt checkout with an empty cart
    Given my cart is empty
    When I navigate to the checkout page
    Then I should be prevented from checking out
    And I should be shown an empty-cart or cart page state