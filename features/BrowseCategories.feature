Feature: Browse product by Categories

Scenario: Open a category from the main navigation
    Given I am on the OpenCart homepage
    When I select the category "Components" from the main navigation
    And I select the "Show All Components"
    Then I should be on the "Components" category page
    And the page heading should contain "Components"

Scenario: Select a subcategory from a category page
    Given I am on the "Components" category page
    When I select the subcategory "Monitors"
    Then I should be on the "Monitors" subcategory page
    And the page heading should contain "Monitors"
    And at least one product should be displayed

Scenario: Sort products in a subcategory by price
    Given I am on the "Monitors" subcategory page
    When I sort the products by "Price (Low > High)"
    Then the products should be listed in ascending price order
    When I sort the products by "Price (High > Low)"
    Then the products should be listed in descending price order
