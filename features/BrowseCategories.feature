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
    And I should see a list of products in the subcategory

Scenario Outline: Sort products in a subcategory by price
    Given I am on the "Monitors" subcategory page
    When I sort the products by "<sort_option>"
    Then the products should be listed in <order> price order

    Examples:
        | sort_option        | order      |
        | Price (Low > High) | ascending  |
        | Price (High > Low) | descending |