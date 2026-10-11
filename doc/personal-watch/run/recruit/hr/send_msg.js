// Boss 直聘 · 定点发送（按姓名切会话 → 核对会话头 → 输入 → 发送 → 校验送达）
// 用法：node send_msg.js   （环境变量：BOSS_COOKIE / BOSS_PROFILE / BOSS_TARGETS / BOSS_REPORT / BOSS_GAP_MS）
// 纪律：≤2–3 人/批；每人之间随机停顿；发送前必须核对 .conversation-main 的姓名，不符立即跳过。
const fs = require('fs');
const { chromium } = require('playwright');

const PROFILE = process.env.BOSS_PROFILE || 'profile';
const COOKIE = process.env.BOSS_COOKIE || '';
const REPORT = process.env.BOSS_REPORT || 'send_report.json';
const GAP = Number(process.env.BOSS_GAP_MS || 25000);
const TARGETS = (function () {
  const f = process.env.BOSS_TARGETS_FILE;
  if (f && fs.existsSync(f)) return JSON.parse(fs.readFileSync(f, 'utf8'));
  return JSON.parse(process.env.BOSS_TARGETS || '[]');
})(); // [{name, text}]

function parseCookies(s) {
  return s.split(';').map(x => x.trim()).filter(Boolean).map(kv => {
    const i = kv.indexOf('=');
    return { name: kv.slice(0, i).trim(), value: kv.slice(i + 1).trim(), url: 'https://www.zhipin.com/' };
  }).filter(c => c.name);
}

const results = [];
function flush() {
  fs.writeFileSync(REPORT, JSON.stringify({ at: new Date().toISOString(), results }, null, 2), 'utf8');
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

    const guard = await page.evaluate(() => ({
      url: location.href,
      hasList: !!document.querySelector('.user-list'),
      hasChat: !!document.querySelector('.chat-message-list'),
      editor: !!document.getElementById('boss-chat-editor-input'),
      submit: !!document.querySelector('.submit-content .submit'),
    }));
    // 刚进页面可能未选中任何会话（此时没有 .chat-message-list / 输入框），
    // 所以只校验左侧列表存在 + 未被跳登录页；逐个切换会话时再校验会话头与输入框。
    if (!guard.hasList || /login\.zhipin\.com|bticket/.test(guard.url)) {
      results.push({ step: 'guard', ok: false, guard });
      flush();
      console.log('GUARD_FAIL ' + JSON.stringify(guard));
      if (ctx) await ctx.close();
      return;
    }

    for (let n = 0; n < TARGETS.length; n++) {
      const tgt = TARGETS[n];
      const rec = { name: tgt.name, text: tgt.text, switched: false, header: '', sent: false, lastMsg: '', status: '', error: '' };
      try {
        // ---- 1) 虚拟列表滚动查找 + 点击 ----
        let found = false;
        await page.evaluate(() => { const l = document.querySelector('.user-list'); if (l) l.scrollTop = 0; });
        await page.waitForTimeout(700);
        let lastH = -1, stall = 0;
        for (let k = 0; k < 300 && !found; k++) {
          const r = await page.evaluate((nm) => {
            const t = el => (el ? (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim() : '');
            const items = [...document.querySelectorAll('.geek-item-wrap')];
            const it = items.find(w => t(w.querySelector('.geek-name, .name')) === nm || t(w).split(' ').includes(nm));
            if (it) { (it.querySelector('.geek-item') || it).click(); return { a: 'clicked', h: 0 }; }
            const l = document.querySelector('.user-list');
            if (!l) return { a: 'nolist', h: 0 };
            const max = l.scrollHeight - l.clientHeight;
            if (l.scrollTop >= max - 4) return { a: (max < 300 && items.length < 8) ? 'wait' : 'bottom', h: l.scrollHeight };
            l.scrollTop = Math.min(max, l.scrollTop + 300);
            return { a: 'scrolling', h: l.scrollHeight };
          }, tgt.name);
          if (r.a === 'clicked') found = true;
          else if (r.a === 'nolist') break;
          else if (r.a === 'bottom') {
            if (r.h === lastH) { if (++stall >= 4) break; } else { stall = 0; lastH = r.h; }
            await page.waitForTimeout(2000);   // 「滚动加载更多」：到底后要等
          }
          else await page.waitForTimeout(r.a === 'wait' ? 2000 : 600);
        }
        rec.switched = found;
        if (!found) { rec.error = 'list_item_not_found'; results.push(rec); flush(); continue; }

        await page.waitForTimeout(2200);

        // ---- 2) 核对会话头姓名（AGENTS.md §4 铁律）----
        const header = await page.evaluate(() => {
          const el = document.querySelector('.conversation-main');
          return el ? (el.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 80) : '';
        });
        rec.header = header;
        if (header.indexOf(tgt.name) < 0) { rec.error = 'header_mismatch'; results.push(rec); flush(); continue; }

        // ---- 3) 输入 + 发送 ----
        const ready = await page.evaluate(() => ({
          editor: !!document.getElementById('boss-chat-editor-input'),
          submit: !!document.querySelector('.submit-content .submit'),
          chat: !!document.querySelector('.chat-message-list'),
        }));
        if (!ready.editor || !ready.submit) { rec.error = 'no_editor:' + JSON.stringify(ready); results.push(rec); flush(); continue; }

        await page.click('#boss-chat-editor-input');
        await page.waitForTimeout(500);
        await page.keyboard.insertText(tgt.text);
        await page.waitForTimeout(700);
        const typed = await page.evaluate(() => {
          const el = document.getElementById('boss-chat-editor-input');
          return el ? (el.innerText || '').trim() : '';
        });
        if (typed.indexOf(tgt.text.slice(0, 8)) < 0) { rec.error = 'insert_failed: ' + typed.slice(0, 60); results.push(rec); flush(); continue; }

        await page.click('.submit-content .submit');
        await page.waitForTimeout(3000);

        // ---- 4) 校验已出现且状态 ----
        const tail = await page.evaluate(() => {
          const t = el => (el ? (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim() : '');
          const msgs = [...document.querySelectorAll('.chat-message-list .message-item, .chat-message-list li, .chat-message-list > div')];
          return msgs.slice(-2).map(m => t(m));
        });
        rec.lastMsg = (tail[tail.length - 1] || '').slice(0, 200);
        rec.sent = rec.lastMsg.indexOf(tgt.text.slice(0, 8)) >= 0;
        rec.status = /已读/.test(rec.lastMsg) ? '已读' : (/送达/.test(rec.lastMsg) ? '送达' : '未知（消息已出现）');
        if (!rec.sent) rec.error = 'sent_not_verified';
      } catch (e) {
        rec.error = String((e && e.message) || e).slice(0, 300);
      }
      results.push(rec);
      flush();
      if (n < TARGETS.length - 1) await page.waitForTimeout(GAP);
    }
  } catch (e) {
    results.push({ step: 'fatal', ok: false, error: String((e && e.message) || e).slice(0, 500) });
    flush();
  }
  console.log('DONE ' + JSON.stringify(results.map(r => ({ n: r.name, sent: r.sent, st: r.status, err: r.error })), null, 0));
  try { if (ctx) await ctx.close(); } catch (e) {}
})();