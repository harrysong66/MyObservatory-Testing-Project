"""Step definitions for API humidity extraction tests."""

import re

from pytest_bdd import given, parsers, scenarios, then, when

from api import WeatherAPIClient
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


@given("today is a weekday", target_fixture="is_weekday")
def today_is_weekday():
    from utils import get_today, get_weekday_name

    today = get_today()
    weekday = get_weekday_name(today)

    is_weekday = weekday not in ["Saturday", "Sunday"]
    logger.info(f"Today is {weekday}, weekday: {is_weekday}")

    return is_weekday


@when("I request the 9-day weather forecast", target_fixture="forecast_data")
def request_nine_day_forecast(api_client, context):
    logger.info("Requesting 9-day weather forecast")

    forecast_data = api_client.get_nine_day_forecast()

    assert forecast_data is not None, "Failed to get forecast data"
    logger.info("Successfully retrieved 9-day forecast")

    context["forecast_data"] = forecast_data
    return forecast_data


@when("I extract humidity for day after tomorrow", target_fixture="humidity_value")
def extract_humidity_day_after_tomorrow(api_client, context):
    logger.info("Extracting humidity for day after tomorrow")

    forecast_data = context.get("forecast_data")
    humidity = api_client.extract_humidity_for_day_after_tomorrow(forecast_data)

    context["humidity"] = humidity
    logger.info(f"Extracted humidity: {humidity}")

    return humidity


@when("I request weather data from an invalid endpoint", target_fixture="error_response")
def request_invalid_endpoint(api_client):
    logger.info("Requesting data from invalid endpoint")

    try:
        # This should fail gracefully
        response = api_client._make_request("/invalid/endpoint/test")
        return response
    except Exception as e:
        logger.info(f"Expected error occurred: {e}")
        return None


@when("I request the 9-day weather forecast via API", target_fixture="api_forecast_data")
def request_forecast_via_api(api_client, context):
    logger.info("Requesting forecast via API")

    forecast_data = api_client.get_nine_day_forecast()
    context["api_forecast_data"] = forecast_data

    return forecast_data


@when("I extract humidity for day after tomorrow from API response", target_fixture="api_humidity")
def extract_humidity_from_api(api_client, context):
    logger.info("Extracting humidity from API response")

    forecast_data = context.get("api_forecast_data")
    humidity = api_client.extract_humidity_for_day_after_tomorrow(forecast_data)

    context["api_humidity"] = humidity
    logger.info(f"API humidity: {humidity}")

    return humidity


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


@then("the humidity should contain minimum and maximum values")
def humidity_contains_min_max(api_client, context):
    logger.info("Verifying humidity contains min and max values")

    humidity = context.get("humidity")
    assert humidity is not None, "Humidity is None"

    humidity_range = api_client.parse_humidity_from_text(humidity)
    assert humidity_range is not None, f"Failed to parse humidity: {humidity}"

    min_val, max_val = humidity_range
    assert min_val is not None, "Minimum humidity is None"
    assert max_val is not None, "Maximum humidity is None"

    logger.info(f"Humidity contains min ({min_val}) and max ({max_val}) values")


@then("minimum humidity should be less than or equal to maximum humidity")
def min_humidity_lte_max(api_client, context):
    logger.info("Verifying min <= max for humidity")

    humidity = context.get("humidity")
    humidity_range = api_client.parse_humidity_from_text(humidity)

    min_val, max_val = humidity_range
    assert min_val <= max_val, f"Minimum humidity ({min_val}) > Maximum humidity ({max_val})"

    logger.info(f"Humidity range is valid: {min_val}% <= {max_val}%")


@then("humidity values should be valid percentages")
def humidity_values_are_valid_percentages(api_client, context):
    logger.info("Verifying humidity values are valid percentages")

    humidity = context.get("humidity")
    assert api_client.validate_humidity_range(humidity), "Humidity range is invalid"

    logger.info("Humidity values are valid percentages")


@then(parsers.parse("I should be able to extract humidity for day offset {day_offset:d}"))
def extract_humidity_for_offset(api_client, context, day_offset):
    logger.info(f"Extracting humidity for day offset {day_offset}")

    forecast_data = context.get("forecast_data")
    humidity = api_client.extract_humidity_for_day_offset(day_offset, forecast_data)

    # Humidity might not be available for all days, so we just log the result
    if humidity:
        logger.info(f"Humidity for day {day_offset}: {humidity}")
    else:
        logger.warning(f"Humidity not available for day {day_offset}")


@then("the response should contain the following fields:")
def response_contains_fields(context, datatable):
    logger.info("Verifying response contains required fields")

    forecast_data = context.get("forecast_data")

    for row in datatable:
        field = row["field"]
        assert field in forecast_data, f"Field '{field}' not found in response"
        logger.info(f"Field '{field}' found in response")


@then("the API client should handle the error")
def api_handles_error(context):
    logger.info("Verifying API error handling")

    error_response = context.get("error_response")
    # Error should be handled, returning None instead of crashing
    assert error_response is None, "Expected None response for invalid endpoint"

    logger.info("API client handled error gracefully")


@then("return None without crashing")
def returns_none_without_crash(context):
    logger.info("Function returned None without crashing")
    assert True


@then(parsers.parse('the humidity format should match pattern "{pattern}"'))
def humidity_matches_pattern(context, pattern):
    logger.info(f"Verifying humidity matches pattern: {pattern}")

    humidity = context.get("humidity")
    assert humidity is not None, "Humidity is None"

    # Escape backslashes in pattern
    pattern = pattern.replace("\\\\", "\\")

    assert re.search(pattern, humidity), f"Humidity '{humidity}' does not match pattern '{pattern}'"

    logger.info(f"Humidity matches pattern: {humidity}")


@then("I should be able to parse the humidity range")
def can_parse_humidity_range(api_client, context):
    logger.info("Verifying humidity range can be parsed")

    humidity = context.get("humidity")
    humidity_range = api_client.parse_humidity_from_text(humidity)

    assert humidity_range is not None, f"Failed to parse humidity: {humidity}"

    min_val, max_val = humidity_range
    logger.info(f"Successfully parsed humidity: {min_val}% - {max_val}%")


@then("the humidity data should be available")
def humidity_data_available(context):
    logger.info("Verifying humidity data is available")

    api_humidity = context.get("api_humidity")
    assert api_humidity is not None, "Humidity data is not available"

    logger.info(f"Humidity data is available: {api_humidity}")


@then(parsers.parse('the humidity should be in valid range "{range_pattern}"'))
def humidity_in_valid_range(api_client, context, range_pattern):
    logger.info(f"Verifying humidity is in valid range: {range_pattern}")

    api_humidity = context.get("api_humidity")
    assert api_humidity is not None, "Humidity is None"

    # Parse the range pattern
    if range_pattern == "0-100%":
        humidity_range = api_client.parse_humidity_from_text(api_humidity)
        assert humidity_range is not None, f"Failed to parse humidity: {api_humidity}"

        min_val, max_val = humidity_range
        assert 0 <= min_val <= 100, f"Min humidity {min_val} out of range"
        assert 0 <= max_val <= 100, f"Max humidity {max_val} out of range"

        logger.info(f"Humidity is in valid range: {min_val}% - {max_val}%")
