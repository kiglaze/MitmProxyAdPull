import sqlite3
import logging
import subprocess
import argparse
import os
import time
import urllib
from urllib.parse import urlparse
from pathlib import Path
import re
import argparse

# DATA GENERATION

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

def sanitize_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)

def get_dumpfile(website):
    sanitized_website = sanitize_filename(website)
    return f"{sanitized_website}.dump"

def get_screenshot_filename(website):
    sanitized_website = sanitize_filename(website)
    return f"{sanitized_website}.png"

def get_video_filename(website):
    sanitized_website = sanitize_filename(website)
    return f"{sanitized_website}.mp4"

# Run mitmdump command to get images from visiting site.
def activate_proxy(website, portNum):
    print('Activating proxy...')
    dumpfile = get_dumpfile(website)
    mitmdump_command = [
        "mitmdump",
        "--listen-port", str(portNum),
        "-w", f"./mitmdumps/{dumpfile}"
    ]
    logger.info(f"Running command: {mitmdump_command}")
    process = subprocess.Popen(mitmdump_command)
    return process
    # TODO (Iris) better to save this somewhere besides /dev/null (not saving). We want the original source file itself. Redirect to specified filename (like website name).
    # TODO (Iris) pass mitmdump output to main.py script. don't insert data into db or make screenshots/recordings until mitmdumps are made from crawler (manager file).
    # once I have the mitmdump file, then I can the replay with something like: mitmdump -nr ./mitmdumps/www.dictionary.com -s main.py
    # .venv/bin/mitmdump -nr ./mitmdumps/www.dictionary.com.dump \
    #   -s main.py \
    #   --set my_custom_arg=https://www.dictionary.com/e/all-the-words/

    # mitmdump --listen-port 8082 -w ./mitmdumps/www.dictionary.com.dump
    # curl -x http://127.0.0.1:8082 https://www.dictionary.com/e/all-the-words/ (in other terminal)
    #    Can also try using browser to visit site with proxy settings on. See if this makes images get saved and loaded.
    # in mitmdump terminal, Ctrl+C



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
        # url encode
        encoded_string = urllib.parse.quote(hostname)
        return encoded_string
        #return hostname.replace("www.", "").replace(".", "_")
    except Exception:
        return "invalid"

def visit_webpage(url, conn):
    cursor = conn.cursor()
    hostname = sanitize_hostname(url)
    filename = f"{hostname}.png"
    output_path = os.path.join(filename)

    try:
        print(f"[+] Capturing {url} → {output_path}")
        print(f"[*] Running command: node browser_client_interface/visit_webpage.js {url}")
        logger.info(f"Running command: node browser_client_interface/visit_webpage.js {url}")
        screenshot_filename = os.path.join("browser_client_interface", "screenshots", get_screenshot_filename(url))
        video_filename = os.path.join("browser_client_interface", "recordings", get_video_filename(url))
        cursor.execute('''
            INSERT OR IGNORE INTO websites_visited (website_url, mitmdump_filepath, screenshot_filepath, video_filepath)
            VALUES (?, ?, ?, ?)
        ''', (url, get_dumpfile(url), screenshot_filename, video_filename))
        start_time = time.time()  # Record the start time
        process = subprocess.Popen(["node", "browser_client_interface/visit_webpage.js", url, screenshot_filename, video_filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Waits for process to finish
        out, err = process.communicate()
        end_time = time.time()  # Record the end time
        duration = end_time - start_time  # Calculate the duration
        logger.info(f"Node process for URL {url} completed in: {duration:.2f} seconds")
        print(out)
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to capture {url}: {e}")
        logger.error(f"[!] Node process failed to capture {url}: {e}")
    finally:
        conn.commit()


def table_setup(conn):
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
        screenshot_filepath TEXT DEFAULT NULL,
        video_filepath TEXT DEFAULT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
    )
    ''')

    conn.commit()


def get_dumps(conn):
    cursor = conn.cursor()

    PORT_NUM = 8082
    #with open(args.input, "r") as f:

    with open("urls_short.txt", "r") as f:
        urls = []
        for line in f:
            url = line.strip()
            if url and not url.startswith("#"):
                if not (url.startswith("http://") or url.startswith("https://")):
                    url = "http://" + url
                urls.append(url)

    Path("mitmdumps").mkdir(exist_ok=True)

    for url in urls:
        if is_port_active(PORT_NUM):
            # print('deactivating proxy')
            deactivate_proxy(PORT_NUM)
        proxy_process = activate_proxy(url, PORT_NUM)
        time.sleep(5)
        visit_webpage(url, conn)

        # Wait for the process to finish

        time.sleep(3)

        # Deactivate the proxy
        deactivate_proxy(PORT_NUM)

def load_dumps(conn):
    cursor = conn.cursor()
    dumps_dir = Path("./mitmdumps")
    dumps_dir.mkdir(exist_ok=True)

    dump_files = list(dumps_dir.glob("*.dump"))
    print(f"Found {len(dump_files)} dump files.")

    for dump_file in dump_files:
        print(f"Processing dump file: {dump_file}")
        mitmdumpfile = str(dump_file.name)
        cursor.execute('''
            SELECT * FROM websites_visited WHERE mitmdump_filepath = ?
        ''', (mitmdumpfile,))
        row = cursor.fetchone()
        url = row[0]

        try:
            mitmdump_load_command = [
                "mitmdump",
                "-nr", str(dump_file),
                "-s", "main.py",
                "--set", f"my_custom_arg={url}"
            ]
            logger.info(f"Running command: {' '.join(mitmdump_load_command)}")
            subprocess.run(mitmdump_load_command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error processing {dump_file}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Manage website visit dumps")
    parser.add_argument("command", choices=["getdumps", "loaddumps"], nargs="?", default=None, help="Which action to perform")
    args = parser.parse_args()
    conn = sqlite3.connect('extracted_texts.db')
    table_setup(conn)
    if args.command == "getdumps":
        get_dumps(conn)
    elif args.command == "loaddumps":
        load_dumps(conn)
    elif args.command is None:
        get_dumps(conn)
        load_dumps(conn)
    conn.close()

if __name__ == "__main__":
    main()
