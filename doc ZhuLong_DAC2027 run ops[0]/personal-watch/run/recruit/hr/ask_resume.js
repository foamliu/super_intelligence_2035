// Boss: click 求简历 then confirm the "确定向牛人索取简历吗？" tooltip (d-c=61025)
const fs = require('fs');
const { chromium } = require('playwright');
const PROFILE = 'C:/Users/liuyu/AppData/Local/Temp/boss_scan/profile';
const OUT = process.env.BOSS_REPORT3 || 'C:/Users/liuyu/AppData/Local/Temp/boss_scan/ask_resume.json';
const NAMES = (function () {
  const nf = process.env.BOSS_NAMES_FILE || 'C:/Users/liuyu/AppData/Local/Temp/boss_scan/ask_targets.txt';
  return fs.readFileSync(nf, 'utf8').split(/\r?\n/).map(s => s.trim()).filter(Boolean);
})();
const parseCookies = s => s.split(';').map(x => x.trim()).filter(Boolean).map(kv => { const i = kv.indexOf('='); return { name: kv.slice(0, i).trim(), value: kv.slice(i + 1).trim(), url: 'https://www.zhipin.com/' }; }).filter(c => c.name);
const res = { at: new Date().toISOString(), items: [] };
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
    await page.waitForFunction(() => document.querySelectorAll('.geek-item-wrap').length >= 5, null, { timeout: 30000 }).catch(() => {});
    await page.waitForTimeout(1500);
    for (const nm of NAMES) {
      const rec = { name: nm, found: false, header: '', step1: null, step2: null, step3: null };
      let found = false;
      await page.evaluate(() => { const l = document.querySelector('.user-list'); if (l) l.scrollTop = 0; });
      await page.waitForTimeout(800);
      let lastH = -1, stall = 0;
      for (let k = 0; k < 300 && !found; k++) {
        const r = await page.evaluate(n => {
          const t = el => (el ? (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim() : '');
          const items = [...document.querySelectorAll('.geek-item-wrap')];
          const it = items.find(w => t(w.querySelector('.geek-name, .name')) === n || t(w).split(' ').includes(n));
          if (it) { (it.querySelector('.geek-item') || it).click(); return { a: 'clicked', h: 0 }; }
          const l = document.querySelector('.user-list');
          if (!l) return { a: 'nolist', h: 0 };
          const max = l.scrollHeight - l.clientHeight;
          if (l.scrollTop >= max - 4) return { a: (max < 300 && items.length < 8) ? 'wait' : 'bottom', h: l.scrollHeight };
          l.scrollTop = Math.min(max, l.scrollTop + 300);
          return { a: 'scrolling', h: l.scrollHeight };
        }, nm);
        if (r.a === 'clicked') found = true;
        else if (r.a === 'nolist') break;
        else if (r.a === 'bottom') {
          if (r.h === lastH) { if (++stall >= 4) break; } else { stall = 0; lastH = r.h; }
          await page.waitForTimeout(2000);   // 「滚动加载更多」：到底后要等
        }
        else await page.waitForTimeout(r.a === 'wait' ? 2000 : 600);
      }
      rec.found = found;
      if (!found) { res.items.push(rec); flush(); continue; }
      await page.waitForTimeout(2600);
      rec.header = await page.evaluate(() => { const m = document.querySelector('.conversation-main'); return m ? (m.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 100) : ''; });
      if (rec.header.indexOf(nm) < 0) { rec.err = 'header_mismatch'; res.items.push(rec); flush(); continue; }
      const openTip = () => page.evaluate(() => { const tip = document.querySelector('.operate-exchange-left .operate-icon-item[d-c="61025"] .exchange-tooltip'); if (!tip) return 'no_tip_el'; const s = getComputedStyle(tip); const r = tip.getBoundingClientRect(); return 'display=' + s.display + ';wh=' + Math.round(r.width) + 'x' + Math.round(r.height); });
      const diag = { before: await openTip() };
      const already = diag.before.indexOf('display=none') < 0 && diag.before.indexOf(';wh=0x') < 0;
      diag.alreadyOpen = already;
      if (!already) {
        try { await page.click('.operate-exchange-left .operate-icon-item[d-c="61025"] .operate-btn', { timeout: 8000 }); diag.askClicked = true; }
        catch (e) { diag.askClicked = false; diag.askErr = String(e.message).slice(0, 90); }
        await page.waitForTimeout(1500);
      }
      diag.mid = await openTip();
      try { await page.click('.operate-exchange-left .operate-icon-item[d-c="61025"] .exchange-tooltip .boss-btn-primary', { timeout: 6000 }); diag.confirmClicked = true; }
      catch (e) { diag.confirmClicked = false; diag.confirmErr = String(e.message).slice(0, 90); }
      rec.step1 = diag;
      await page.waitForTimeout(4500);
      rec.step3 = await page.evaluate(() => {
        const t = e => (e ? (e.innerText || e.textContent || '').replace(/\s+/g, ' ').trim() : '');
        const ml = document.querySelector('.chat-message-list');
        const body = document.body.innerText || '';
        return {
          tipStillVisible: [...document.querySelectorAll('.operate-exchange-left .exchange-tooltip')].some(e => e.offsetParent !== null),
          hasSentTip: body.indexOf('简历请求已发送') >= 0,
          resumeLines: [...new Set(body.split('\n').map(s => s.replace(/\s+/g, ' ').trim()).filter(s => s && s.length <= 40 && /简历/.test(s)))].slice(0, 18),
          tail: ml ? t(ml).slice(-380) : '',
          btns: [...document.querySelectorAll('.operate-exchange-left .operate-icon-item')].map(e => ({ txt: t(e), dis: /disabled/.test(String(e.className)) || !!e.querySelector('.disabled') })),
        };
      });
      res.items.push(rec); flush();
      await page.waitForTimeout(2500);
    }
  } catch (e) { res.error = String((e && e.message) || e).slice(0, 300); flush(); }
  console.log('ASK_DONE ' + JSON.stringify(res.items.map(i => ({ n: i.name, f: i.found, s1: i.step1 && i.step1.clicked, s2: i.step2 && i.step2.confirmed, sent: i.step3 && i.step3.hasSentTip }))));
  try { if (ctx) await ctx.close(); } catch (e) {}
})();
