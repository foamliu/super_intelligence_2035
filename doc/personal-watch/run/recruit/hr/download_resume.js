// Boss resume PDF downloader  (SOP: AGENTS.md §7)
// Flow: switch conversation -> verify .conversation-main -> find "点击预览附件简历"
//       -> intercept response /wflow/zpgeek/download/preview4boss/{geekId} -> write PDF
//       -> hide preview container.  NO control clicks (no 约面试/换电话/换微信/同意/拒绝).
// Env: BOSS_COOKIE (required) | BOSS_NAMES_FILE | BOSS_OUTDIR | BOSS_REPORT5 | BOSS_DRY=1 (probe only)
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const PROFILE = 'C:/Users/liuyu/AppData/Local/Temp/boss_scan/profile';
const TFILE = process.env.BOSS_NAMES_FILE || 'C:/Users/liuyu/AppData/Local/Temp/boss_scan/dl_targets.txt';
const OUT = process.env.BOSS_REPORT5 || 'C:/Users/liuyu/AppData/Local/Temp/boss_scan/download_report.json';
const DRY = String(process.env.BOSS_DRY || '') === '1';
const pad = n => String(n).padStart(2, '0');
const stamp = (d = new Date()) => d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
const stampU = (d = new Date()) => d.getFullYear() + '_' + pad(d.getMonth() + 1) + '_' + pad(d.getDate());  // 2026_09_27 (file-name prefix)
const CATEGORY = String(process.env.BOSS_CATEGORY || '').trim();   // 'intern' | 'social' | '' 
const CATDIR = CATEGORY === 'intern' ? '实习生' : (CATEGORY === 'social' ? '社招' : '');
const OUTDIR = process.env.BOSS_OUTDIR || ('C:/Users/liuyu/recruit/简历/' + (CATDIR ? CATDIR + '/' : ''));   // 2026-09-27 起：不建日期子目录，日期写进文件名
const NAMES = fs.readFileSync(TFILE, 'utf8').split(/\r?\n/).map(s => s.trim()).filter(Boolean);

const parseCookies = s => s.split(';').map(x => x.trim()).filter(Boolean).map(kv => {
  const i = kv.indexOf('='); return { name: kv.slice(0, i).trim(), value: kv.slice(i + 1).trim(), url: 'https://www.zhipin.com/' };
}).filter(c => c.name);

const res = { at: new Date().toISOString(), dry: DRY, category: CATEGORY, outDir: OUTDIR, targets: NAMES, items: [] };
const flush = () => fs.writeFileSync(OUT, JSON.stringify(res, null, 2), 'utf8');
const safeName = s => s.replace(/[\\/:*?"<>|]/g, '_').trim();

// probe: header + whether an attachment-resume entry exists (+ pdf file names shown)
const PROBE = () => {
  const t = el => (el ? (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim() : '');
  const ml = document.querySelector('.chat-message-list');
  const main = document.querySelector('.conversation-main');
  const leaf = [...document.querySelectorAll('.chat-message-list *')]
    .filter(e => e.children.length === 0 && (e.innerText || '').indexOf('点击预览附件简历') >= 0);
  const lines = (ml ? (ml.innerText || '') : '').split('\n').map(s => s.trim());
  const pdfs = lines.filter(s => /\.pdf$/i.test(s) && s.length <= 90);
  return {
    header: main ? t(main).slice(0, 220) : '',
    attachEntries: leaf.length,
    pdfs: [...new Set(pdfs)].slice(-3),
    hasConsentCard: (document.body.innerText || '').indexOf('对方想发送附件简历') >= 0,
    hasSentTip: (document.body.innerText || '').indexOf('简历请求已发送') >= 0,
  };
};

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

    // pass 1: which targets exist in the virtual list  (keep scrolling while "load more" adds height)
    const present = {};
    await page.evaluate(() => { const l = document.querySelector('.user-list'); if (l) l.scrollTop = 0; });
    await page.waitForTimeout(800);
    let lastH1 = -1, stall1 = 0;
    for (let k = 0; k < 500; k++) {
      const r = await page.evaluate((names) => {
        const t = el => (el ? (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim() : '');
        const items = [...document.querySelectorAll('.geek-item-wrap')];
        const seen = [];
        for (const nm of names) {
          const it = items.find(e => t(e.querySelector('.geek-name, .name')) === nm || t(e).split(' ').includes(nm));
          if (it) seen.push({ name: nm, item: t(it).slice(0, 120) });
        }
        const l = document.querySelector('.user-list');
        if (!l) return { seen, done: 'nolist', h: 0 };
        const max = l.scrollHeight - l.clientHeight;
        if (l.scrollTop >= max - 4) return { seen, done: (max < 300 && items.length < 8) ? 'wait' : 'bottom', h: l.scrollHeight };
        l.scrollTop = Math.min(max, l.scrollTop + 300);
        return { seen, done: 'scrolling', h: l.scrollHeight };
      }, NAMES);
      for (const s of r.seen) present[s.name] = s.item;
      if (r.done === 'nolist') break;
      if (r.done === 'bottom') {
        if (r.h === lastH1) { if (++stall1 >= 4) break; } else { stall1 = 0; lastH1 = r.h; }
        await page.waitForTimeout(2000);   // wait for "load more" to append older conversations
        continue;
      }
      if (r.done === 'wait') { await page.waitForTimeout(2000); continue; }
      await page.waitForTimeout(420);
    }
    res.presentInList = present;
    flush();

    if (!DRY) fs.mkdirSync(OUTDIR, { recursive: true });

    for (const nm of NAMES) {
      const rec = { name: nm, found: false, inList: !!present[nm] };
      if (!present[nm]) { rec.error = 'not_in_list'; res.items.push(rec); flush(); continue; }

      let found = false;
      await page.evaluate(() => { const l = document.querySelector('.user-list'); if (l) l.scrollTop = 0; });
      await page.waitForTimeout(700);
      let lastH2 = -1, stall2 = 0;
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
          if (r.h === lastH2) { if (++stall2 >= 4) break; } else { stall2 = 0; lastH2 = r.h; }
          await page.waitForTimeout(2000);
        }
        else await page.waitForTimeout(r.a === 'wait' ? 2000 : 600);
      }
      rec.found = found;
      if (!found) { rec.error = 'list_item_not_found'; res.items.push(rec); flush(); continue; }
      await page.waitForTimeout(2600);

      const info = await page.evaluate(PROBE);
      Object.assign(rec, info);
      if (info.header.indexOf(nm) < 0) { rec.error = 'header_mismatch'; res.items.push(rec); flush(); continue; }
      if (!info.attachEntries) { rec.error = 'no_attachment_resume'; res.items.push(rec); flush(); continue; }
      if (DRY) { res.items.push(rec); flush(); continue; }

      // ---- download ----
      try {
        const respP = page.waitForResponse(r => /preview4boss/i.test(r.url()) || /application\/pdf/i.test(r.headers()['content-type'] || ''), { timeout: 30000 }).catch(() => null);
        // 就地点击（避免 Playwright 可见性等待：Boss 会重渲染会话区，元素挂 id 后会失效）
        const mark = await page.evaluate(() => {
          const leaf = [...document.querySelectorAll('.chat-message-list *')]
            .filter(e => e.children.length === 0 && (e.innerText || '').indexOf('点击预览附件简历') >= 0);
          if (!leaf.length) return null;
          const el = leaf[leaf.length - 1];
          let n = el;
          for (let i = 0; i < 4 && n; i++) {
            if (n.tagName === 'A' || n.tagName === 'BUTTON' || /btn|link/i.test(String(n.className))) break;
            n = n.parentElement;
          }
          const tgt = n || el;
          const r = el.getBoundingClientRect();
          tgt.click();
          return { tag: tgt.tagName, cls: String(tgt.className).slice(0, 60), w: Math.round(r.width), h: Math.round(r.height) };
        });
        if (!mark) { rec.error = 'attach_leaf_disappeared'; res.items.push(rec); flush(); continue; }
        rec.clickInfo = mark;
        const resp = await respP;
        rec.url = resp ? resp.url() : null;
        rec.contentType = resp ? (resp.headers()['content-type'] || '') : null;
        let buf = null;
        let pdfUrl = null;
        const mm = /[?&]url=([^&]+)/.exec((resp && resp.url()) || '');
        if (mm) { try { pdfUrl = decodeURIComponent(mm[1]); } catch (e) {} }
        if (pdfUrl && pdfUrl.charAt(0) === '/') pdfUrl = 'https://www.zhipin.com' + pdfUrl;
        if (pdfUrl) {
          rec.pdfUrlHead = pdfUrl.slice(0, 120);
          const got = await page.evaluate(async (u) => {
            try {
              const r = await fetch(u, { credentials: 'include' });
              if (!r.ok) return { err: 'http_' + r.status };
              const ab = await r.arrayBuffer();
              const bytes = new Uint8Array(ab);
              let bin = ''; const CH = 0x8000;
              for (let i = 0; i < bytes.length; i += CH) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + CH));
              return { b64: btoa(bin), type: r.headers.get('content-type') || '', len: bytes.length };
            } catch (e) { return { err: String((e && e.message) || e).slice(0, 120) }; }
          }, pdfUrl).catch(e => ({ err: String((e && e.message) || e).slice(0, 120) }));
          rec.fetchType = got && got.type; rec.fetchErr = got && got.err; rec.fetchLen = got && got.len;
          if (got && got.b64) { try { buf = Buffer.from(got.b64, 'base64'); } catch (e) {} }
        }
        if (!buf || buf.length < 1000 || buf.slice(0, 5).toString('latin1') !== '%PDF-') {
          // fallback: inject <a download> into the page and catch the browser download event
          try {
            const dlP = page.waitForEvent('download', { timeout: 20000 }).catch(() => null);
            if (pdfUrl) await page.evaluate((u) => {
              const a = document.createElement('a'); a.href = u; a.download = ''; a.style.display = 'none';
              document.body.appendChild(a); a.click();
            }, pdfUrl);
            const dl = await dlP;
            if (dl) { const tmp = path.join(OUTDIR, 'tmp_' + Date.now() + '.pdf'); await dl.saveAs(tmp); buf = fs.readFileSync(tmp); fs.unlinkSync(tmp); }
          } catch (e) { rec.dlErr = String((e && e.message) || e).slice(0, 120); }
        }
        if (!buf || buf.length < 1000 || buf.slice(0, 5).toString('latin1') !== '%PDF-') {
          rec.error = 'body_not_pdf';
        } else {
          const base = (info.pdfs && info.pdfs.length) ? safeName(info.pdfs[info.pdfs.length - 1]) : ('简历_' + nm + '.pdf');
          let fname = stampU() + '_' + base;             // e.g. 2026_09_27_张三.pdf
          let target = path.join(OUTDIR, fname);
          for (let i = 2; fs.existsSync(target); i++) {  // never overwrite an existing file
            fname = stampU() + '_' + i + '_' + base;
            target = path.join(OUTDIR, fname);
          }
          fs.writeFileSync(target, buf);
          rec.saved = target;
          rec.bytes = buf.length;
          rec.ok = true;
        }
      } catch (e) {
        rec.error = String((e && e.message) || e).slice(0, 160);
      }
      // reset preview overlay (hide only — no control clicks)
      await page.evaluate(() => {
        document.querySelectorAll('iframe').forEach(f => {
          const w = f.closest('.boss-popup__wrapper') || f.closest('div[class*="dialog"]') || f.parentElement;
          if (w) w.style.display = 'none';
        });
        document.querySelectorAll('.boss-popup__wrapper').forEach(w => { if (w.querySelector('iframe')) w.style.display = 'none'; });
      });
      await page.waitForTimeout(1200);
      res.items.push(rec); flush();
      await page.waitForTimeout(1800);
    }
  } catch (e) { res.error = String((e && e.message) || e).slice(0, 400); flush(); }
  console.log('DL_DONE ' + JSON.stringify(res.items.map(i => ({ n: i.name, f: i.found, att: i.attachEntries, pdfs: i.pdfs, ok: !!i.ok, bytes: i.bytes, err: i.error || '' }))));
  try { if (ctx) await ctx.close(); } catch (e) {}
})();
