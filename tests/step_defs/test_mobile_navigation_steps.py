from pytest_bdd import given, parsers, scenarios, then, when
from utils import get_logger

logger = get_logger(__name__)

scenarios("../features/mobile_navigation.feature")


# --------------------------------------------
# given steps
# --------------------------------------------


@given("the MyObservatory app is launched", target_fixture="app_launched")
def app_is_launched(driver):
    logger.info("MyObservatory app is launched")
    assert driver is not None, "Driver is not initialized"
    return True


@given("I am on the agreement page", target_fixture="agreement_page_loaded")
def on_agreement_page(driver, agreement_page):
    logger.info("Navigating to MyObservatory agreement page")

    # Wait for agreement_page to load
    assert agreement_page.wait_for_agreement_page_load(timeout=20), "agreement_page failed to load"

    # Verify agreement_page is displayed
    assert agreement_page.is_agreement_page_displayed(timeout=10), "agreement_page is not displayed"

    logger.info("Successfully on MyObservatory agreement page")
    return agreement_page


# --------------------------------------------
# when steps
# --------------------------------------------


@when("I accept the agreement")
def accept_agreement(driver, agreement_page):
    logger.info("accepting the agreement")
    # Click the agree button
    assert agreement_page.click_agree_button(timeout=15), "Failed to click agree button"
    logger.info("Successfully accepted the agreement")


@when("I slide and close the slide page")
def slide_and_close_slide_page(driver, slide_page):
    logger.info("Sliding through and closing the slide page")
    assert slide_page.click_next_page_button(timeout=15), "Failed to perform slide action"
    assert slide_page.click_next_page_button(timeout=15), "Failed to perform slide action"
    assert slide_page.click_close_button(timeout=10), "Failed to close slide page"
    logger.info("Successfully slid through and closed the slide page")


@when(parsers.parse('I tap on "{button_text}"'))
def tap_on_button(driver, home_page, navigation_drawer_page, forecast_warning_page, button_text, context):
    logger.info(f"Tapping on: {button_text}")
    if button_text == "Hamburger Menu":
        success = home_page.click_hamburger_menu_button(timeout=10)
        assert success, f"Failed to tap on '{button_text}'"
        context["last_action"] = "tapped_hamburger_menu"

    if button_text == "Forecast & Warning Services":
        success = navigation_drawer_page.click_forecast_warning_services(timeout=15)
        assert success, f"Failed to tap on '{button_text}'"
        context["last_action"] = "tapped_forecast_warning"
        
    elif button_text == "9-Day Forecast":
        success = forecast_warning_page.click_nine_day_forecast(timeout=15)
        assert success, f"Failed to tap on '{button_text}'"
        context["last_action"] = "tapped_nine_day_forecast"
        
    else:
        raise ValueError(f"Unknown button: {button_text}")
    
    logger.info(f"Successfully tapped on: {button_text}")


@when(parsers.parse('I navigate to "{page_name}" page'))
def navigate_to_page(driver, home_page, forecast_warning_page, nine_day_forecast_page, page_name, context):
    logger.info(f"Navigating to {page_name} page")
    
    if page_name == "9-Day Forecast":
        # Full navigation flow
        assert home_page.click_forecast_warning_services(timeout=15), "Failed to click Forecast & Warning"
        assert forecast_warning_page.wait_for_page_load(timeout=20), "Forecast & Warning page failed to load"
        assert forecast_warning_page.click_nine_day_forecast(timeout=15), "Failed to click 9-Day Forecast"
        assert nine_day_forecast_page.wait_for_page_load(timeout=20), "9-Day Forecast page failed to load"
        
        context["current_page"] = nine_day_forecast_page
    else:
        raise ValueError(f"Unknown page: {page_name}")
    
    logger.info(f"Successfully navigated to {page_name} page")


# --------------------------------------------
# then steps
# --------------------------------------------


@then(parsers.parse('I should see the "{page_name}" page'))
def should_see_page(driver, slide_page, home_page, navigation_drawer_page, nine_day_forecast_page, page_name, context):
    logger.info(f"Verifying {page_name} page is displayed")
    
    if page_name == "Slide":
        assert slide_page.is_slide_page_displayed(timeout=15), f"{page_name} page is not displayed"
        context["current_page"] = slide_page

    elif page_name == "Home":
        assert home_page.is_home_page_displayed(timeout=15), f"{page_name} page is not displayed"
        context["current_page"] = home_page

    elif page_name == "Navigation Drawer":
        assert navigation_drawer_page.is_page_displayed(timeout=15), f"{page_name} page is not displayed"
        context["current_page"] = navigation_drawer_page
        
    elif page_name == "9-Day Forecast":
        assert nine_day_forecast_page.is_page_displayed(timeout=15), f"{page_name} page is not displayed"
        context["current_page"] = nine_day_forecast_page
        
    else:
        raise ValueError(f"Unknown page: {page_name}")
    
    logger.info(f"{page_name} page is displayed")


@then(parsers.parse('the page should display "{ord_num}" day\'s forecast information'))
def should_display_forecast_info(driver, nine_day_forecast_page, context):
    logger.info("Verifying forecast information is displayed")
    
    # Get forecast items
    forecast_items = nine_day_forecast_page.get_all_forecast_items()
    
    assert len(forecast_items) > 0, "No forecast items found"
    logger.info(f"Found {len(forecast_items)} forecast items")

    logger.info(nine_day_forecast_page.get_forecast_by_day_offset(9))
    
    context["forecast_items_count"] = len(forecast_items)