import puppeteer from 'puppeteer-core';
import fs from 'fs';
import path from 'path';

const urls = [
  { id: 1, url: 'https://share.gemini.google/z2qblhYK0TLA', file: '01_模块化自重构机器人原型机设计方案.md' },
  { id: 2, url: 'https://share.gemini.google/4GBFlMPSFnrF', file: '02_模块软硬件与电源设计方案.md' },
  { id: 3, url: 'https://share.gemini.google/qSpHg1ZvTOcS', file: '03_模块化电能能效评价体系设计.md' },
  { id: 4, url: 'https://share.gemini.google/CnlU2EoiejsW', file: '04_五维一体物理单元设计方案.md' }
];

function cleanQuery(text) {
  if (!text) return '';
  text = text.trim();
  if (text.startsWith('你说 ')) {
    const parts = text.split('\n\n');
    if (parts.length > 1 && parts[0].replace('你说 ', '').trim() === parts[1].trim()) {
      return parts[1].trim();
    }
    return text.replace(/^你说\s+/, '').trim();
  }
  return text;
}

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

        const queryNodes = Array.from(document.querySelectorAll('user-query'));
        const responseNodes = Array.from(document.querySelectorAll('message-content'));

        const turns = [];
        const maxLen = Math.max(queryNodes.length, responseNodes.length);
        for (let i = 0; i < maxLen; i++) {
          turns.push({
            query: queryNodes[i] ? queryNodes[i].innerText.trim() : '',
            response: responseNodes[i] ? responseNodes[i].innerText.trim() : ''
          });
        }

        return {
          title,
          turns,
          bodyText: document.body.innerText
        };
      });

      console.log('Extracted Title: ' + pageData.title);
      console.log('Turns count: ' + pageData.turns.length);

      let md = '# ' + pageData.title + '\n\n';
      md += '> **来源链接**: [' + item.url + '](' + item.url + ')\n';
      md += '> **生成时间**: ' + new Date().toISOString() + '\n\n---\n\n';

      if (pageData.turns.length > 0) {
        pageData.turns.forEach((t, idx) => {
          const q = cleanQuery(t.query);
          md += '## 对话轮次 ' + (idx + 1) + '\n\n';
          if (q) {
            md += '### 提问\n\n' + q + '\n\n';
          }
          if (t.response) {
            md += '### 回答\n\n' + t.response + '\n\n';
          }
          md += '---\n\n';
        });
      } else {
        md += pageData.bodyText;
      }

      const outPath = path.join('doc', item.file);
      fs.writeFileSync(outPath, md, 'utf8');
      console.log('Successfully saved to ' + outPath + ' (' + md.length + ' chars)');

    } catch (e) {
      console.error('Error processing ' + item.url + ':', e);
    }
  }

  await browser.close();
  console.log('All docs exported successfully!');
}

run();