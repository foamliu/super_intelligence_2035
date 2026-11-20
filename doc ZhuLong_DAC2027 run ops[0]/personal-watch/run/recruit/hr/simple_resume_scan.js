// Boss 直聘 · 只读「简单简历」扫描 v2：先收割全会话列表建索引（名字→位置），再逐个跳转读会话头简单简历
// 不发消息、不点任何控件、不下载简历。
// 用法：node resume_scan2.js（BOSS_COOKIE / BOSS_PROFILE / BOSS_NAMES / BOSS_OUT / BOSS_LIMIT / BOSS_PAUSE_MS）
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const PROFILE = process.env.BOSS_PROFILE || path.join(__dirname, 'profile');
const COOKIE = process.env.BOSS_COOKIE || '';
const OUT = process.env.BOSS_OUT || path.join(__dirname, 'resume_scan.json');
const NAMES = process.env.BOSS_NAMES || path.join(__dirname, 'names.txt');
const LIMIT = Number(process.env.BOSS_LIMIT || 0);
const PAUSE = Number(process.env.BOSS_PAUSE_MS || 1200);
const LOG = path.join(__dirname, 'resume_scan.log');
function log(s) { try { fs.appendFileSync(LOG, '[' + new Date().toISOString() + '] ' + s + '\n', 'utf8'); } catch (e) {} }
function parseCookies(s) {
  return s.split(';').map(x => x.trim()).filter(Boolean).map(kv => {
    const i = kv.indexOf('=');
    return { name: kv.slice(0, i).trim(), value: kv.slice(i + 1).trim(), url: 'https://www.zhipin.com/' };
  }).filter(c => c.name);
}

let names = fs.readFileSync(NAMES, 'utf8').replace(/^\uFEFF/, '').split(/\r?\n/).map(s => s.trim()).filter(Boolean);
if (LIMIT) names = names.slice(0, LIMIT);

let state = { at: '', rows: {} };
try {
  if (fs.existsSync(OUT)) {
    const j = JSON.parse(fs.readFileSync(OUT, 'utf8'));
    if (j && j.rows && typeof j.rows === 'object' && !Array.isArray(j.rows)) state = j;
  }
} catch (e) { log('STATE_READ_WARN ' + String(e.message || e)); }
function flush() { state.at = new Date().toISOString(); fs.writeFileSync(OUT, JSON.stringify(state, null, 2), 'utf8'); }

// 收割：从头滚到底，记录每个名字出现时的 scrollTop（虚拟列表渲染窗口）
async function harvest(page) {
  const idx = {};
  let lastTop = -1, stuck = 0;
  for (let k = 0; k < 400; k++) {
    const r = await page.evaluate(() => {
      const t = el => (el ? (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim() : '');
      const l = document.querySelector('.user-list');
      const seen = [...document.querySelectorAll('.geek-item-wrap')].map(w => ({
        n: t(w.querySelector('.geek-name, .name')), top: l ? l.scrollTop : 0,
      })).filter(x => x.n);
      return { seen, top: l ? l.scrollTop : 0 };
    });
    r.seen.forEach(x => { if (!(x.n in idx) || x.top < idx[x.n].top) idx[x.n] = { top: x.top }; });
    if (r.top === lastTop) { stuck++; if (stuck >= 2) break; } else stuck = 0;
    lastTop = r.top;
    const before = await page.evaluate(() => {
      const l = document.querySelector('.user-list');
      if (!l) return -1;
      const b = l.scrollTop;
      l.scrollTop = Math.min(b + 300, l.scrollHeight);
      return b;
    });
    if (before < 0) break;
    await page.waitForTimeout(200);
  }
  return idx;
}

// 跳到指定位置附近找这个人并点击
async function clickByName(page, nm, topPos) {
  for (let s = 0; s < 24; s++) {
    const target = Math.max(0, topPos - 600 + s * 300);
    const r = await page.evaluate(({ name, top }) => {
      const t = el => (el ? (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim() : '');
      const l = document.querySelector('.user-list');
      if (l) l.scrollTop = top;
      const items = [...document.querySelectorAll('.geek-item-wrap')];
      let it = items.find(w => t(w.querySelector('.geek-name, .name')) === name);
      if (!it) it = items.find(w => (t(w.querySelector('.geek-name, .name')) || '').includes(name));
      if (it) { (it.querySelector('.geek-item') || it).click(); return 'clicked'; }
      return 'miss';
    }, { name: nm, top: target });
    if (r === 'clicked') return true;
    await page.waitForTimeout(260);
  }
  return false;
}


(async () => {
  let ctx;
  try {
    ctx = await chromium.launchPersistentContext(PROFILE, {
      channel: 'chrome', headless: false,
      viewport: { width: 1500, height: 950 },
      args: ['--disable-blink-features=AutomationControlled', '--no-first-run', '--no-default-browser-check'],
    });
    const cs = parseCookies(COOKIE);
    if (cs.length) await ctx.addCookies(cs);
    ctx.on('page', p => { p.on('dialog', d => d.dismiss().catch(() => {})); });
    const page = await ctx.newPage();
    page.on('dialog', d => d.dismiss().catch(() => {}));

    await page.goto('https://www.zhipin.com/web/chat/index', { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(7000);

    const guard = await page.evaluate(() => ({ url: location.href, hasList: !!document.querySelector('.user-list') }));
    if (!guard.hasList || /login\.zhipin\.com|bticket/.test(guard.url)) {
      log('GUARD_FAIL ' + JSON.stringify(guard)); flush();
      try { await ctx.close(); } catch (e) {}
      return;
    }

    log('HARVEST_START');
    const idx = await harvest(page);
    log('HARVEST_DONE total=' + Object.keys(idx).length);
    state.index = idx;
    flush();

    const todo = names.filter(nm => !(state.rows[nm] && state.rows[nm].header));
    log('TODO=' + todo.length + ' ' + JSON.stringify(todo));
    let done = 0;
    for (const nm of todo) {
      const rec = { header: '', card: '', error: '' };
      const pos = idx[nm] ? idx[nm].top : null;
      if (pos === null) { rec.error = 'not_in_conversation_list'; state.rows[nm] = rec; log(nm + ' ABSENT'); flush(); continue; }
      let ok = false;
      try { ok = await clickByName(page, nm, pos); } catch (e) { rec.error = 'click_err:' + String(e.message || e).slice(0, 120); }
      if (!ok) { rec.error = 'click_failed'; state.rows[nm] = rec; log(nm + ' CLICK_FAIL'); flush(); continue; }
      await page.waitForTimeout(PAUSE);
      const data = await page.evaluate(() => {
        const t = el => (el ? (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim() : '');
        const main = document.querySelector('.conversation-main');
        return { header: main ? t(main).slice(0, 900) : '' };
      });
      if (!data.header.includes(nm)) {
        rec.error = 'wrong_conversation(main=' + data.header.slice(0, 40) + ')';
        state.rows[nm] = rec; log(nm + ' ' + rec.error); flush(); continue;
      }
      rec.header = data.header;
      state.rows[nm] = rec;
      done++;
      log(nm + ' OK | ' + rec.header.slice(0, 200));
      flush();
    }
    log('DONE scanned_new=' + done + ' total=' + Object.keys(state.rows).length);
    console.log('DONE scanned_new=' + done);
  } catch (e) {
    log('FATAL ' + String((e && e.message) || e));
    console.log('FATAL ' + String((e && e.message) || e));
  }
  try { if (ctx) await ctx.close(); } catch (e) {}
})();
