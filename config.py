from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()
JINA_API_KEY = os.getenv('JINA_API_KEY')
CHROME_WEB_DRIVER_PATH = os.getenv('CHROME_WEB_DRIVER_PATH')

DATA_DIR = 'data'
QUEUE_FILE = 'queue.json'
POLL_INTERVAL = 1.0  # Polling interval in seconds

# Ensure the data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
