Feature: Checkout
    As a logged-in user
    I want to progress through the checkout process
    So that I can place an order with valid details and see validation feedback when information is missing or invalid

Background:
    Given I am logged in as a registered user

Scenario: Complete checkout with valid details
    Given my cart contains "HTC Touch HD"
    When I proceed to checkout
    And I fill out my billing details
    And I fill out my delivery details
    And I select a delivery method
    And I select a payment method
    And I confirm the order
    Then I should be on the order confirmation page

Scenario: Checkout with missing required details
    Given my cart contains "HTC Touch HD"
    When I proceed to checkout
    And I leave the mandatory billing fields empty
    Then I should see validation feedback for the missing required fields

Scenario: Attempt checkout with an empty cart
    Given my cart is empty
    When I navigate to the checkout page
    Then the page should show my cart is empty