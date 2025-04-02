// screenshot.js
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

  const browser = await puppeteer.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--ignore-certificate-errors',
      '--proxy-server=http=127.0.0.1:8082',
    ],
    executablePath: CHROME_MAC_EXECUTABLE_PATH,
    timeout: 0,
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1366, height: 768 });

  try {
    await page.goto(url, { waitUntil: 'networkidle0', timeout: 120000 });
    await page.screenshot({ path: screenshotPath, fullPage: true });
  } catch (err) {
    console.error(`Failed to take screenshot of ${url}:`, err);
  } finally {
    await browser.close();
  }
})();
