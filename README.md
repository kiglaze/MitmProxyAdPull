# 
## Mitm Proxy Ad Pull -- Running the Program
If preliminary step were already completed, just run:
```
mitmdump -s main.py --listen-port 8082
```
... and visit the target website in your browser.
Also, if you have already trusted the certificate for mitmproxy (see preliminary steps), the proxy will be configured by the code in screenshot.js automatically.
In this case, you can skip the manual proxy configuration in your browser, or unset it if it's set.


## Preliminary steps (if you are new):

### Mitmproxy Installation and Setup
1. Install mitmproxy.
   - If on a Mac, you can use Homebrew:
       ```
       brew install mitmproxy
       ```
2. Run the mitmproxy server:
   ```
   mitmdump -s main.py --listen-port 8082
   ```
   This command starts the mitmproxy server and listens on port 8082.
3. The code uses the mitmproxy server with 127.0.0.1 (localhost) and port 8082.
   - Set your browser's proxy settings to use `127.0.0.1` and port `8082`.
     - In Firefox, go to Preferences > Network Settings > Manual proxy configuration and enter `127.0.0.1` for HTTP Proxy and `8082` for Port.
   - On a Mac for Chrome, you must go to System Settings > Network > Details button for your WiFi connection > Proxies tab
     - Check Web proxy (HTTP) and Secure web proxy (HTTPS), then configure for `127.0.0.1` and port `8082`
4. Install mitmproxy's CA certificate in your browser and make it trusted:
   - Open `http://mitm.it` in your browser.
   - Follow the instructions to install the CA certificate for your operating system and browser.
   - Make sure to trust the certificate in your computer's settings. Do this via Keychain Access (at least if using a Mac)
5. Restart your browser to apply the changes.

### Tesseract for text extraction from images:
```bash
brew install tesseract
```

### Puppeteer User Data Directory Setup
Set up the user data directory (example is for Mac, and the "puppeteer-profile" directory is created in the home directory, in this case):
```bash
mkdir -p /Users/irisglaze/puppeteer-profile
```
Launch Chrome manually once with the user data directory:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --user-data-dir="/Users/irisglaze/puppeteer-profile"
```

------------------
## Notes to Self: ...
puppeteer (or selenium)
- use to control which url's are visited. this will allow us to programmatically know what site an image is coming from.
- can also be part of main.py
- take screenshot of page before marking ad vs. not ad image process
  - script in slack

one column with llm detection, one column with manual ad detection
doesn't matter where the ad is from for now

ignore blank text for now

repo ad

each person do half of manual image checks for now

--------------
Sites to check are in ./urls.txt

Example command for URL https://www.livescience.com/:
```bash
    node browser_client_interface/screenshot.js https://www.livescience.com/
```
OR
```bash
    node browser_client_interface/screenshot.js https://www.livescience.com/ /Users/irisglaze/code/thesis/MitmProxyAdPull/browser_client_interface/livescience.png
```
--------------
notes from April 3, 2025:

script:
for loop for urls
mitmdump command called, with -o option to output to file
a few second wait - don't need record the wait time, using while loop
unix command to see if mitm proxy is running
node command with puppeteer
look at the script:
https://github.com/ahsan238/Ad-Compliance/blob/main/src/server.py
def activateProxy(website, portNum):
def isPortActive(instance_port):
after node process is run, disconnect mitmdump process (one connection = 1 website url of focus)
