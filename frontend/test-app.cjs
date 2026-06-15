const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    geolocation: { latitude: 12.9716, longitude: 77.5946 },
    permissions: ['geolocation'],
  });
  const page = await context.newPage();
  page.on('console', (msg) => console.log('CONSOLE:', msg.type(), msg.text()));
  page.on('pageerror', (err) => console.log('PAGEERROR:', err.message));

  await page.goto('http://localhost:5173/');
  await page.click('text=Explore');
  await page.waitForTimeout(1500);

  const getTitle = async () => page.locator('h2').first().textContent();
  console.log('Card 1:', await getTitle());

  const card = await page.locator('.cursor-grab').first();
  const box = await card.boundingBox();
  const startX = box.x + box.width / 2;
  const startY = box.y + box.height / 2;
  await page.mouse.move(startX, startY);
  await page.mouse.down();
  for (let i = 1; i <= 20; i++) {
    await page.mouse.move(startX - i * 15, startY, { steps: 2 });
    await page.waitForTimeout(20);
  }
  await page.mouse.up();
  await page.waitForTimeout(1000);
  console.log('Card after left swipe:', await getTitle());
  await page.screenshot({ path: '/tmp/3-after-swipe-left.png' });

  // Swipe right on next top card
  const card2 = await page.locator('.cursor-grab').first();
  const box2 = await card2.boundingBox();
  const sx = box2.x + box2.width / 2;
  const sy = box2.y + box2.height / 2;
  await page.mouse.move(sx, sy);
  await page.mouse.down();
  for (let i = 1; i <= 20; i++) {
    await page.mouse.move(sx + i * 15, sy, { steps: 2 });
    await page.waitForTimeout(20);
  }
  await page.mouse.up();
  await page.waitForTimeout(1000);
  await page.screenshot({ path: '/tmp/4-detail-view.png' });

  await browser.close();
})();
