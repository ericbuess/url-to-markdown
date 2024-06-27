from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.events import EventFiringWebDriver
from config import CHROME_WEB_DRIVER_PATH
from url_listener import UrlChangeListener
from selenium import webdriver
import logging


def initialize_web_driver(queue):
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    service = Service(CHROME_WEB_DRIVER_PATH)

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logging.info("WebDriver initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize WebDriver: {str(e)}")
        raise

    try:
        event_driver = EventFiringWebDriver(driver, UrlChangeListener(queue))
        logging.info("EventFiringWebDriver initialized and wrapping WebDriver")
    except Exception as e:
        logging.error(f"Failed to initialize EventFiringWebDriver: {str(e)}")
        driver.quit()
        raise

    # Verify that WebDriver is attached and responsive
    try:
        current_url = event_driver.current_url
        logging.info(f"Current URL after initialization: {current_url}")
    except Exception as e:
        logging.error(f"Failed to get current URL: {str(e)}")
        event_driver.quit()
        raise

    return event_driver


def reset_web_driver(queue):
    logging.info("Resetting WebDriver...")
    try:
        driver = initialize_web_driver(queue)
        logging.info("WebDriver has been reset successfully")
        return driver
    except Exception as e:
        logging.error(f"Failed to reset WebDriver: {str(e)}")
        raise
