# README
## For installation instructions:
see INSTALLATION_INSTRUCTIONS.md file
## Order to run the program:
- website_visits_recording_manager.py
- check_image_text.py
- llm_interface/api_calls.py
- llm_interface/api_calls_context.py
## Mitm Proxy Ad Pull -- Running the Program
### Intercept with mitmdump
If preliminary step were already completed, just run:
```
mitmdump -s main.py --listen-port 8082 --set my_custom_arg="<directory_name_for_saved_image_output>"
```
where `<directory_name_for_saved_image_output>` is the directory where you want to save the images (under saved_images).

... and visit the target website by using the Node JS script command listed below.
Also, if you have already trusted the certificate for mitmproxy (see preliminary steps), the proxy will be configured by the code in visit_webpage.js automatically.

### Automate the browser and take a screenshot
This Node command automatically opens the browser and takes a screenshot of the page at the specified URL. The screenshot is saved in the specified directory.
```bash
    node browser_client_interface/visit_webpage.js https://www.livescience.com/
```
OR
```bash
    node browser_client_interface/visit_webpage.js https://www.livescience.com/ /Users/irisglaze/code/thesis/MitmProxyAdPull/browser_client_interface/livescience.png
```

### BOTH of previous two steps for multiple URLs (mitmdump and screenshot-taking Node command)
website_visits_recording_manager.py

Sites to check are in listed in ./urls.txt

### Onces images are saved, extract the text from the images.
check_image_text.py

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
-----

do urls have text or not text if I visit them live? count with words vs without words
test 25-50 total urls manually

also can see if my words pytesseract script extracts text from the Disney image (img.3lift.com_.webp from accuweather)
