import argparse
import time
from threading import Lock
from config import POLL_INTERVAL
from utils import is_valid_url, file_exists_for_url, download_url_content, save_content_to_file
from web_driver import initialize_web_driver, reset_web_driver
from queue_manager import QueueManager
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def queue_only_mode(queue_manager):
    logging.info("Running in queue-only mode")
    while True:
        url = queue_manager.get()
        if url:
            if is_valid_url(url) and not file_exists_for_url(url):
                try:
                    logging.info(f"Attempting to download: {url}")
                    content = download_url_content(url)
                    save_content_to_file(url, content)
                    logging.info(f"{url} downloaded successfully.")
                except Exception as e:
                    logging.error(f"Failed to download {url}: {str(e)}")
                    queue_manager.add(url)  # Add back to queue for retry
            else:
                logging.info(
                    f"Skipping {url} - invalid URL or file already exists.")
        time.sleep(POLL_INTERVAL)


def url_watch_mode(queue_manager):
    logging.info("Running in URL-watch mode")
    driver = initialize_web_driver(queue_manager)
    logging.info("WebDriver initialized and ready")

    try:
        while True:
            try:
                current_windows = driver.window_handles
                for window in current_windows:
                    driver.switch_to.window(window)
                    current_url = driver.current_url
                    if is_valid_url(current_url) and not file_exists_for_url(current_url):
                        queue_manager.add(current_url)
                    driver.execute_script("window.close();")
                time.sleep(POLL_INTERVAL)
            except Exception as e:
                logging.error(f"Error during main loop: {e}")
                driver = reset_web_driver(queue_manager)
    finally:
        driver.quit()


def main():
    parser = argparse.ArgumentParser(description="URL to Markdown Converter")
    parser.add_argument("-w", "--watch", action="store_true",
                        help="Enable URL watch mode")
    args = parser.parse_args()

    queue_manager = QueueManager()

    try:
        if args.watch:
            url_watch_mode(queue_manager)
        else:
            queue_only_mode(queue_manager)
    except KeyboardInterrupt:
        logging.info("Process interrupted by user")
    finally:
        queue_manager.save_to_file()


if __name__ == "__main__":
    main()
