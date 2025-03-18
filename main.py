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


from mitmproxy import http
import os
import mimetypes
import urllib.parse
import re

# Directory to save images
SAVE_DIR = "saved_images"
IFRAME_FILE = "saved_iframes.txt"

# Ensure the save directory exists
os.makedirs(SAVE_DIR, exist_ok=True)


def response(flow: http.HTTPFlow):
    """
    Intercept HTTP responses and save images.
    """
    content_type = flow.response.headers.get("content-type", "")

    # Check if the response is an image
    if content_type.startswith("image/"):
        save_image(flow, content_type)

    # Extract iframe sources from HTML pages
    elif "text/html" in content_type:
        save_iframe_sources(flow)

def save_image(flow: http.HTTPFlow, content_type: str):
    """
    Save image content from the HTTP response.
    """
    # Get the file extension based on content-type
    ext = mimetypes.guess_extension(content_type.split(";")[0]) or ".bin"

    # Create a filename based on URL
    parsed_url = urllib.parse.urlparse(flow.request.url)
    filename = f"{parsed_url.netloc}_{os.path.basename(parsed_url.path)}{ext}"
    filename = filename.replace("/", "_")  # Avoid slashes in filenames
    filepath = os.path.join(SAVE_DIR, filename)

    # Save the image
    with open(filepath, "wb") as f:
        f.write(flow.response.content)

    print(f"Saved image: {filepath}")


def save_iframe_sources(flow: http.HTTPFlow):
    """
    Extracts and saves iframe sources from HTML responses.
    """
    html_content = flow.response.text

    # Find all iframe sources using regex
    iframe_srcs = re.findall(r'<iframe[^>]+src="([^"]+)"', html_content)

    if iframe_srcs:
        with open(IFRAME_FILE, "a") as f:
            for src in iframe_srcs:
                f.write(src + "\n")

        print(f"✅ Saved {len(iframe_srcs)} iframe URLs to {IFRAME_FILE}")
