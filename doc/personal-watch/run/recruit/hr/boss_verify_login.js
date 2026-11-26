// Boss 直聘 · 登录态复核：注入 cookie → 打开会话页 → 点开第一个会话 → 核对会话头/消息区/输入框
// 只读：只点会话项，不发消息、不点任何邀约或简历控件。
// 用法：node verify_login.js（BOSS_COOKIE / BOSS_PROFILE / BOSS_OUT）
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const PROFILE = process.env.BOSS_PROFILE || path.join(__dirname, 'profile');
const COOKIE = process.env.BOSS_COOKIE || '';
const OUT = process.env.BOSS_OUT || path.join(__dirname, 'verify_login.json');

function parseCookies(s) {
  return s.split(';').map(x => x.trim()).filter(Boolean).map(kv => {
    const i = kv.indexOf('=');
    return { name: kv.slice(0, i).trim(), value: kv.slice(i + 1).trim(), url: 'https://www.zhipin.com/' };
  }).filter(c => c.name);
}

const result = {
  at: new Date().toISOString(), ok: false, error: '', url: '',
  cookieCount: 0, authCookies: [], step: '', conversationMain: '', has: {}, lastMessages: [],
};

(async () => {
  let ctx;
  try {
    ctx = await chromium.launchPersistentContext(PROFILE, {
      channel: 'chrome',
      headless: false,
      viewport: { width: 1500, height: 950 },
      args: ['--disable-blink-features=AutomationControlled', '--no-first-run', '--no-default-browser-check'],
    });

    const cs = parseCookies(COOKIE);
    result.cookieCount = cs.length;
    result.authCookies = ['wt2', 'wbg', 'zp_at', 'bst'].filter(k => cs.some(c => c.name === k));
    if (cs.length) await ctx.addCookies(cs);

    ctx.on('page', p => { p.on('dialog', d => d.dismiss().catch(() => {})); });
    const page = await ctx.newPage();
    page.on('dialog', d => d.dismiss().catch(() => {}));

    await page.goto('https://www.zhipin.com/web/chat/index', { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(8000);
    result.url = page.url();

    const clicked = await page.evaluate(() => {
      const it = document.querySelector('.geek-item-wrap .geek-item') || document.querySelector('.geek-item');
      if (!it) return false;
      it.click();
      return true;
    });
    result.step = clicked ? 'clicked-first-conversation' : 'no-conversation-found';
    await page.waitForTimeout(2500);

    const d = await page.evaluate(() => {
      const txt = el => (el ? (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim() : '');
      const list = document.querySelector('.chat-message-list');
      const msgs = list
        ? [...list.querySelectorAll(':scope > *')].slice(-4).map(e => txt(e).slice(0, 140))
        : [];
      return {
        has: {
          userList: !!document.querySelector('.user-list'),
          chatMessageList: !!document.querySelector('.chat-message-list'),
          editor: !!document.getElementById('boss-chat-editor-input'),
          submit: !!document.querySelector('.submit-content .submit'),
          conversationMain: !!document.querySelector('.conversation-main'),
        },
        head: txt(document.querySelector('.conversation-main')).slice(0, 240),
        msgs,
      };
    });

    result.has = d.has;
    result.conversationMain = d.head;
    result.lastMessages = d.msgs;
    result.ok = !!(d.has.chatMessageList && d.has.userList && d.has.conversationMain && d.has.editor);
  } catch (e) {
    result.error = String((e && e.message) || e).slice(0, 500);
  }
  let writeErr = '';
  try { fs.writeFileSync(OUT, JSON.stringify(result, null, 2), 'utf8'); } catch (e) { writeErr = String(e && e.message || e); }
  console.log('OK=' + result.ok + ' step=' + result.step + ' err=' + result.error);
  console.log('OUTPATH=' + OUT + ' | dirname=' + __dirname + ' | cwd=' + process.cwd()
    + ' | existsAfterWrite=' + fs.existsSync(OUT) + ' | writeErr=' + writeErr);
  console.log('AUTH=' + JSON.stringify(result.authCookies) + ' URL=' + result.url);
  console.log('HAS=' + JSON.stringify(result.has));
  console.log('HEAD=' + Buffer.from(String(result.conversationMain), 'utf8').toString('base64'));
  console.log('MSGS=' + Buffer.from((result.lastMessages || []).join(' ||| '), 'utf8').toString('base64'));
  try { if (ctx) await ctx.close(); } catch (e) {}
})();
