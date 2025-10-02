# Run: mitmdump -s main.py --listen-port 8082
# mitm option -d to dump images. save entire session into dump file. iterate through all requests.
# save image somewhere
# puppeteer, similar to selinium
#   use to take care of scrolling to take full page screenshots
#   r option for replay, to replay the session that you had saved
import sqlite3
import sys

# 2 sets: text of all the images (n images), from n images, 2 datasets: raw image, and text from images using the python library
# pass raw image to LLM, is this an ad. is this text related to the ad.

# on load event, then take screenshot

# compare passing the image to passing the text to the LLM to detect if is an ad
# do this for a couple of web pages
# ###########################################
# need to test for multiple non-ad images. safe screenshots of webpage.
# need to validate for negative cases, i.e. images that are not ads.

# DATA PARSING

from mitmproxy import http, ctx
import os
import mimetypes
import urllib.parse
import re
import logging

from urllib.parse import urlparse

# Directory to save images
SAVE_DIR = "saved_images"

# Ensure the save directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

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

logger.info(f"Arguments received: {sys.argv}")
print(f"Arguments received: {sys.argv}")

conn = sqlite3.connect('extracted_texts.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS image_saved_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    full_filepath TEXT NOT NULL UNIQUE,
    source_url TEXT NOT NULL,
    source_url_rating INTEGER DEFAULT NULL,
    referrer_url TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (referrer_url) REFERENCES websites_visited(website_url)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS websites_visited (
    website_url TEXT PRIMARY KEY,
    mitmdump_filepath TEXT NOT NULL UNIQUE,
    website_html_mitmdump_filepath TEXT DEFAULT NULL,
    website_context_description TEXT DEFAULT NULL,
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
image_logger = create_logger("image_saving.log")
content_type_logger = create_logger("content_type.log")

def sanitize_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)

# TODO: Do "coverage analysis" to make sure all images are being captured. Separate mitm log.
def save_image(flow: http.HTTPFlow, filepath_directory, referrer_url, content_type: str):
    """
    Save image content from the HTTP response.
    """
    # Get the file extension based on content-type
    ext = mimetypes.guess_extension(content_type.split(";")[0]) or ".bin"

    # Create a filename based on URL
    parsed_url = urllib.parse.urlparse(flow.request.url)
    filename = f"{parsed_url.netloc}_{os.path.basename(parsed_url.path)}{ext}"
    filename = filename.replace("/", "_")  # Avoid slashes in filenames
    filepath = os.path.join(filepath_directory, filename)

    # Save the image
    with open(filepath, "wb") as f:
        f.write(flow.response.content)
    # Insert the row into the image_saved_data table
    source_url = flow.request.url if hasattr(flow, "request") and flow.request else ''
    cursor.execute('''
        INSERT INTO image_saved_data (filename, full_filepath, source_url, referrer_url)
        VALUES (?, ?, ?, ?)
    ''', (filename, filepath, source_url, referrer_url))

    image_logger.info(f"Saved image: {filepath}")

def response(flow: http.HTTPFlow):
    custom_value = ctx.options.my_custom_arg
    print(f"[REQUEST] {flow.request.pretty_url}")
    url = flow.request.url
    # print(">>>>>>>\n>>>>>>>>\n")
    # print(">>> ", flow.request.method, url)
    #referrer_url = flow.request.headers.get("Referer", None)
    referrer_url = custom_value
    filepath_directory = None
    if referrer_url is not None:
        sanitized_referrer = sanitize_filename(referrer_url)
        filepath_directory = os.path.join(SAVE_DIR, sanitized_referrer)
        os.makedirs(filepath_directory, exist_ok=True)
        if url == custom_value and flow.request.method == "GET":
            print(f"Matched response for URL: {flow.request.url}")
            logger.info(f"Matched response for URL: {flow.request.url}")
            content_type = flow.response.headers.get("content-type", "")
            if content_type.startswith("text/html"):
                print(flow.response.text)
                logger.info(f"Matched response for HTML: {flow.response.text}")
                html_dir = "html_mitmdumps"
                os.makedirs(html_dir, exist_ok=True)
                html_mitmdump_filename = f"{sanitized_referrer}.html"
                html_mitmdump_filepath = os.path.join(html_dir, html_mitmdump_filename)
                with open(html_mitmdump_filepath, "w", encoding="utf-8") as f:
                    f.write(flow.response.text)
                    cursor.execute('''
                        UPDATE websites_visited SET website_html_mitmdump_filepath = ? WHERE website_url = ?
                    ''', (html_mitmdump_filename, url))
    else:
        filepath_directory = os.path.join(SAVE_DIR, "no_referrer")
        os.makedirs(filepath_directory, exist_ok=True)

    """ 
    Intercept HTTP responses and save images.
    """
    content_type = flow.response.headers.get("content-type", "")

    content_type_logger.info(content_type)

    # Check if the response is an image
    if content_type.startswith("image/"):
        print(">>>>>>>\n>>>>>>>>\n")
        save_image(flow, filepath_directory, referrer_url, content_type)


        # Commit the changes to the database
        conn.commit()

def load(loader):
    loader.add_option(
        name = "my_custom_arg",
        typespec = str,
        default = "default_value",
        help = "A custom argument passed to mitmdump"
    )




