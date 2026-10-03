import puppeteer from 'puppeteer-core';
import fs from 'fs';
import path from 'path';

const urls = [
  { id: 1, url: 'https://share.gemini.google/z2qblhYK0TLA', defaultFile: '01_模块化自重构机器人原型机设计方案.md' },
  { id: 2, url: 'https://share.gemini.google/4GBFlMPSFnrF', defaultFile: '02_资料2.md' },
  { id: 3, url: 'https://share.gemini.google/qSpHg1ZvTOcS', defaultFile: '03_资料3.md' },
  { id: 4, url: 'https://share.gemini.google/CnlU2EoiejsW', defaultFile: '04_资料4.md' }
];

async function run() {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true,
    args: [
      '--proxy-server=http://127.0.0.1:7897',
      '--no-sandbox',
      '--disable-setuid-sandbox'
    ]
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  for (const item of urls) {
    console.log('[Processing item ' + item.id + '] ' + item.url);
    try {
      await page.goto(item.url, { waitUntil: 'networkidle2', timeout: 60000 });
      await new Promise(r => setTimeout(r, 6000));

      const pageData = await page.evaluate(() => {
        let title = document.title;
        const h1 = document.querySelector('h1');
        if (h1 && h1.innerText.trim()) {
          title = h1.innerText.trim();
        }

        // Try to locate conversation elements or fallback to clean body text
        const bodyText = document.body.innerText;
        return {
          title,
          bodyText
        };
      });

      console.log('Extracted Title: ' + pageData.title);
      console.log('Body text length: ' + pageData.bodyText.length);

      let content = '# ' + pageData.title + '\n\n';
      content += '> 原文链接: ' + item.url + '\n\n';
      content += pageData.bodyText;

      const filename = path.join('doc', item.defaultFile);
      fs.writeFileSync(filename, content, 'utf8');
      console.log('Saved ' + filename);
    } catch (e) {
      console.error('Error processing ' + item.url + ':', e);
    }
  }

  await browser.close();
  console.log('All done!');
}

run();
