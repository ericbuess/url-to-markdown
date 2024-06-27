import time
from queue import Queue, Empty
from threading import Thread, Lock
from config import JINA_API_KEY, POLL_INTERVAL, DATA_DIR, QUEUE_FILE
from utils import download_url_content, save_content_to_file, file_exists_for_url, alert_sound, save_queue_to_file, load_queue_from_file, PaymentRequiredError, is_valid_url

queue_file_lock = Lock()


def process_url(url):
    if file_exists_for_url(url):
        print(f"{url} already exists.")
        return True

    try:
        print(f"Attempting to download: {url}")
        md_content = download_url_content(url, JINA_API_KEY)
        time.sleep(2)  # Introduce a delay to ensure download completes
        if not md_content.startswith("event: data"):
            print(f"Downloaded the wrong file type for {
                  url}. Content does not start with 'event: data'.")
            alert_sound()
            return False
        else:
            save_content_to_file(url, md_content)
            print(f"{url} downloaded successfully.")
            return True
    except PaymentRequiredError as e:
        print(f"Failed to download content from {url}: {e}")
        print("Add JIRA API credits or generate a new API Key.")
        return False
    except Exception as e:
        print(f"Failed to download content from {url}: {e}")
        alert_sound()
        return False


def download_worker(queue):
    while True:
        try:
            url = queue.get(timeout=POLL_INTERVAL)
            if process_url(url):
                with queue_file_lock:
                    queue_items = load_queue_from_file()
                    if url in queue_items:
                        queue_items.remove(url)
                        save_queue_to_file(queue_items)
                    else:
                        print(f"URL {
                              url} not found in queue file. It may have been removed by another process.")
            queue.task_done()
        except Empty:
            continue  # If queue is empty, continue the loop


def start_download_worker(queue):
    worker_thread = Thread(target=download_worker, args=(queue,))
    worker_thread.daemon = True
    worker_thread.start()
    return worker_thread
