# Installation
## In general: 
Node version v18.20.7 \
Python version 3.11.7

## For Mac:
### Homebrew Installation
If you don't have Homebrew installed, install it.

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

### Install ffmpeg for video processing (if needed):
```bash
brew install ffmpeg
```

### Install requirements.txt file
```bash
pip install -r requirements.txt
```

### NPM installations
```bash
npm install
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

### After installations (to avoid sources of possible snags)
Make sure mitmdumps directory exists
Make sure certificate is up to date. If not, reinstall it.
    Commands to check expiration date:
    ```bash
    openssl x509 -in ~/.mitmproxy/mitmproxy-ca-cert.pem -noout -dates -subject
    ```
    ```bash
    security find-certificate -c mitmproxy -p | openssl x509 -noout -dates -subject
    ```
    To reinstall:
        Run mitmdump server:
        ```bash
        mitmdump --listen-port 8082
        ```
        Go to http://mitm.it/
Make sure --user-data-dir referenced in browser_client_interface/visit_webpage.js is correct for your puppeteer user data directory, on your machine.
    