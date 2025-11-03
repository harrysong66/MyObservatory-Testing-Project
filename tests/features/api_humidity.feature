Feature: Weather API - Humidity Extraction
  As a weather data consumer
  I want to retrieve humidity information from the Weather API
  So that I can get accurate relative humidity forecasts

  Background:
    Given the Weather API is accessible

  @api @smoke
  Scenario: Retrieve 9-day weather forecast
    When I request the 9-day weather forecast
    Then the API should return a successful response
    And the response should contain forecast data
    And the forecast should include weatherForecast array

  @api @smoke
  Scenario: Extract relative humidity for day after tomorrow
    When I request the 9-day weather forecast
    Then I should extract the relative humidity for day after tomorrow
    And the humidity should be in format "XX - YY"
    And the humidity values should be between 0 and 100