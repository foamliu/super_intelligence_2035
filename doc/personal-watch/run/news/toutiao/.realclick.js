(async () => {
  const [x, y] = [__X__, __Y__];
  const el = document.elementFromPoint(x, y);
  const info = { x, y, tag: el && el.tagName, cls: el && String(el.className), t: el && (el.innerText || '').trim() };
  for (const type of ['mouseover', 'mousedown', 'mouseup', 'click']) {
    el.dispatchEvent(new MouseEvent(type, { bubbles: true, cancelable: true, clientX: x, clientY: y, button: 0, view: window }));
    await new Promise((r) => setTimeout(r, 60));
  }
  await new Promise((r) => setTimeout(r, 2500));
  const ta = document.querySelector('.comment-textarea');
  const items = [...document.querySelectorAll('.ttp-comment-item')].slice(0, 2).map((n) => n.innerText.replace(/\s+/g, ' ').slice(0, 90));
  return JSON.stringify({ info, left: ta ? (ta.value || ta.innerText || '').trim().length : -1, items });
})()
