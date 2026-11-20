(async () => {
  const ta = document.querySelector('.comment-textarea');
  if (!ta) return JSON.stringify({ err: 'no textarea' });
  const box = ta.closest('div[class*="comment"]') || ta.parentElement.parentElement;
  const btns = [...box.querySelectorAll('button,div[role=button],span')]
    .filter((n) => /发布|发送|评论/.test((n.innerText || '').trim()) && (n.innerText || '').trim().length <= 4)
    .map((n) => ({ tag: n.tagName, cls: n.className, t: n.innerText.trim(), dis: n.disabled }));
  const btn = [...box.querySelectorAll('button')].find((n) => /发布|发送/.test(n.innerText));
  if (!btn) return JSON.stringify({ err: 'no button', btns });
  btn.click();
  await new Promise((r) => setTimeout(r, 2500));
  return JSON.stringify({ clicked: btn.innerText.trim(), val: ta.value || ta.innerText, btns });
})()
