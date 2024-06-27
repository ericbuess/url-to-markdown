from selenium.webdriver.support.events import AbstractEventListener
from utils import is_valid_url, file_exists_for_url, load_queue_from_file, save_queue_to_file
from download_worker import queue_file_lock


class UrlChangeListener(AbstractEventListener):
    def __init__(self, queue):
        self.queue = queue
        print("UrlChangeListener initialized")

    def before_navigate_to(self, url, driver):
        if not is_valid_url(url):
            print(f"Ignoring irrelevant URL: {url}")
            return
        print(f"before_navigate_to triggered with URL: {url}")
        if not file_exists_for_url(url):
            with queue_file_lock:
                queue_items = load_queue_from_file()
                if url not in queue_items:
                    queue_items.append(url)
                    save_queue_to_file(queue_items)
                    self.queue.put(url)
            print(f"Detected URL: {url}")
            with open('url_listener.log', 'a') as log_file:
                log_file.write(f"Detected URL: {url}\n")
        driver.execute_script("window.close();")

    def after_navigate_to(self, url, driver):
        # No action needed in this method for the current requirements
        pass
