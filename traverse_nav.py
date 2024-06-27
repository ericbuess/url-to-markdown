from download_worker import queue_file_lock
from web_driver import initialize_web_driver
from utils import is_valid_url, save_queue_to_file, load_queue_from_file, alert_sound, file_exists_for_url
from config import CHROME_WEB_DRIVER_PATH, QUEUE_FILE
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import sys
import signal
import time
import json
from queue import Queue


def signal_handler(sig, frame):
    sys.exit(0)


def append_to_queue(url):
    with queue_file_lock:
        queue = load_queue_from_file()
        if url not in queue and not file_exists_for_url(url):
            queue.append(url)
            save_queue_to_file(queue)
            print(f"Added {url} to queue")
        elif file_exists_for_url(url):
            print(f"Skipped {url} - file already exists")


def wait_for_nav_elements(driver, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//ul[@role='tree']//a"))
        )
    except TimeoutException:
        print("Timed out waiting for nav elements to load")
        return False
    return True


def click_and_append(link, driver):
    initial_url = driver.current_url
    try:
        href = link.get_attribute("href")
        if href and is_valid_url(href):
            if href == initial_url:
                return

            print(f"Navigating to {href}")
            link.click()
            if wait_for_nav_elements(driver):
                current_url = driver.current_url
                append_to_queue(current_url)
                return current_url
    except StaleElementReferenceException:
        return None
    except WebDriverException as e:
        print(f"WebDriverException: {e}")
        return None
    return initial_url


def get_next_link_index(current_index, links):
    for i, link in enumerate(links):
        try:
            parent_li = link.find_element(By.XPATH, "./..")
            data_index = parent_li.get_attribute("data-index")
            if data_index is not None:
                try:
                    data_index = int(data_index)
                    if data_index > current_index:
                        return i, data_index
                except ValueError:
                    continue
        except StaleElementReferenceException:
            return None, None
    return None, None


def find_active_link(driver):
    try:
        active_link = driver.find_element(
            By.XPATH, "//li[contains(@class, 'active')]/a")
        return active_link
    except WebDriverException:
        return None


def traverse_links(driver):
    initial_url = driver.current_url

    active_link = find_active_link(driver)
    if active_link:
        click_and_append(active_link, driver)
        initial_url = driver.current_url

    current_index = int(active_link.find_element(
        By.XPATH, "./..").get_attribute("data-index")) if active_link else -1

    while True:
        if not wait_for_nav_elements(driver):
            print("Nav elements not found, retrying...")
            continue

        links = driver.find_elements(By.XPATH, "//ul[@role='tree']//a")
        link_index, next_index = get_next_link_index(current_index, links)
        if link_index is None:
            break

        current_index = next_index
        link = links[link_index]

        new_url = click_and_append(link, driver)
        if new_url is None or new_url == initial_url:
            continue

        initial_url = new_url

        sub_links = driver.find_elements(
            By.XPATH, f"//ul[@role='tree']//li[@data-index='{current_index}']//ul[@role='group']//a")
        for sub_link in sub_links:
            sub_url = click_and_append(sub_link, driver)
            if sub_url is None or sub_url == initial_url:
                continue

            initial_url = sub_url


def main():
    signal.signal(signal.SIGINT, signal_handler)

    queue = Queue()
    file_queue = load_queue_from_file()
    file_queue = [url for url in file_queue if is_valid_url(url)]
    save_queue_to_file(file_queue)

    driver = initialize_web_driver(queue)
    try:
        traverse_links(driver)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
