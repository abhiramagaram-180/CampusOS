const { chromium } = require('playwright');

(async () => {
 const browser = await chromium.launch({ headless: true });
 const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });

 const logs = [];
 page.on('console', msg => logs.push(msg.type() + ': ' + msg.text()));

 await page.goto('http://localhost:3000', { waitUntil: 'networkidle', timeout: 30000 });

 // Wait for loading screen to disappear
 await page.waitForSelector('#loading.hidden', { timeout: 5000 }).catch(() => {});
 await page.waitForTimeout;

 console.log('=== ALL CONSOLE LOGS ===');
 logs.forEach(l => console.log(l));
 console.log('=== TOTAL:', logs.length, '===');

 await page.screenshot({ path: 'E:/campus2/game-screenshot2.png', fullPage: false });
 console.log('Screenshot saved');
 await browser.close();
})();
