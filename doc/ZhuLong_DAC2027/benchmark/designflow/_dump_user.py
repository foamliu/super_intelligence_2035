# -*- coding: utf-8 -*-
import json,sys
path=sys.argv[1]
N=int(sys.argv[2]) if len(sys.argv)>2 else 4
try:
    data=json.load(open(path))
except Exception as e:
    print("ERR json:",e); sys.exit(0)
msgs=data if isinstance(data,list) else data.get("messages",[])
def text_of(c):
    if isinstance(c,str): return c
    if isinstance(c,list):
        out=[]
        for p in c:
            if isinstance(p,dict):
                if "text" in p: out.append(str(p["text"]))
                elif p.get("type")=="text" and "content" in p: out.append(str(p["content"]))
            elif isinstance(p,str): out.append(p)
        return " ".join(out)
    if isinstance(c,dict):
        if "text" in c: return str(c["text"])
        if "content" in c: return text_of(c["content"])
    return str(c)
cnt=0
for m in msgs:
    if not isinstance(m,dict): continue
    msg=m.get("message",m)
    role=msg.get("role") or m.get("role") or m.get("type")
    if role=="user" or role=="say":
        t=text_of(msg.get("content",m.get("text","")))
        t=t.replace("\n"," ")[:300]
        if t.strip():
            cnt+=1
            print("U%d: %s"%(cnt,t))
            if cnt>=N: break
print("# total msgs:",len(msgs))
