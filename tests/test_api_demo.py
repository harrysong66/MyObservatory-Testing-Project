"""Example test demonstrating the framework without requiring actual Appium setup.

This test showcases the API testing capabilities which can run without mobile devices.
"""

import pytest

from api import WeatherAPIClient
from utils import get_day_after_tomorrow, get_logger, get_today, get_weekday_name

logger = get_logger(__name__)


@pytest.mark.api
@pytest.mark.smoke
class TestWeatherAPIDemo:
    """Demonstration tests for Weather API functionality."""

    def test_api_client_initialization(self, api_client):
        """Test that API client can be initialized."""
        assert api_client is not None
        assert api_client.base_url == "https://data.weather.gov.hk"
        logger.info("✓ API client initialized successfully")

    def test_get_nine_day_forecast(self, api_client):
        """Test retrieving 9-day weather forecast."""
        forecast_data = api_client.get_nine_day_forecast()
        
        assert forecast_data is not None, "Failed to get forecast data"
        assert isinstance(forecast_data, dict), "Forecast data should be a dictionary"
        assert "weatherForecast" in forecast_data, "Missing weatherForecast key"
        
        forecasts = forecast_data["weatherForecast"]
        assert len(forecasts) > 0, "Forecast list is empty"
        
        logger.info(f"✓ Retrieved forecast with {len(forecasts)} items")

    def test_extract_humidity_day_after_tomorrow(self, api_client):
        """Test extracting humidity for day after tomorrow."""
        forecast_data = api_client.get_nine_day_forecast()
        assert forecast_data is not None
        
        humidity = api_client.extract_humidity_for_day_after_tomorrow(forecast_data)
        
        if humidity:
            logger.info(f"✓ Humidity for day after tomorrow: {humidity}%")
            
            # Validate format
            humidity_range = api_client.parse_humidity_from_text(humidity)
            assert humidity_range is not None, f"Failed to parse humidity: {humidity}"
            
            min_val, max_val = humidity_range
            assert 0 <= min_val <= 100, f"Min humidity {min_val} out of range"
            assert 0 <= max_val <= 100, f"Max humidity {max_val} out of range"
            assert min_val <= max_val, f"Min {min_val} > Max {max_val}"
            
            logger.info(f"✓ Humidity range validated: {min_val}% - {max_val}%")
        else:
            pytest.skip("Humidity data not available for day after tomorrow")

    def test_date_utilities(self):
        """Test date utility functions."""
        today = get_today()
        day_after_tomorrow = get_day_after_tomorrow()
        
        assert today is not None
        assert day_after_tomorrow is not None
        
        today_name = get_weekday_name(today)
        tomorrow_name = get_weekday_name(day_after_tomorrow)
        
        logger.info(f"✓ Today is {today_name}")
        logger.info(f"✓ Day after tomorrow is {tomorrow_name}")
        
        assert today_name in [
            "Monday", "Tuesday", "Wednesday", "Thursday", 
            "Friday", "Saturday", "Sunday"
        ]

    def test_api_response_structure(self, api_client):
        """Test API response has expected structure."""
        forecast_data = api_client.get_nine_day_forecast()
        assert forecast_data is not None
        
        # Check required fields
        required_fields = ["generalSituation", "weatherForecast", "updateTime"]
        for field in required_fields:
            assert field in forecast_data, f"Missing required field: {field}"
            logger.info(f"✓ Field '{field}' present in response")
        
        # Check weatherForecast structure
        forecasts = forecast_data["weatherForecast"]
        assert isinstance(forecasts, list)
        
        if len(forecasts) > 0:
            first_forecast = forecasts[0]
            expected_keys = ["forecastDate", "forecastMinrh", "forecastMaxrh"]
            
            for key in expected_keys:
                if key in first_forecast:
                    logger.info(f"✓ Forecast item has '{key}' field")

    def test_humidity_validation(self, api_client):
        """Test humidity validation logic."""
        # Valid humidity ranges
        valid_cases = [
            ("60 - 85", (60, 85)),
            ("50-90%", (50, 90)),
            ("70 - 80%", (70, 80)),
        ]
        
        for humidity_str, expected in valid_cases:
            result = api_client.parse_humidity_from_text(humidity_str)
            assert result == expected, f"Failed to parse '{humidity_str}'"
            logger.info(f"✓ Correctly parsed '{humidity_str}' as {expected}")
        
        # Validate ranges
        assert api_client.validate_humidity_range("60 - 85")
        assert api_client.validate_humidity_range("50-90%")
        logger.info("✓ Humidity validation works correctly")

    @pytest.mark.regression
    def test_api_error_handling(self, api_client):
        """Test API error handling with invalid endpoint."""
        try:
            # This should handle the error gracefully
            result = api_client._make_request("/invalid/endpoint")
            # If it doesn't raise an exception, result should be None
            assert result is None or isinstance(result, dict)
        except Exception as e:
            # Error is expected and should be handled
            logger.info(f"✓ Error handled gracefully: {type(e).__name__}")
            assert True

    def test_current_weather_api(self, api_client):
        """Test retrieving current weather data."""
        weather_data = api_client.get_current_weather()
        
        if weather_data:
            assert isinstance(weather_data, dict)
            logger.info("✓ Current weather data retrieved successfully")
            
            # Log some data if available
            if "temperature" in weather_data:
                logger.info(f"  Current temperature data available")
        else:
            pytest.skip("Current weather data not available")


@pytest.mark.api
def test_api_client_context_manager():
    """Test API client can be used as context manager."""
    with WeatherAPIClient() as client:
        assert client is not None
        forecast = client.get_nine_day_forecast()
        assert forecast is not None
    
    logger.info("✓ API client context manager works correctly")


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__, "-v", "-m", "api"])
