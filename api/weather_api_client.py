"""Weather API client with retry logic and error handling."""

import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from urllib3.util.retry import Retry

from config import config
from utils import get_logger

logger = get_logger(__name__)


class WeatherAPIClient:
    """Client for Hong Kong Observatory Weather API with robust error handling."""

    def __init__(self):
        """Initialize Weather API client."""
        self.base_url = config.api.base_url
        self.timeout = config.api.timeout
        self.max_retries = config.api.retry_count
        
        # Get retry configuration from YAML
        retry_config = config.get_yaml_value("api", "retry", default={})
        self.retry_delay = retry_config.get("delay", 1)
        self.backoff_factor = retry_config.get("backoff_factor", 2)
        
        # Setup session with retry strategy
        self.session = self._create_session()
        
        logger.info(f"WeatherAPIClient initialized with base URL: {self.base_url}")

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[500, 502, 503, 504, 429],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        headers_config = config.get_yaml_value("api", "headers", default={})
        session.headers.update(headers_config)
        
        return session

    @retry(
        retry=retry_if_exception_type((requests.Timeout, requests.ConnectionError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        timeout_value = timeout or self.timeout
        
        logger.debug(f"Making request to: {url}")
        logger.debug(f"Parameters: {params}")
        
        try:
            response = self.session.get(url, params=params, timeout=timeout_value)
            response.raise_for_status()
            
            logger.info(f"Request successful: {url}")
            return response.json()
            
        except requests.Timeout as e:
            logger.error(f"Request timeout: {url}")
            raise
        except requests.ConnectionError as e:
            logger.error(f"Connection error: {url}")
            raise
        except requests.HTTPError as e:
            logger.error(f"HTTP error {response.status_code}: {url}")
            raise
        except requests.RequestException as e:
            logger.error(f"Request failed: {url} - {e}")
            raise
        except ValueError as e:
            logger.error(f"Invalid JSON response: {url} - {e}")
            raise

    def get_nine_day_forecast(self) -> Optional[Dict[str, Any]]:
        logger.info("Fetching 9-day weather forecast")
        
        try:
            # Endpoint from YAML config
            endpoint = config.get_yaml_value(
                "api", "endpoints", "nine_day_forecast",
                default="/weatherAPI/opendata/weather.php?dataType=fnd&lang=en"
            )
            
            data = self._make_request(endpoint)
            
            if data:
                logger.info("9-day forecast retrieved successfully")
                logger.debug(f"Forecast data keys: {list(data.keys())}")
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get 9-day forecast: {e}")
            return None

    def get_current_weather(self) -> Optional[Dict[str, Any]]:
        logger.info("Fetching current weather")
        
        try:
            endpoint = config.get_yaml_value(
                "api", "endpoints", "current_weather",
                default="/weatherAPI/opendata/weather.php?dataType=rhrread&lang=en"
            )
            
            data = self._make_request(endpoint)
            
            if data:
                logger.info("Current weather retrieved successfully")
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get current weather: {e}")
            return None

    def get_weather_warning(self) -> Optional[Dict[str, Any]]:
        logger.info("Fetching weather warning")
        
        try:
            endpoint = config.get_yaml_value(
                "api", "endpoints", "weather_warning",
                default="/weatherAPI/opendata/weather.php?dataType=warnsum&lang=en"
            )
            
            data = self._make_request(endpoint)
            
            if data:
                logger.info("Weather warning retrieved successfully")
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get weather warning: {e}")
            return None

    def extract_forecast_for_date(
        self,
        date: datetime,
        forecast_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        logger.info(f"Extracting forecast for date: {date.strftime('%Y-%m-%d')}")
        
        # Fetch forecast data if not provided
        if forecast_data is None:
            forecast_data = self.get_nine_day_forecast()
        
        if not forecast_data:
            logger.error("No forecast data available")
            return None
        
        try:
            # Get forecast list
            forecasts = forecast_data.get("weatherForecast", [])
            
            if not forecasts:
                logger.warning("No forecast items found in data")
                return None
            
            # Find matching forecast by date
            target_date_str = date.strftime("%Y%m%d")
            
            for forecast in forecasts:
                forecast_date = forecast.get("forecastDate", "")
                
                # Try to match date
                if forecast_date == target_date_str:
                    logger.info(f"Found forecast for {date.strftime('%Y-%m-%d')}")
                    return forecast
            
            logger.warning(f"No forecast found for date: {date.strftime('%Y-%m-%d')}")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting forecast for date: {e}")
            return None

    def extract_humidity_for_day_offset(
        self,
        day_offset: int = 0,
        forecast_data: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        logger.info(f"Extracting humidity for day offset: {day_offset}")
        
        # Calculate target date
        target_date = datetime.now() + timedelta(days=day_offset)
        
        # Get forecast for the date
        forecast = self.extract_forecast_for_date(target_date, forecast_data)
        
        if not forecast:
            return None
        
        # Extract humidity
        humidity_min = forecast.get("forecastMinrh", {})
        humidity_max = forecast.get("forecastMaxrh", {})
        
        # Get values
        min_val = humidity_min.get("value")
        max_val = humidity_max.get("value")
        
        if min_val is not None and max_val is not None:
            humidity_str = f"{min_val} - {max_val}"
            logger.info(f"Humidity for day {day_offset}: {humidity_str}%")
            return humidity_str
        
        logger.warning(f"Humidity data not found for day {day_offset}")
        return None

    def extract_humidity_for_day_after_tomorrow(
        self,
        forecast_data: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        logger.info("Extracting humidity for day after tomorrow")
        return self.extract_humidity_for_day_offset(day_offset=2, forecast_data=forecast_data)

    def parse_humidity_from_text(self, text: str) -> Optional[tuple]:
        pattern = r'(\d+)\s*%?\s*[-–]\s*(\d+)\s*%?'
        
        match = re.search(pattern, text)
        if match:
            min_humidity = int(match.group(1))
            max_humidity = int(match.group(2))
            logger.debug(f"Parsed humidity: {min_humidity}% - {max_humidity}%")
            return (min_humidity, max_humidity)
        
        return None

    def validate_humidity_range(
        self,
        humidity_str: str,
        expected_min: Optional[int] = None,
        expected_max: Optional[int] = None
    ) -> bool:
        humidity_range = self.parse_humidity_from_text(humidity_str)
        
        if not humidity_range:
            logger.error(f"Failed to parse humidity: {humidity_str}")
            return False
        
        min_val, max_val = humidity_range
        
        # Validate range makes sense
        if min_val > max_val:
            logger.error(f"Invalid humidity range: min ({min_val}) > max ({max_val})")
            return False
        
        # Validate against expected values
        if expected_min is not None and min_val < expected_min:
            logger.error(f"Minimum humidity {min_val}% below expected {expected_min}%")
            return False
        
        if expected_max is not None and max_val > expected_max:
            logger.error(f"Maximum humidity {max_val}% above expected {expected_max}%")
            return False
        
        logger.info(f"Humidity range validated: {min_val}% - {max_val}%")
        return True

    def close(self) -> None:
        """Close the session."""
        try:
            self.session.close()
            logger.info("API client session closed")
        except Exception as e:
            logger.error(f"Error closing session: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
