Feature: MyObservatory App Navigation
  As a user of the MyObservatory app
  I want to navigate through different forecast sections
  So that I can view detailed weather information

  Background:
    Given the MyObservatory app is launched

  @mobile @android @ios @smoke @regression
  Scenario: Navigate to 9-Day Forecast
    Given I am on the agreement page
    When I accept the agreement
    Then I should see the "Slide" page
    When I slide and close the slide page
    Then I should see the "Home" page
    When I tap on "Hamburger Menu"
    Then I should see the "Navigation Drawer" page
    When I tap on "Forecast & Warning Services"
    And I tap on "9-Day Forecast"
    Then I should see the "9-Day Forecast" page
    And the page should display "9th" day's forecast information