import subprocess
import argparse
import os
from urllib.parse import urlparse
from pathlib import Path

def sanitize_hostname(url):
    try:
        hostname = urlparse(url).hostname or "unknown"
        return hostname.replace("www.", "").replace(".", "_")
    except Exception:
        return "invalid"

def take_screenshot(url):
    hostname = sanitize_hostname(url)
    filename = f"{hostname}.png"
    output_path = os.path.join(filename)

    try:
        print(f"[+] Capturing {url} → {output_path}")
        subprocess.run([
            "node",
            "browser_client_interface/screenshot.js",
            url
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to capture {url}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Batch run Puppeteer screenshots through mitmproxy.")
    #parser.add_argument("--input", required=True, help="Path to a text file with one URL per line")
    args = parser.parse_args()

    # Make sure the output directory exists
    #Path(args.output).mkdir(parents=True, exist_ok=True)

    #with open(args.input, "r") as f:
    with open("urls.txt", "r") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    for url in urls:
        take_screenshot(url)

if __name__ == "__main__":
    main()
