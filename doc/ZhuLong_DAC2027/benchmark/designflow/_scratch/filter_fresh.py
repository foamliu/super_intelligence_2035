import re, sys

# Build exclusion set from all 4 shards + allexcl
excl=set()
for f in ['A','B','C','D']:
  for line in open(f'designflow/trace_ledger_{f}.tsv'):
    parts=line.split('\t')
    if len(parts)>0 and parts[0]:
      s=re.sub(r'\.(messages\.)?json$','',parts[0].strip())
      if s: excl.add(s)
for line in open('designflow/trace_ledger_allexcl_tmp.tsv'):
    s=line.strip()
    if s: excl.add(re.sub(r'\.(messages\.)?json$','',s))

# C case users (to flag seen users)
c_users=set()
for line in open('designflow/trace_ledger_C.tsv'):
  parts=line.split('\t')
  if len(parts)>5 and parts[5]=='case' and parts[1]:
    c_users.add(parts[1].strip())

# Read candidate file passed as arg
cands_file = sys.argv[1]
fresh=[]
for line in open(cands_file):
  line=line.rstrip('\n')
  if not line: continue
  parts=line.split('\t')
  if len(parts)<5: continue
  mc,session,user,host,kw = parts[0],parts[1],parts[2],parts[3],parts[4]
  sid=re.sub(r'\.(messages\.)?json$','',session)
  if sid in excl: continue
  # classify domain by keywords
  kws=kw.lower()
  if 'virtuoso' in kws and ('drc' in kws or 'calibre' in kws or 'lvs' in kws or '.gds' in kws):
    dom='layout_virtuoso'
  elif 'aether' in kws or 'pyaether' in kws:
    dom='layout_aether'
  elif 'calibre' in kws or 'lvs' in kws or 'drc' in kws or 'pex' in kws:
    dom='physical_verify'
  elif 'dbcreaterect' in kws or 'dbcreatepolygon' in kws or 'virtuoso' in kws:
    dom='layout_virtuoso'
  else:
    dom='physical_verify'
  seen = user in c_users
  fresh.append((int(mc),sid,user,host,dom,seen,kw))

print(f"excl={len(excl)} c_users={len(c_users)} fresh={len(fresh)}")
# Sort by mc desc, prefer new users first within similar mc
fresh.sort(key=lambda x:(-x[0], x[5]))
print("=== TOP 25 FRESH (new-user first within mc tier) ===")
for mc,sid,user,host,dom,seen,kw in fresh[:25]:
  flag = "[seen_user]" if seen else "[NEW_USER]"
  print(f"{mc}\t{sid}\t{user}\t{host}\t{dom}\t{flag}\t{kw[:80]}")
