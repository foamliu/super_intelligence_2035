s = open('designflow/_tmp/next_awk.sh').read()
idxs = [i for i, c in enumerate(s) if c == chr(39)]
prog = s[idxs[2] + 1:idxs[3]]
# unescape bash doubled backslashes for awk -f file context
prog = prog.replace('\\.', '.').replace('\\t', '\t')  # placeholder, fix below
# Actually we want \\. -> \. ; do it char-wise
prog = s[idxs[2] + 1:idxs[3]]
out = []
i = 0
while i < len(prog):
    if prog[i] == '\\' and i + 1 < len(prog) and prog[i + 1] == '\\':
        out.append('\\')
        i += 2
    else:
        out.append(prog[i])
        i += 1
prog = ''.join(out)
open('designflow/_tmp/next_program.awk', 'w').write(prog)
print('PROG_LEN', len(prog))
print(repr(prog[:120]))
print(repr(prog[-80:]))
