import subprocess
import argparse
import os
import time
from urllib.parse import urlparse
from pathlib import Path


def activate_proxy(website, portNum):
    print('Activating proxy...')
    sanitized_website = sanitize_hostname(website)
    os.system(
        f"mitmdump -s main.py --listen-port {portNum} --set my_custom_arg={sanitized_website} > /dev/null &")

def deactivate_proxy(instance_port):
    print('De-activating proxy...')
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
        process = subprocess.Popen(["node", "browser_client_interface/screenshot.js", url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        print(out)
        process.wait()
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to capture {url}: {e}")

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
