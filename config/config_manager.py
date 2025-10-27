"""Configuration management module.

This module handles loading and managing configuration from multiple sources:
1. config.yaml (default configuration)
2. Environment variables (override config.yaml)
3. Fallback values for robustness
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()

class AppiumServerConfig(BaseSettings):
    """Appium server configuration."""

    type: str = Field(default="local", description="Server type: local or docker")
    local_host: str = Field(default="127.0.0.1", alias="APPIUM_LOCAL_HOST")
    local_port: int = Field(default=4723, alias="APPIUM_LOCAL_PORT")
    docker_host: str = Field(default="localhost", alias="APPIUM_DOCKER_HOST")
    docker_port: int = Field(default=4723, alias="APPIUM_DOCKER_PORT")
    timeout: int = Field(default=60)

    model_config = {
        "extra": "ignore",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "populate_by_name": True,
    }


class AndroidConfig(BaseSettings):
    """Android platform configuration."""

    platform_name: str = Field(default="Android", alias="ANDROID_PLATFORM_NAME")
    platform_version: str = Field(default="13.0", alias="ANDROID_PLATFORM_VERSION")
    device_name: str = Field(default="Android Emulator", alias="ANDROID_DEVICE_NAME")
    udid: str = Field(default="emulator-5554", alias="ANDROID_UDID")
    device_type: str = Field(default="emulator", alias="ANDROID_DEVICE_TYPE")
    app_package: str = Field(default="hko.MyObservatory_v1_0", alias="ANDROID_APP_PACKAGE")
    app_activity: str = Field(default=".AgreementPage", alias="ANDROID_APP_ACTIVITY")
    app_path: str = Field(default="", alias="ANDROID_APP_PATH")
    automation_name: str = Field(default="UiAutomator2", alias="ANDROID_AUTOMATION_NAME")
    auto_grant_permissions: bool = Field(default=True, alias="ANDROID_AUTO_GRANT_PERMISSIONS")
    no_reset: bool = Field(default=False, alias="ANDROID_NO_RESET")
    full_reset: bool = Field(default=False, alias="ANDROID_FULL_RESET")

    model_config = {
        "extra": "ignore",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "populate_by_name": True,
    }


class IOSConfig(BaseSettings):
    """iOS platform configuration."""

    platform_name: str = Field(default="iOS", alias="IOS_PLATFORM_NAME")
    platform_version: str = Field(default="16.0", alias="IOS_PLATFORM_VERSION")
    device_name: str = Field(default="iPhone 14", alias="IOS_DEVICE_NAME")
    udid: str = Field(default="auto", alias="IOS_UDID")
    device_type: str = Field(default="simulator", alias="IOS_DEVICE_TYPE")
    bundle_id: str = Field(default="hk.gov.hko.MyObservatory", alias="IOS_BUNDLE_ID")
    app_path: str = Field(default="", alias="IOS_APP_PATH")
    automation_name: str = Field(default="XCUITest", alias="IOS_AUTOMATION_NAME")
    auto_accept_alerts: bool = Field(default=True, alias="IOS_AUTO_ACCEPT_ALERTS")
    no_reset: bool = Field(default=False, alias="IOS_NO_RESET")
    full_reset: bool = Field(default=False, alias="IOS_FULL_RESET")

    model_config = {
        "extra": "ignore",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "populate_by_name": True,
    }


class APIConfig(BaseSettings):
    """API configuration."""

    base_url: str = Field(default="https://data.weather.gov.hk", alias="API_BASE_URL")
    timeout: int = Field(default=30, alias="API_TIMEOUT")
    retry_count: int = Field(default=3, alias="API_RETRY_COUNT")
    retry_delay: int = Field(default=1, alias="API_RETRY_DELAY")

    model_config = {
        "extra": "ignore",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "populate_by_name": True,
    }


class TestConfig(BaseSettings):
    """Test execution configuration."""

    platform: str = Field(default="android", alias="TEST_PLATFORM")
    implicit_wait: int = Field(default=10, alias="IMPLICIT_WAIT")
    explicit_wait: int = Field(default=20, alias="EXPLICIT_WAIT")
    capture_screenshot: bool = Field(default=True, alias="CAPTURE_SCREENSHOT")
    screenshot_dir: str = Field(default="reports/screenshots", alias="SCREENSHOT_DIR")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_dir: str = Field(default="logs", alias="LOG_DIR")
    report_dir: str = Field(default="reports", alias="REPORT_DIR")

    model_config = {
        "extra": "ignore",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "populate_by_name": True,
    }


class ConfigManager:
    """Central configuration manager with fallback support."""

    _instance: Optional["ConfigManager"] = None
    _yaml_config: Dict[str, Any] = {}

    def __new__(cls):
        """Singleton pattern to ensure single instance."""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_yaml_config()
        return cls._instance

    def _load_yaml_config(self) -> None:
        """Load configuration from YAML file with fallback."""
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        try:
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    self._yaml_config = yaml.safe_load(f) or {}
            else:
                print(f"Warning: Config file not found at {config_path}. Using defaults.")
                self._yaml_config = {}
        except Exception as e:
            print(f"Error loading config file: {e}. Using defaults.")
            self._yaml_config = {}

    def get_yaml_value(self, *keys: str, default: Any = None) -> Any:
        value = self._yaml_config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    @property
    def appium_server(self) -> AppiumServerConfig:
        """Get Appium server configuration."""
        server_type = os.getenv("APPIUM_SERVER_TYPE", "local")
        config = AppiumServerConfig(type=server_type)

        # Override with YAML if not set in env
        if not os.getenv("APPIUM_LOCAL_HOST"):
            config.local_host = self.get_yaml_value(
                "appium", "server", "local", "host", default=config.local_host
            )
        if not os.getenv("APPIUM_LOCAL_PORT"):
            config.local_port = self.get_yaml_value(
                "appium", "server", "local", "port", default=config.local_port
            )

        return config

    @property
    def android(self) -> AndroidConfig:
        """Get Android configuration."""
        config = AndroidConfig()

        # Merge with YAML config for device type
        device_type = config.device_type
        yaml_device = self.get_yaml_value("android", "device", device_type, default={})

        # Override with YAML if not set in env
        if not os.getenv("ANDROID_DEVICE_NAME") and yaml_device:
            config.device_name = yaml_device.get("deviceName", config.device_name)
        if not os.getenv("ANDROID_PLATFORM_VERSION") and yaml_device:
            config.platform_version = yaml_device.get("platformVersion", config.platform_version)

        return config

    @property
    def ios(self) -> IOSConfig:
        """Get iOS configuration."""
        config = IOSConfig()

        # Merge with YAML config for device type
        device_type = config.device_type
        yaml_device = self.get_yaml_value("ios", "device", device_type, default={})

        # Override with YAML if not set in env
        if not os.getenv("IOS_DEVICE_NAME") and yaml_device:
            config.device_name = yaml_device.get("deviceName", config.device_name)
        if not os.getenv("IOS_PLATFORM_VERSION") and yaml_device:
            config.platform_version = yaml_device.get("platformVersion", config.platform_version)

        return config

    @property
    def api(self) -> APIConfig:
        """Get API configuration."""
        config = APIConfig()

        # Override with YAML if not set in env
        if not os.getenv("API_BASE_URL"):
            config.base_url = self.get_yaml_value("api", "base_url", default=config.base_url)
        if not os.getenv("API_TIMEOUT"):
            config.timeout = self.get_yaml_value("api", "timeout", default=config.timeout)

        return config

    @property
    def test(self) -> TestConfig:
        """Get test configuration."""
        config = TestConfig()

        # Override with YAML if not set in env
        if not os.getenv("IMPLICIT_WAIT"):
            config.implicit_wait = self.get_yaml_value(
                "test", "waits", "implicit", default=config.implicit_wait
            )
        if not os.getenv("EXPLICIT_WAIT"):
            config.explicit_wait = self.get_yaml_value(
                "test", "waits", "explicit", default=config.explicit_wait
            )

        return config

    def get_appium_url(self) -> str:
        """Get Appium server URL based on configuration.
        
        Returns:
            Appium server URL with fallback
        """
        server_config = self.appium_server

        if server_config.type.lower() == "docker":
            host = server_config.docker_host
            port = server_config.docker_port
        else:
            host = server_config.local_host
            port = server_config.local_port

        return f"http://{host}:{port}"

    def get_capabilities(self, platform: Optional[str] = None) -> Dict[str, Any]:
        platform = platform or self.test.platform
        platform = platform.lower()

        if platform == "android":
            return self._get_android_capabilities()
        elif platform == "ios":
            return self._get_ios_capabilities()
        else:
            raise ValueError(f"Unsupported platform: {platform}")

    def _get_android_capabilities(self) -> Dict[str, Any]:
        """Generate Android capabilities."""
        android_config = self.android

        capabilities = {
            "platformName": android_config.platform_name,
            "platformVersion": android_config.platform_version,
            "deviceName": android_config.device_name,
            "automationName": android_config.automation_name,
            "appPackage": android_config.app_package,
            "appActivity": android_config.app_activity,
            "noReset": android_config.no_reset,
            "fullReset": android_config.full_reset,
            "autoGrantPermissions": android_config.auto_grant_permissions,
            "newCommandTimeout": 300,
        }

        # Add UDID for specific device
        if android_config.udid and android_config.udid != "auto":
            capabilities["udid"] = android_config.udid

        # Add app path if specified
        if android_config.app_path and os.path.exists(android_config.app_path):
            capabilities["app"] = android_config.app_path

        return capabilities

    def _get_ios_capabilities(self) -> Dict[str, Any]:
        """Generate iOS capabilities."""
        ios_config = self.ios

        capabilities = {
            "platformName": ios_config.platform_name,
            "platformVersion": ios_config.platform_version,
            "deviceName": ios_config.device_name,
            "automationName": ios_config.automation_name,
            "bundleId": ios_config.bundle_id,
            "noReset": ios_config.no_reset,
            "fullReset": ios_config.full_reset,
            "autoAcceptAlerts": ios_config.auto_accept_alerts,
            "newCommandTimeout": 300,
        }

        # Add UDID for specific device
        if ios_config.udid and ios_config.udid != "auto":
            capabilities["udid"] = ios_config.udid

        # Add app path if specified
        if ios_config.app_path and os.path.exists(ios_config.app_path):
            capabilities["app"] = ios_config.app_path

        return capabilities


# Global config instance
config = ConfigManager()
