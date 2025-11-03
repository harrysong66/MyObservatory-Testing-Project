"""Step definitions for API humidity extraction tests."""

import re

from pytest_bdd import given, parsers, scenarios, then, when

from utils import get_logger

logger = get_logger(__name__)

# Load all scenarios from the feature file
scenarios("../features/api_humidity.feature")


@given("the Weather API is accessible", target_fixture="api_accessible")
def api_is_accessible(api_client):
    """Verify API is accessible.
    
    Args:
        api_client: WeatherAPIClient fixture
    """
    logger.info("Verifying Weather API is accessible")
    assert api_client is not None, "API client is not initialized"
    return True


@when("I request the 9-day weather forecast", target_fixture="forecast_data")
def request_nine_day_forecast(api_client, context):
    logger.info("Requesting 9-day weather forecast")

    forecast_data = api_client.get_nine_day_forecast()

    assert forecast_data is not None, "Failed to get forecast data"
    logger.info("Successfully retrieved 9-day forecast")

    context["forecast_data"] = forecast_data
    return forecast_data

@then("the API should return a successful response")
def api_returns_success(context):
    logger.info("Verifying API response is successful")

    forecast_data = context.get("forecast_data")
    assert forecast_data is not None, "Forecast data is None"
    assert isinstance(forecast_data, dict), "Forecast data is not a dictionary"

    logger.info("API response is successful")


@then("the response should contain forecast data")
def response_contains_forecast_data(context):
    logger.info("Verifying response contains forecast data")

    forecast_data = context.get("forecast_data")
    assert forecast_data, "Forecast data is empty"
    assert len(forecast_data) > 0, "Forecast data has no content"

    logger.info(f"Response contains {len(forecast_data)} keys")


@then("the forecast should include weatherForecast array")
def forecast_includes_weather_forecast_array(context):
    logger.info("Verifying weatherForecast array exists")

    forecast_data = context.get("forecast_data")
    assert "weatherForecast" in forecast_data, "weatherForecast key not found"

    weather_forecast = forecast_data["weatherForecast"]
    assert isinstance(weather_forecast, list), "weatherForecast is not a list"
    assert len(weather_forecast) > 0, "weatherForecast array is empty"

    logger.info(f"weatherForecast array contains {len(weather_forecast)} items")


@then("I should extract the relative humidity for day after tomorrow")
def should_extract_humidity_day_after_tomorrow(api_client, context):
    logger.info("Extracting humidity for day after tomorrow")

    forecast_data = context.get("forecast_data")
    humidity = api_client.extract_humidity_for_day_after_tomorrow(forecast_data)

    assert humidity is not None, "Failed to extract humidity"

    context["humidity"] = humidity
    logger.info(f"Successfully extracted humidity: {humidity}")


@then(parsers.parse('the humidity should be in format "{format_pattern}"'))
def humidity_in_format(context, format_pattern):
    logger.info(f"Verifying humidity format: {format_pattern}")

    humidity = context.get("humidity")
    assert humidity is not None, "Humidity is None"

    # Check format matches pattern
    if format_pattern == "XX - YY":
        pattern = r'\d+\s*-\s*\d+'
        assert re.search(pattern, humidity), f"Humidity '{humidity}' does not match format '{format_pattern}'"

    logger.info(f"Humidity format is valid: {humidity}")


@then("the humidity values should be between 0 and 100")
def humidity_values_in_range(api_client, context):
    logger.info("Verifying humidity values are in valid range")

    humidity = context.get("humidity")
    assert humidity is not None, "Humidity is None"

    # Parse humidity range
    humidity_range = api_client.parse_humidity_from_text(humidity)
    assert humidity_range is not None, f"Failed to parse humidity: {humidity}"

    min_val, max_val = humidity_range

    assert 0 <= min_val <= 100, f"Minimum humidity {min_val} is out of range"
    assert 0 <= max_val <= 100, f"Maximum humidity {max_val} is out of range"

    logger.info(f"Humidity values are in valid range: {min_val}% - {max_val}%")

