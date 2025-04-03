// Example command for URL https://www.livescience.com/:
//    node browser_client_interface/screenshot.js https://www.livescience.com/
//    -- OR --
//    node browser_client_interface/screenshot.js https://www.livescience.com/ /Users/irisglaze/code/thesis/MitmProxyAdPull/browser_client_interface/livescience.png

const FIREFOX_MAC_EXECUTABLE_PATH = "/Applications/Firefox.app/Contents/MacOS/firefox";
const CHROME_MAC_EXECUTABLE_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

const path = require('path');
const fs = require('fs');

const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

async function autoScroll(page){
  await page.evaluate(async () => {
    await new Promise((resolve) => {
      let totalHeight = 0;
      const distance = 500;
      const timer = setInterval(() => {
        const scrollHeight = document.body.scrollHeight;
        window.scrollBy(0, distance);
        totalHeight += distance;

        if (totalHeight >= scrollHeight){
          clearInterval(timer);
          resolve();
        }
      }, 300);
    });
  });
}


(async () => {
  const url = process.argv[2];
  let screenshotPath = process.argv[3];

  if (!url) {
    console.error("Please provide a URL.");
    process.exit(1);
  }

  if (!screenshotPath) {
    const hostname = new URL(url).hostname.replace(/^www\./, '');
    screenshotPath = path.join(__dirname, 'screenshots/', `${hostname}.png`);
  }

  // Create the screenshots directory if it doesn't exist
  const screenshotsDir = path.join(__dirname, 'screenshots/');
  if (!fs.existsSync(screenshotsDir)) {
    fs.mkdirSync(screenshotsDir, { recursive: true });
    console.log(`Created directory: ${screenshotsDir}`);
  }

  console.log(`URL: ${url}`);
  console.log(`Saving screenshot to: ${screenshotPath}`);
  args = ['--disable-web-security',
    '--disable-application-cache',
    '--media-cache-size=1',
    '--disk-cache-size=1',
    '--no-sandbox',
    '--disable-setuid-sandbox',
    `--proxy-server=https=127.0.0.1:8082`,
    '--ignore-certificate-errors',
    '--ignore-certificate-errors-spki-list',
    '--user-data-dir=/Users/irisglaze/puppeteer-profile'
  ]

  const browser = await puppeteer.launch({
    headless: false,
    args: args,
    executablePath: CHROME_MAC_EXECUTABLE_PATH,
    timeout: 0,
  });

  const page = await browser.newPage();

  page.on('request', req => {
    if (req.resourceType() === 'image') {
      console.log(`[IMG REQ] ${req.url()}`);
    }
  });

  await page.setViewport({ width: 1366, height: 768 });

  try {
    await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36');
    await page.goto(url, { waitUntil: 'load', timeout: 180000 });
    // Auto scroll to the bottom of the page
    await autoScroll(page);
    // Wait for all images to load
    await page.evaluate(async () => {
      const imgs = Array.from(document.images);
      await Promise.all(imgs.map(img => {
        if (img.complete) return;
        return new Promise(resolve => {
          img.onload = img.onerror = resolve;
        });
      }));
    });
    await new Promise(resolve => setTimeout(resolve, 5000));

    await page.screenshot({ path: screenshotPath, fullPage: true });
  } catch (err) {
    console.error(`Failed to take screenshot of ${url}:`, err);
  } finally {
    await browser.close();
  }
})();
