# MyObservatory Testing Framework

A comprehensive testing framework for the MyObservatory mobile application and Weather API, built with **Python 3**, **Appium**, **pytest**, **pytest-bdd**, and **requests**.

## Features

- **Multi-platform support**: Test both Android and iOS applications
- **API testing**: Test RESTful APIs with retry logic and robust error handling
- **BDD approach**: Behavior-Driven Development using Gherkin syntax
- **Flexible configuration**: Support for local and Docker-based Appium servers
- **Dependency injection**: Multi-layer DI using pytest fixtures
- **Page Object Model**: Clean, maintainable page objects with robust element handling
- **Fallback mechanisms**: Automatic fallbacks for element locators and actions
- **Rich reporting**: HTML reports, screenshots on failure, detailed logging
- **uv package management**: Fast, modern Python package management

## Requirements

- Python 3.10+
- uvpackage manager
- Appium Server 2.x
- Android SDK
- Xcode
- Node.js and npm

## Quick Start

### 1. Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or use pip
pip install uv
```

### 2. Clone and Setup

```bash
cd MyObservatory-Testing-Project

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# - Set platform (android/ios)
# - Configure Appium server (local/docker)
# - Set device details
```

### 4. Install and Start Appium

```bash
# Install Appium
npm install -g appium

# Install drivers
appium driver install uiautomator2  # For Android
appium driver install xcuitest      # For iOS

# Start Appium server
appium --port 4723
```

### 5. Run Tests

```bash
# Run all tests
pytest

# Run mobile tests only
pytest -m mobile

# Run API tests only
pytest -m api

# Run smoke tests
pytest -m smoke

# Run with parallel execution
pytest -n auto

# Run specific feature
pytest tests/step_defs/test_mobile_navigation_steps.py
```

### YAML Configuration (config/config.yaml)

The framework uses a layered configuration approach:
1. Default values in `config.yaml`
2. Environment variables override defaults
3. Fallback mechanisms for robustness


## Running Tests

### By Platform

```bash
# Android tests
pytest -m android

# iOS tests
pytest -m ios
```

### By Test Type

```bash
# Mobile app tests
pytest -m mobile

# API tests
pytest -m api

# Smoke tests (critical functionality)
pytest -m smoke

# Regression tests
pytest -m regression
```

### With Specific Configuration

```bash
# Override platform
TEST_PLATFORM=ios pytest -m mobile

# Use Docker Appium server
APPIUM_SERVER_TYPE=docker pytest

# Increase timeout for slow tests
EXPLICIT_WAIT=30 pytest -m slow
```


## Troubleshooting

### Appium Connection Issues

```bash
# Check Appium is running
curl http://localhost:4723/status

# Check device is connected
adb devices        # Android
xcrun simctl list  # iOS
```

### Element Not Found

- Check locator strategy in page objects
- Increase wait timeouts in `.env`
- Use `scroll_to_element()` for off-screen elements


## Best Practices

1. **Use BDD for readability**: Write tests in Gherkin for stakeholder understanding
2. **Leverage fixtures**: Use dependency injection for clean test code
3. **Handle edge cases**: Framework includes extensive fallback mechanisms
4. **Configure, don't hardcode**: Use environment variables and config files
5. **Log extensively**: Comprehensive logging aids debugging
6. **Screenshot failures**: Automatically captured for failed tests
7. **Use markers**: Organize tests with pytest markers (`@pytest.mark.smoke`)