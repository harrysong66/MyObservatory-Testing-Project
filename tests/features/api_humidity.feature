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

  @api @regression
  Scenario: Validate humidity data format
    When I request the 9-day weather forecast
    And I extract humidity for day after tomorrow
    Then the humidity should contain minimum and maximum values
    And minimum humidity should be less than or equal to maximum humidity
    And humidity values should be valid percentages

  @api @regression
  Scenario Outline: Extract humidity for specific day offset
    When I request the 9-day weather forecast
    Then I should be able to extract humidity for day offset <day_offset>

    Examples:
      | day_offset | description        |
      | 0          | today              |
      | 1          | tomorrow           |
      | 2          | day after tomorrow |
      | 3          | three days ahead   |

  @api @smoke
  Scenario: API response includes all required fields
    When I request the 9-day weather forecast
    Then the response should contain the following fields:
      | field                |
      | generalSituation     |
      | weatherForecast      |
      | updateTime           |

  @api @regression
  Scenario: Handle API errors gracefully
    When I request weather data from an invalid endpoint
    Then the API client should handle the error
    And return None without crashing

  @api @smoke
  Scenario: Verify day after tomorrow humidity matches expected format
    Given today is a weekday
    When I request the 9-day weather forecast
    And I extract the relative humidity for day after tomorrow
    Then the humidity format should match pattern "\\d+ - \\d+"
    And I should be able to parse the humidity range

  @api @regression
  Scenario: Compare app and API humidity data
    When I request the 9-day weather forecast via API
    And I extract humidity for day after tomorrow from API response
    Then the humidity data should be available
    And the humidity should be in valid range "0-100%"
