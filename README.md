# 
## Mitm Proxy Ad Pull -- Running the Program
If preliminary step were already completed, just run:
```
mitmdump -s main.py --listen-port 8082
```
... and visit the target website in your browser.


Preliminary steps:
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
3. Configure your browser to use the mitmproxy server:
   - Set your browser's proxy settings to use `127.0.0.1` and port `8082`.
     - In Firefox, go to Preferences > Network Settings > Manual proxy configuration and enter `127.0.0.1` for HTTP Proxy and `8082` for Port.
4. Install mitmproxy's CA certificate in your browser and make it trusted:
   - Open `http://mitm.it` in your browser.
   - Follow the instructions to install the CA certificate for your operating system and browser.
   - Make sure to trust the certificate in your computer's settings. (at least if using a Mac)
5. Restart your browser to apply the changes.



----------

```bash
brew install tesseract
```
