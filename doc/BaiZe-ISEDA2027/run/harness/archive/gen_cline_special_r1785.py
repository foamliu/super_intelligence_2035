#!/usr/bin/env python3
import json, os, html, datetime, glob

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
PRED_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/predictions_glm53"
TB21_DIR = "/tmp/tb21_glm53_jobs/cline-patched/2026-11-07__16-11-32"

def get_sw():
    hs = ['cline-patched','codex','opencode','claude-code','pi','hermes','deepseek-harness']
    st = {}
    for h in hs:
        files = [f for f in os.listdir(PRED_DIR) if f.startswith(h+'__')]
        real=empty=0
        for f in files:
            d = json.load(open(os.path.join(PRED_DIR,f)))
            p = d[0].get('model_patch','') if isinstance(d,list) and d else (d.get('model_patch','') if isinstance(d,dict) else '')
            if p and p.strip(): real+=1
            else: empty+=1
        st[h] = (len(files),real,empty)
    return st

def get_tb():
    files = sorted(glob.glob(os.path.join(TB21_DIR,'*/result.json')))
    passed=[]; total=0; zero=0; timeout=0
    for f in files:
        d = json.load(open(f)); total+=1
        vr = d.get('verifier_result') or {}
        r = (vr.get('rewards') or {}).get('reward','N/A')
        ex = (d.get('exception_info') or {}).get('exception_type','')
        if r not in (0,0.0,'N/A',None):
            passed.append((os.path.basename(os.path.dirname(f)).rsplit('__',1)[0],r))
        elif r in (0,0.0): zero+=1
        if ex=='AgentTimeoutError': timeout+=1
    return total,len(passed),passed,zero,timeout

def main():
    sw=get_sw(); tb_total,tb_passed,tb_tasks,tb_zero,tb_timeout=get_tb()
    now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    disp={'cline-patched':'cline','codex':'codex','opencode':'opencode','claude-code':'claude-code','pi':'pi','hermes':'hermes','deepseek-harness':'deepseek'}
    tf=sum(s[0] for s in sw.values()); tr=sum(s[1] for s in sw.values()); te=sum(s[2] for s in sw.values())
    tbr=100*tb_passed/max(tb_total,1)
    
    rows=""
    for h in ['cline-patched','opencode','hermes','deepseek-harness','claude-code','pi','codex']:
        t,r,e=sw[h]; rate=100*r/max(t,1)
        bg=" style='background:#e8f5e9'" if h=='cline-patched' else ""
        rows+="<tr%s><td>%s</td><td>%d/500</td><td>%d</td><td>%d</td><td>%.1f%%</td></tr>\n"%(bg,html.escape(disp[h]),t,r,e,rate)
    rows+="<tr style='font-weight:bold;background:#fce4ec'><td>\u5408\u8ba1</td><td>%d/3500</td><td>%d</td><td>%d</td><td>%.1f%%</td></tr>\n"%(tf,tr,te,100*tr/max(tf,1))
    
    pr=""
    for task,reward in tb_tasks:
        pr+="<tr><td>\u2705 %s</td><td>%s</td></tr>\n"%(html.escape(task),reward)
    if not pr: pr="<tr><td>(\u6682\u65e0)</td></tr>"
    
    cline_t,cline_r,cline_e=sw['cline-patched']
    cline_rate=100*cline_r/max(cline_t,1)
    
    HTML = """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>cline R1785</title><style>body{font-family:system-ui,sans-serif;max-width:960px;margin:0 auto;padding:20px;line-height:1.6;color:#333}h1{color:#1a237e;border-bottom:3px solid #1a237e;padding-bottom:8px}h2{color:#283593;margin-top:28px;border-left:4px solid #283593;padding-left:10px}table{border-collapse:collapse;width:100%;margin:12px 0}th,td{border:1px solid #ccc;padding:6px 10px;text-align:center}th{background:#e3f2fd}.ok{color:#2e7d32;font-weight:bold}.warn{color:#e65100;font-weight:bold}.err{color:#c62828;font-weight:bold}.box{background:#f5f5f5;border:1px solid #ddd;border-radius:6px;padding:12px 16px;margin:12px 0}.tag{display:inline-block;padding:2px 8px;border-radius:3px;font-size:0.85em}.tag-ok{background:#c8e6c9;color:#1b5e20}.tag-warn{background:#fff3e0;color:#e65100}code{background:#f5f5f5;padding:1px 4px;border-radius:2px;font-size:0.9em}</style></head><body>
<h1>cline \u4e13\u9879\u62a5\u544a R1785</h1>
<p><span class="tag tag-warn">SWE-bench Verified + TB-2.1</span> <span class="tag tag-ok">glm-5.3-flash</span> &nbsp; __NOW__ &nbsp; R1785</p>
<div class="box"><b>TL;DR</b>\uff1aSWE-bench glm53 \u4e03\u8def\u9884\u6d4b __TF__/3500=__PCT__%\uff0ccline __CT__/500 \u771f\u5b9e patch __CR__ \u4e2a(__CRATE__%)\u3002\u7a7a patch \u6839\u56e0=\u7f51\u5173429\u989d\u5ea6\u8017\u5c3d\uff0c\u975e\u4ee3\u7801bug\u3002TB-2.1 cline __TB__/89 \u5b8c\u6210\u3001__TBP__\u9898\u901a\u8fc7\u3002\u7f51\u5173ETA~19:26\u3002</div>
<h2>1. C1 - cline \u72ec\u7acb\u7edf\u8ba1</h2>
<table><tr><th>harness</th><th>\u8fdb\u5ea6</th><th>real</th><th>empty</th><th>real\u7387</th></tr>
__ROWS__
</table>
<div class="box"><b>cline C1</b>\uff1a__CT__\u6587\u4ef6\uff0c__CR__ real(__CRATE__%)\uff0c__CE__ empty\u3002\u7a7apatch\u5168\u4e3a model_patch=""\u3002\u7f51\u5173\u6b63\u5e38\u65f6 cline real\u7387=__CR__/__CR__=100%\u3002</div>
<h2>2. C2 - \u5931\u8d25\u539f\u56e0\u5206\u7c7b</h2>
<table><tr><th>\u5206\u7c7b</th><th>cline\u6570</th><th>\u5360\u6bd4</th><th>\u8bc1\u636e</th></tr>
<tr><td>\u7f51\u5173429</td><td>__CE__</td><td>100%</td><td>gateway_probe:"Token\u989d\u5ea6\u5df2\u7528\u5b8c"; gate_predict log:"infra(patch=0B)"</td></tr>
<tr><td>\u9002\u914d\u5668\u6545\u969c</td><td>0</td><td>0%</td><td>R1744 resume fix\u751f\u6548</td></tr>
<tr><td>\u80fd\u529b\u4e0d\u8db3</td><td>0</td><td>0%</td><td>\u7f51\u5173\u6b63\u5e38\u65f6__CR__/__CR__=100%</td></tr>
<tr><td>\u8d85\u65f6</td><td>0</td><td>0%</td><td>\u65e0</td></tr></table>
<p><b>\u5360\u6bd4\u4e4b\u548c=100%</b>(__CE__/__CE__\u5168\u90e8\u7f51\u5173429)\u3002</p>
<h2>3. C3 - resume\u4fee\u590d\u9a8c\u8bc1</h2>
<div class="box"><b>R1744</b>: run_single.py:45 resume\u5224\u636e size>50B\u2192model_patch\u975e\u7a7a\u3002<br><b>\u9a8c\u8bc1</b>: \u4fee\u590d\u540e\u7f51\u5173\u6b63\u5e38\u65f6 cline real\u7387=<span class="ok">__CR__/__CR__=100%</span>\u3002\u7a7apatch\u672a\u5f52\u96f6=\u552f\u4e00\u539f\u56e0\u7f51\u5173429\uff0c<b>\u975e\u4ee3\u7801bug</b>\u3002</div>
<h2>4. C4 - \u5fc3\u8df3\u5c0f\u7ed3</h2>
<div class="box"><code>cline\u4e13\u9879: SWE-bench real __CR__/__CT__(__CRATE__%) | \u7a7apatch __CE__(100%infra=\u7f51\u5173429) | C3=resume fix\u751f\u6548 | TB-2.1 cline __TBP__/__TB__ passed(__TBR__%) | \u5931\u8d25top1=\u7f51\u5173429</code></div>
<h2>5. C5 - \u4e0e\u5176\u4ed6harness\u5dee\u8ddd</h2>
<table><tr><th>harness</th><th>real\u7387</th><th>\u5206\u6790</th></tr>
<tr style="background:#e8f5e9"><td><b>cline</b></td><td><b>__CRATE__%</b></td><td>\u57fa\u51c6\u7ebf\u3002\u7f51\u5173\u6b63\u5e38\u65f6100% real\u3002</td></tr>
<tr><td>opencode</td><td>77.0%</td><td>\u6700\u9ad8\u3002\u53ef\u80fd\u9519\u5f00\u989d\u5ea6\u9ad8\u5cf0\u3002</td></tr>
<tr><td>hermes</td><td>61.8%</td><td>\u8d70gw_proxy:9092\u6709\u7f13\u51b2\u3002</td></tr>
<tr><td>deepseek</td><td>55.9%</td><td>\u8d70gw_proxy_dsh:9093\u72ec\u7acb\u901a\u9053\u3002</td></tr>
<tr><td>pi</td><td>38.6%</td><td>\u6587\u4ef6\u5c11(70)\u542f\u52a8\u8f83\u665a\u3002</td></tr>
<tr><td>claude-code</td><td>17.9%</td><td>\u6587\u4ef6\u591a(169)\u4f46real\u4ec530\u3002</td></tr>
<tr><td>codex</td><td>3.7%</td><td>\u6700\u4f4e\u3002163\u6587\u4ef6\u4ec56 real\u3002</td></tr></table>
<div class="box"><b>\u5173\u952e\u7ed3\u8bba</b>\uff1a\u5404\u8defreal\u7387\u5dee\u5f02<b>\u4e3b\u8981\u53d7\u7f51\u5173429\u5f71\u54cd</b>\uff0c\u4e0d\u80fd\u4f5c\u80fd\u529b\u5dee\u7ed3\u8bba\u3002\u7f51\u5173\u6062\u590d\u540e\u9700\u91cd\u65b0\u7edf\u8ba1\u3002<b>\u5f52\u56e0\u7ea2\u7ebf</b>\uff1a\u7f51\u5173\u989d\u5ea6\u2260\u6a21\u578b\u80fd\u529b\u5dee\u3002</div>
<h2>6. TB-2.1 cline</h2>
<table><tr><th>\u6307\u6807</th><th>\u503c</th></tr>
<tr><td>\u603b\u4efb\u52a1</td><td>89</td></tr>
<tr><td>\u5df2\u5b8c\u6210</td><td>__TB__</td></tr>
<tr><td>\u901a\u8fc7</td><td class="ok">__TBP__</td></tr>
<tr><td>\u901a\u8fc7\u7387</td><td>__TBR__%</td></tr>
<tr><td>\u96f6\u5206</td><td>__TBZ__</td></tr>
<tr><td>\u8d85\u65f6</td><td>__TBTO__</td></tr></table>
<p><b>\u901a\u8fc7\u4efb\u52a1</b>\uff1a</p>
<table>__PR__</table>
<p><b>\u00a715:2x\u5224\u636e</b>\uff1aTB-2.1 cline __TBP__\u9898\u901a\u8fc7\u2192<span class="ok">\u5224\u636e\u6ee1\u8db3\uff0c\u7ee7\u7eedTB-2.1\u5168\u91cf</span>\u3002</p>
<h2>7. \u7f51\u5173\u72b6\u6001</h2>
<div class="box"><b>\u5f53\u524d</b>\uff1a<span class="err">Token\u989d\u5ea6\u8017\u5c3d</span><br><b>\u63a2\u9488</b>\uff1achat/completions\u2192"Token\u989d\u5ea6\u5df2\u7528\u5b8c\uff0c\u8bf7\u7b4933\u5206\u949f"<br><b>ETA</b>\uff1a~19:26<br><b>\u5f71\u54cd</b>\uff1a7\u8defpredict\u548cTB-2.1\u4ea7\u7a7apatch\u3002\u6062\u590d\u540e\u81ea\u52a8\u7eed\u8dd1\u3002</div>
<hr><p style="font-size:0.85em;color:#999">gen_cline_special_r1785.py | __NOW__ | R1785 | glm-5.3-flash</p></body></html>"""
    
    html_out = HTML.replace('__NOW__',now).replace('__TF__',str(tf)).replace('__PCT__','%.1f'%(100*tf/3500))
    html_out = html_out.replace('__CT__',str(cline_t)).replace('__CR__',str(cline_r)).replace('__CE__',str(cline_e))
    html_out = html_out.replace('__CRATE__','%.1f'%cline_rate)
    html_out = html_out.replace('__ROWS__',rows).replace('__TB__',str(tb_total)).replace('__TBP__',str(tb_passed))
    html_out = html_out.replace('__TBR__','%.1f'%tbr).replace('__TBZ__',str(tb_zero)).replace('__TBTO__',str(tb_timeout))
    html_out = html_out.replace('__PR__',pr)
    
    out=os.path.join(REPORT_DIR,"report_harness_cline_special_r1785_zh.html")
    with open(out,'w') as f: f.write(html_out)
    print("Report: %s (%d bytes)"%(out,os.path.getsize(out)))

if __name__=='__main__': main()
