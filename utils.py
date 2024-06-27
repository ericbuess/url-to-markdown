import requests
from urllib.parse import urlparse, urljoin
import json
import os
import logging
from config import DATA_DIR, QUEUE_FILE

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class PaymentRequiredError(Exception):
    """Exception raised for 402 Payment Required errors."""
    pass


def is_valid_url(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme in ["http", "https"] and not url.startswith("chrome://")


def normalize_url(url):
    if url.startswith("https://"):
        return url[8:]  # Remove 'https://'
    elif url.startswith("http://"):
        return url[7:]  # Remove 'http://'
    return url


def download_url_content(url, jina_api_key=None):
    normalized_url = normalize_url(url)
    full_url = 'https://r.jina.ai/' + normalized_url
    logging.info(f"Downloading content from: {full_url}")

    headers = {
        "Accept": "text/event-stream",
        "X-With-Generated-Alt": "true"
    }
    if jina_api_key:
        headers["Authorization"] = f"Bearer {jina_api_key}"

    try:
        response = requests.get(full_url, headers=headers)
        if response.status_code == 200:
            first_line = response.text.split('\n', 1)[0]
            if first_line.startswith("event: data"):
                return response.text
            else:
                raise ValueError(
                    "Downloaded content is not in the expected markdown format")
        elif response.status_code == 402:
            raise PaymentRequiredError("402 Payment Required")
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading content: {str(e)}")
        raise e


def save_content_to_file(url, content):
    filename = f"{urlparse(url).netloc}{
        urlparse(url).path.replace('/', '_')}.md"
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w") as file:
        file.write(content)
    logging.info(f"Content saved to: {filepath}")


def file_exists_for_url(url):
    filename = f"{urlparse(url).netloc}{
        urlparse(url).path.replace('/', '_')}.md"
    filepath = os.path.join(DATA_DIR, filename)
    return os.path.exists(filepath)


def alert_sound():
    logging.warning("Download failed")


def save_queue_to_file(queue_items):
    with open(QUEUE_FILE, 'w') as file:
        json.dump(queue_items, file)
    logging.info(f"Queue saved to file: {QUEUE_FILE}")


def load_queue_from_file():
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'r') as file:
            queue_items = json.load(file)
        logging.info(f"Queue loaded from file: {QUEUE_FILE}")
        return queue_items
    return []
