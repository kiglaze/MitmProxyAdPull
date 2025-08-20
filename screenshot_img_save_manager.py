import logging
import subprocess
import argparse
import os
import time
from urllib.parse import urlparse
from pathlib import Path

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

# Create logs.
logger = create_logger("website_visit_manager_logger.log")

# Run mitmdump command to get images from visiting site.
def activate_proxy(website, portNum):
    print('Activating proxy...')
    sanitized_website = sanitize_hostname(website)
    logger.info(f"Running command: mitmdump -s main.py --listen-port {portNum} --set my_custom_arg={sanitized_website} > /dev/null &")
    os.system(
        f"mitmdump -s main.py --listen-port {portNum} --set my_custom_arg={sanitized_website} > /dev/null &")


def deactivate_proxy(instance_port):
    print('De-activating proxy...')
    logger.info(f"Running command: kill -9 $(lsof -ti:{''}) ..... for port {instance_port}")
    r = subprocess.Popen("kill -9 $(lsof -ti:{})".format(instance_port), shell =True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = r.communicate()

def is_port_active(instance_port):
    r = subprocess.Popen(f"ss -plnt | grep {instance_port}".format(instance_port), shell =True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = r.communicate()
    for l in out.splitlines():
        if str(instance_port) in l.decode():
            # print('Port is active')
            return True
    return False

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
        print(f"[*] Running command: node browser_client_interface/screenshot.js {url}")
        logger.info(f"Running command: node browser_client_interface/screenshot.js {url}")
        start_time = time.time()  # Record the start time
        process = subprocess.Popen(["node", "browser_client_interface/screenshot.js", url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        end_time = time.time()  # Record the end time
        duration = end_time - start_time  # Calculate the duration
        logger.info(f"Node process for URL {url} completed in: {duration:.2f} seconds")
        print(out)
        process.wait()
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to capture {url}: {e}")
        logger.error(f"[!] Node process failed to capture {url}: {e}")

def main():
    PORT_NUM = 8082
    #with open(args.input, "r") as f:
    with open("urls_short.txt", "r") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    command = "node"
    script_path = "browser_client_interface/screenshot.js"
    for url in urls:
        if is_port_active(PORT_NUM):
            # print('deactivating proxy')
            deactivate_proxy(PORT_NUM)
        activate_proxy(url, PORT_NUM)
        time.sleep(5)
        take_screenshot(url)

        # Wait for the process to finish

        time.sleep(3)

        # Deactivate the proxy
        deactivate_proxy(PORT_NUM)

if __name__ == "__main__":
    main()
