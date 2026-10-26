// Screen capture of a public web page (S48: the real announcement page): a full-page PNG at 1920 px wide, plus the
// page's text and the fetch time, so the capture can be logged and checked. Usage: node scripts/capture_page.mjs <url> <out.png>
// --no-sandbox: Ubuntu AppArmor blocks Chrome's user-namespace sandbox on this machine.
import fs from 'fs';
import puppeteer from 'puppeteer';

const [url, out] = process.argv.slice(2);
const browser = await puppeteer.launch({ headless: 'shell', args: ['--no-sandbox'] });
const page = await browser.newPage();
await page.setViewport({ width: 1920, height: 1080 });
const resp = await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
await new Promise((r) => setTimeout(r, 1500));
await page.screenshot({ path: out, fullPage: true });
fs.writeFileSync(out.replace(/\.png$/, '.txt'), await page.evaluate(() => document.body.innerText));
fs.writeFileSync(out.replace(/\.png$/, '.json'), JSON.stringify({ url, final_url: page.url(), status: resp.status(),
  fetched: new Date().toISOString(), title: await page.title() }, null, 1));
console.log(resp.status(), page.url(), await page.title());
await browser.close();
