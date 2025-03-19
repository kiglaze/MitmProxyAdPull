import os
from PIL import Image
import pytesseract
import logging

# Directory containing images
IMAGE_DIR = "./saved_images_testing"

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
        return ""

def extract_text_from_images(directory):
    """
    Extract text from all images in a directory.

    Args:
        directory (str): The path to the directory containing images.

    Returns:
        dict: A dictionary with image file names as keys and extracted text as values.
    """
    extracted_texts = {}
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            image_path = os.path.join(directory, filename)
            text = extract_text_from_image(image_path)
            extracted_texts[filename] = text
    return extracted_texts

if __name__ == "__main__":
    texts = extract_text_from_images(IMAGE_DIR)
    for image_file, text in texts.items():
        print(f"Text from {image_file}:\n{text}\n")
        image_text_logger.info(f"Text from {image_file}:\n{text}\n")