const { chromium } = require('playwright');

(async () => {
 const browser = await chromium.launch({ headless: true });
 const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
 await page.goto('http://localhost:3000', { waitUntil: 'networkidle', timeout: 30000 });
 await page.waitForTimeout;
 await page.screenshot({ path: 'E:/campus2/game-screenshot.png', fullPage: false });
 console.log('Screenshot saved');
 await browser.close();
})();
