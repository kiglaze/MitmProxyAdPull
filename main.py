# Run: mitmdump -s main.py --listen-port 8082
# mitm option -d to dump images. save entire session into dump file. iterate through all requests.
# save image somewhere
# puppeteer, similar to selinium
#   use to take care of scrolling to take full page screenshots
#   r option for replay, to replay the session that you had saved

# 2 sets: text of all the images (n images), from n images, 2 datasets: raw image, and text from images using the python library
# pass raw image to LLM, is this an ad. is this text related to the ad.

# on load event, then take screenshot

# compare passing the image to passing the text to the LLM to detect if is an ad
# do this for a couple of web pages
# ###########################################
# need to test for multiple non-ad images. safe screenshots of webpage.
# need to validate for negative cases, i.e. images that are not ads.

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

def response(flow: http.HTTPFlow):
    custom_value = ctx.options.my_custom_arg
    print(f"[REQUEST] {flow.request.pretty_url}")
    url = flow.request.url
    #print(">>> ", flow.request.method, url)
    #referrer_url = flow.request.headers.get("Referer", None)
    referrer_url = custom_value
    if referrer_url is not None:
        sanitized_referrer = sanitize_filename(referrer_url)
        os.makedirs(os.path.join(SAVE_DIR, sanitized_referrer), exist_ok=True)
    else:
        os.makedirs(SAVE_DIR + "/" + "no_referrer/", exist_ok=True)

    """ 
    Intercept HTTP responses and save images.
    """
    content_type = flow.response.headers.get("content-type", "")

    content_type_logger.info(content_type)

    # Check if the response is an image
    if content_type.startswith("image/"):
        save_image(flow, referrer_url, content_type)

def load(loader):
    loader.add_option(
        name = "my_custom_arg",
        typespec = str,
        default = "default_value",
        help = "A custom argument passed to mitmdump"
    )

def save_image(flow: http.HTTPFlow, referrer, content_type: str):
    """
    Save image content from the HTTP response.
    """
    # Get the file extension based on content-type
    ext = mimetypes.guess_extension(content_type.split(";")[0]) or ".bin"

    # Create a filename based on URL
    parsed_url = urllib.parse.urlparse(flow.request.url)
    filename = f"{parsed_url.netloc}_{os.path.basename(parsed_url.path)}{ext}"
    filename = filename.replace("/", "_")  # Avoid slashes in filenames
    if referrer is not None:
        filepath = os.path.join(SAVE_DIR, sanitize_filename(referrer), filename)
    else:
        filepath = os.path.join(SAVE_DIR, "no_referrer", filename)

    # Save the image
    with open(filepath, "wb") as f:
        f.write(flow.response.content)
    image_logger.info(f"Saved image: {filepath}")


