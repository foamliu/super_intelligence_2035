// Boss READ-ONLY conversation scanner (no sending, no clicks on controls)
// Purpose: list the most-recent conversations + dump the tail of each message list,
//          so we can see which candidates REPLIED in the last N hours.
// Env: BOSS_COOKIE (required) | BOSS_REPORT6 (out json) | BOSS_TOP (how many conversations, default 20)
const fs = require('fs');
const { chromium } = require('playwright');

const PROFILE = 'C:/Users/liuyu/AppData/Local/Temp/boss_scan/profile';
const OUT = process.env.BOSS_REPORT6 || 'C:/Users/liuyu/AppData/Local/Temp/boss_scan/scan_msgs.json';
const TOP = parseInt(process.env.BOSS_TOP || '20', 10);

const parseCookies = s => s.split(';').map(x => x.trim()).filter(Boolean).map(kv => {
  const i = kv.indexOf('='); return { name: kv.slice(0, i).trim(), value: kv.slice(i + 1).trim(), url: 'https://www.zhipin.com/' };
}).filter(c => c.name);

const res = { at: new Date().toISOString(), top: TOP, list: [], items: [] };
const flush = () => fs.writeFileSync(OUT, JSON.stringify(res, null, 2), 'utf8');

(async () => {
  let ctx;
  try {
    ctx = await chromium.launchPersistentContext(PROFILE, { channel: 'chrome', headless: false, viewport: { width: 1500, height: 950 },
      args: ['--disable-blink-features=AutomationControlled', '--no-first-run', '--no-default-browser-check'] });
    const cs = parseCookies(process.env.BOSS_COOKIE || '');
    if (cs.length) await ctx.addCookies(cs);
    ctx.on('page', p => { p.on('dialog', d => d.dismiss().catch(() => {})); });
    const page = await ctx.newPage();
    page.on('dialog', d => d.dismiss().catch(() => {}));
    await page.goto('https://www.zhipin.com/web/chat/index', { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(9000);
    res.landedUrl = page.url();
    await page.waitForFunction(() => document.querySelectorAll('.geek-item-wrap').length >= 5, null, { timeout: 30000 }).catch(() => {});
    await page.waitForTimeout(1500);

    // phase 1: collect conversation names (scroll a bit to load more, stop when height stable 3x)
    let stable = 0, lastH = 0;
    for (let i = 0; i < 30 && stable < 3; i++) {
      const h = await page.evaluate(() => {
        const l = document.querySelector('.user-list'); if (!l) return -1;
        l.scrollTop = Math.min(l.scrollHeight - l.clientHeight, l.scrollTop + 400);
        return l.scrollHeight;
      });
      if (h === lastH) stable++; else { stable = 0; lastH = h; }
      await page.waitForTimeout(stable ? 1600 : 700);
    }
    res.list = await page.evaluate(() => {
      const t = el => (el ? (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim() : '');
      return [...document.querySelectorAll('.geek-item-wrap')]
        .map(e => t(e.querySelector('.geek-name')) || t(e).split(' ')[0] || '')
        .filter(Boolean);
    });
    flush();

    // phase 2: for each of the first TOP conversations, open it and dump the tail
    const targets = res.list.slice(0, TOP);
    for (const nm of targets) {
      await page.evaluate(() => { const l = document.querySelector('.user-list'); if (l) l.scrollTop = 0; });
      await page.waitForTimeout(700);
      let clicked = false;
      for (let k = 0; k < 120 && !clicked; k++) {
        const r = await page.evaluate((nm) => {
          const t = el => (el ? (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim() : '');
          const items = [...document.querySelectorAll('.geek-item-wrap')];
          const it = items.find(e => t(e.querySelector('.geek-name, .name')) === nm || t(e).split(' ').includes(nm));
          if (it) { (it.querySelector('.geek-item') || it).click(); return 'clicked'; }
          const list = document.querySelector('.user-list');
          if (!list) return 'nolist';
          const max = list.scrollHeight - list.clientHeight;
          if (list.scrollTop >= max - 4) return (max < 300 && items.length < 8) ? 'wait' : 'bottom';
          list.scrollTop = Math.min(max, list.scrollTop + 300);
          return 'scrolling';
        }, nm);
        if (r === 'clicked') clicked = true;
        else if (r === 'bottom' || r === 'nolist') break;
        else await page.waitForTimeout(r === 'wait' ? 2000 : 600);
      }
      await page.waitForTimeout(2200);
      const info = await page.evaluate(() => {
        const t = el => (el ? (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim() : '');
        const ml = document.querySelector('.chat-message-list');
        const main = document.querySelector('.conversation-main');
        const lines = ml ? (ml.innerText || '').split('\n').map(s => s.trim()).filter(Boolean) : [];
        return {
          header: main ? t(main).slice(0, 300) : '',
          tail: (ml ? t(ml) : '').slice(-900),
          lastLines: lines.slice(-14),
        };
      });
      res.items.push(Object.assign({ name: nm, clicked }, info));
      flush();
      await page.waitForTimeout(1200);
    }
  } catch (e) { res.error = String((e && e.message) || e).slice(0, 400); flush(); }
  console.log('SCAN_DONE ' + JSON.stringify(res.items.map(i => ({ n: i.name, c: i.clicked }))));
  try { if (ctx) await ctx.close(); } catch (e) {}
})();