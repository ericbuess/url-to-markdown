import json
import threading
import time
from collections import deque
from config import QUEUE_FILE
import logging


class QueueManager:
    def __init__(self, save_interval=60):
        self.queue = deque()
        self.url_set = set()
        self.lock = threading.Lock()
        self.save_interval = save_interval
        self.last_save_time = time.time()
        self.load_from_file()

    def load_from_file(self):
        try:
            with open(QUEUE_FILE, 'r') as file:
                urls = json.load(file)
                with self.lock:
                    self.queue = deque(urls)
                    self.url_set = set(urls)
            logging.info(f"Queue loaded from file: {QUEUE_FILE}")
        except FileNotFoundError:
            logging.warning(f"Queue file not found: {QUEUE_FILE}")
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from queue file: {QUEUE_FILE}")

    def save_to_file(self):
        with self.lock:
            urls = list(self.queue)
        with open(QUEUE_FILE, 'w') as file:
            json.dump(urls, file)
        logging.info(f"Queue saved to file: {QUEUE_FILE}")
        self.last_save_time = time.time()

    def add(self, url):
        with self.lock:
            if url not in self.url_set:
                self.queue.append(url)
                self.url_set.add(url)
                logging.info(f"Added URL to queue: {url}")
        self.check_save()

    def get(self):
        with self.lock:
            if self.queue:
                url = self.queue.popleft()
                self.url_set.remove(url)
                logging.info(f"Retrieved URL from queue: {url}")
                return url
        return None

    def remove(self, url):
        with self.lock:
            try:
                self.queue.remove(url)
                self.url_set.remove(url)
                logging.info(f"Removed URL from queue: {url}")
            except ValueError:
                logging.warning(
                    f"Attempted to remove non-existent URL from queue: {url}")
        self.check_save()

    def check_save(self):
        if time.time() - self.last_save_time > self.save_interval:
            self.save_to_file()

    def __len__(self):
        return len(self.queue)

    def __contains__(self, url):
        return url in self.url_set
