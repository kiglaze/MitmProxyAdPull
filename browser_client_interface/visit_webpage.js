// Example command for URL https://www.livescience.com/:
//    node browser_client_interface/screenshot.js https://www.livescience.com/
//    -- OR --
//    node browser_client_interface/screenshot.js https://www.livescience.com/ /Users/irisglaze/code/thesis/MitmProxyAdPull/browser_client_interface/livescience.png

const FIREFOX_MAC_EXECUTABLE_PATH = "/Applications/Firefox.app/Contents/MacOS/firefox";
const CHROME_MAC_EXECUTABLE_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

const path = require('path');
const fs = require('fs');

// For logging.
const winston = require('winston');

const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());


function createLogger(logFile, logLevel = 'info') {
  /**
   * Create a new logger with a specified log file and log level.
   *
   * Args:
   *   logFile (string): The path to the log file.
   *   logLevel (string): The logging level (default is 'info').
   *
   * Returns:
   *   winston.Logger: Configured logger.
   */
  return winston.createLogger({
    level: logLevel,
    format: winston.format.combine(
      winston.format.timestamp(),
      winston.format.printf(({ timestamp, level, message }) => {
        return `${timestamp} - ${level.toUpperCase()} - ${message}`;
      })
    ),
    transports: [
      new winston.transports.Console(),
      new winston.transports.File({ filename: logFile })
    ]
  });
}

const logger = createLogger('screenshot_logger.log');
logger.info('Logger initialized.');

async function autoScroll(page){
  async function autoScrollDown() {
    await page.evaluate(async () => {
      // Pick the element that actually scrolls; fallback to the document
      const el = (() => {
        const docEl = document.scrollingElement || document.documentElement || document.body;
        const cands = Array.from(document.querySelectorAll('*')).filter(e => {
          try {
            const s = getComputedStyle(e);
            const can = /(auto|scroll)/.test(s.overflowY) || /(auto|scroll)/.test(s.overflow);
            const tall = e.scrollHeight > e.clientHeight + 2;
            const vis = !!(e.offsetWidth || e.offsetHeight || e.getClientRects().length);
            return can && tall && vis;
          } catch { return false; }
        });
        return (cands.sort((a,b)=>b.scrollHeight-a.scrollHeight)[0]) || docEl;
      })();

      const tickMs = 50;
      const maxMs = 40000;      // hard cap so we don't scroll forever
      const idleMs = 2000;      // stop if no new content appears for this long
      const step = Math.max(100, Math.floor(el.clientHeight * 0.8));

      let lastH = el.scrollHeight;
      let lastChange = Date.now();
      const start = Date.now();

      while (true) {
        el.scrollBy(0, step);
        await new Promise(r => setTimeout(r, tickMs));

        const { scrollTop, clientHeight, scrollHeight } = el;
        if (scrollHeight > lastH + 5) { lastH = scrollHeight; lastChange = Date.now(); }

        const nearBottom = scrollTop + clientHeight + step >= scrollHeight;
        const idleTooLong = Date.now() - lastChange >= idleMs;
        const timedOut = Date.now() - start >= maxMs;
        if (timedOut || (nearBottom && idleTooLong)) break;
      }
    });
  }

  async function autoScrollUp() {
    // Scroll back to the top
    await page.evaluate(async () => {
      await new Promise((resolve) => {
        let currentPosition = document.documentElement.scrollTop || document.body.scrollTop;
        const distance = 50;
        const timer = setInterval(() => {
          window.scrollBy(0, -distance);
          currentPosition -= distance;

          if (currentPosition <= 0) {
            clearInterval(timer);
            resolve();
          }
        }, 100);
      });
    });
  }

  await autoScrollDown();
  await autoScrollUp();
}

/*async function autoScroll(page) {
  await page.evaluate(async () => {
    const scrollableElement = document.scrollingElement || document.documentElement || document.body;
    const step = Math.max(200, Math.floor(window.innerHeight * 0.8)); // Scroll step size
    const delay = 50; // Delay between scroll steps in milliseconds
    const maxScrollTime = 15000; // Maximum scroll time in milliseconds
    const startTime = Date.now();

    while (Date.now() - startTime < maxScrollTime) {
      const { scrollTop, scrollHeight, clientHeight } = scrollableElement;
      if (scrollTop + clientHeight >= scrollHeight) break; // Stop if at the bottom
      scrollableElement.scrollBy(0, step);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  });
}*/

(async () => {
  const url = process.argv[2];
  let screenshotPath = process.argv[3];
  let recordingPath = process.argv[4]; // [NEW] optional recording output


  if (!url) {
    console.error("Please provide a URL.");
    process.exit(1);
  }

  if (!screenshotPath || !recordingPath) {
    const hostname = new URL(url).hostname.replace(/^www\./, '');
    if (!screenshotPath) {
      screenshotPath = path.join(__dirname, 'screenshots/', `${hostname}.png`);
      logger.info(`Screenshot path not provided. Using default: ${screenshotPath}`);
    }
    if (!recordingPath) {
      recordingPath = path.join(__dirname, 'recordings/', `${hostname}.mp4`);
      logger.info(`Recording path not provided. Using default: ${recordingPath}`);
    }
  }

  // Create the screenshots directory if it doesn't exist
  const screenshotsDir = path.join(__dirname, 'screenshots/');
  if (!fs.existsSync(screenshotsDir)) {
    fs.mkdirSync(screenshotsDir, { recursive: true });
    console.log(`Created directory: ${screenshotsDir}`);
  }
  // Create the recordings directory if it doesn't exist
  const recordingsDir = path.join(__dirname, 'recordings/');
    if (!fs.existsSync(recordingsDir)) {
    fs.mkdirSync(recordingsDir, { recursive: true });
    console.log(`Created directory: ${recordingsDir}`);
  }

  console.log(`URL: ${url}`);
  args = ['--disable-web-security',
    '--disable-application-cache',
    '--media-cache-size=1',
    '--disk-cache-size=1',
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-notifications',
    '--no-first-run',  // Disable first run check
    '--no-default-browser-check',  // Disable default browser check
    `--proxy-server=https=127.0.0.1:8082`,
    '--ignore-certificate-errors',
    '--ignore-certificate-errors-spki-list',
    '--user-data-dir=/Users/irisglaze/puppeteer-profile'
  ]

  const browser = await puppeteer.launch({
    headless: 'new',
    args: args,
    executablePath: CHROME_MAC_EXECUTABLE_PATH,
    timeout: 120000,
  });

  const page = await browser.newPage();

/*  page.on('request', req => {
    if (req.resourceType() === 'image') {
      console.log(`[IMG REQ] ${req.url()}`);
    }
  });*/

  await page.setViewport({ width: 1366, height: 768 });
  console.log(`Visiting page in browser with Puppeteer...`);
  // [NEW] Start screencast before navigation so we capture everything, including page load
  let recorder = null;
  try {
    recorder = await page.screencast({ path: recordingPath, fps: 30 }); // requires ffmpeg
    console.log(`Recording to: ${recordingPath}`);
    logger.info(`Recording to: ${recordingPath}`);
  } catch (e) {
    console.warn(`Failed to start screencast (will continue without video): ${e.message}`);
    logger.warn(`Failed to start screencast (will continue without video): ${e.message}`);
  }
  try {
    await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36');
    try {
      await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
    } finally {
      // Added timeout to allow dynamic content to load
      await new Promise(resolve => setTimeout(resolve, 5000));
    }
    console.log("Auto scrolling...");
    await autoScroll(page);
    console.log("Done auto scrolling...");
    // Wait for all images to load
    await page.evaluate(async () => {
      const imgs = Array.from(document.images);
      const loadImage = (img) => {
        return new Promise((resolve) => {
          if (img.complete) {
            resolve();
          } else {
            const timeout = setTimeout(() => resolve(), 5000); // 5 seconds timeout
            img.onload = img.onerror = () => {
              clearTimeout(timeout);
              resolve();
            };
          }
        });
      };
      await Promise.all(imgs.map(loadImage));
    });

  } catch (err) {
    console.error(`Error occurred: ${err.message}`);
    logger.error(`Error occurred: ${err.message}`);
  } finally {

    console.log("Taking screenshot...");
    logger.info('Taking screenshot...');
    await page.screenshot({ path: screenshotPath, fullPage: true });

    // [NEW] Always stop the recorder if it started
    if (recorder && typeof recorder.stop === 'function') {
      try {
        await recorder.stop();
        console.log("Stopped recording.");
      } catch (e) {
        console.warn(`Failed to stop recording cleanly: ${e.message}`);
      }
    }

    await browser.close();
  }
})();
