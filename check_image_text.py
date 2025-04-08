import os

from PIL import Image
import pytesseract
import logging
import sqlite3

# Directory containing images
IMAGE_DIR = "./saved_images"

# Ensure the directory exists
if not os.path.exists(IMAGE_DIR):
    raise FileNotFoundError(f"The directory {IMAGE_DIR} does not exist.")

# Configure logging to log to a file
try:
    file_handler = logging.FileHandler("app.log")
except Exception as e:
    print(f"Failed to create file handler: {e}")
    file_handler = None

# Reset any existing log handlers, such as from mitmproxy
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configure logging to log to a file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        file_handler
    ] if file_handler else [logging.StreamHandler()]
)
logger = logging.getLogger(__name__)



conn = sqlite3.connect('extracted_texts.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS image_texts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    text TEXT,
    is_suspected_ad_auto BOOLEAN DEFAULT NULL,
    is_suspected_ad_manual BOOLEAN DEFAULT NULL,
    full_filepath TEXT,
    url_visited_directory TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
)
''')
conn.commit()



def create_logger(log_file, log_level=logging.INFO):
    """
    Create a new logger with a specified log file and log level.

    Args:
        log_file (str): The path to the log file.
        log_level (int): The logging level (default is logging.INFO).

    Returns:
        logging.Logger: Configured logger.
    """
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    logger = logging.getLogger(log_file)
    logger.setLevel(log_level)
    logger.addHandler(file_handler)

    return logger

# Creating logs
image_text_logger = create_logger("image_text_saving.log")


def extract_text_from_image(image_path):
    """
    Extract text from a single image using Tesseract-OCR.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The extracted text.
    """
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"Failed to extract text from {image_path}: {e}")
        return None

def extract_text_from_images(directory):
    """
    Extract text from all images in a directory and its sub-directories.

    Args:
        directory (str): The path to the directory containing images.

    Returns:
        dict: A dictionary with image file names as keys and extracted text as values.
    """
    extracted_texts = {}
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                image_path = os.path.join(root, filename)
                try:
                    image = Image.open(image_path)
                    if image.size == (1, 1):
                        continue  # Skip images of size 1x1
                except Exception as e:
                    print(f"Failed to open image {image_path}: {e}")
                    continue
                text = extract_text_from_image(image_path)
                if text is None or not text.strip():
                    continue  # Skip images with no text found
                url_visited_directory = root.split(IMAGE_DIR)[1].lstrip('/')
                # Insert filename and text into the database
                cursor.execute('INSERT INTO image_texts (filename, text, full_filepath, url_visited_directory) VALUES (?, ?, ?, ?)', (filename, text, image_path, url_visited_directory))
                conn.commit()
                extracted_texts[filename] = text
    return extracted_texts

if __name__ == "__main__":
    texts = extract_text_from_images(IMAGE_DIR)
    for image_file, text in texts.items():
        print(f"Text from {image_file}:\n{text}\n")
        image_text_logger.info(f"Text from {image_file}:\n{text}\n")