Feature: Wishlist Management
    As a logged-in user
    I want to add, view, and remove products from my wishlist
    So that I can save products I am interested in and manage them later

Background:
    Given I am logged in as a registered user

Scenario: Add a product to the wishlist
    Given my wishlist is empty
    And I am on the product page for "HTC Touch HD"
    When I add the product to my wishlist
    Then I should see a confirmation that the product was added to the wishlist
    And the wishlist should contain "HTC Touch HD"

Scenario: Add wishlist item to cart
    Given product "HTC Touch HD" is in my wishlist
    When I open the wishlist page
    And I add product "HTC Touch HD" to my cart
    Then the cart should contain "HTC Touch HD"

Scenario: Remove a product from the wishlist
    Given product "HTC Touch HD" is in my wishlist
    When I remove "HTC Touch HD" from my wishlist
    Then I should see a confirmation that the product was removed from the wishlist
    And the wishlist should not contain "HTC Touch HD"