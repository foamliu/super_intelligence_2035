# cq860 深读笔记 — dlyg 网表批量插电阻脚本

## trace_source
- session_file: 1789993024776_cq860.messages.json
- user: thomasz · host: 10.129.2.11 · mc=44
- domain: schematic_netlist (keywords: netlist:66 .cdl:30 .spf_RC schematic)
- 50 msgs, 4 user_input turns

## 用户轮逐字
- **U#0** (preamble): "现在读取/proj/ddgoa/V0/simdir/finesim/workdir/thomasz/260921_Klib/netlists/ 我将给你提出脚本需求"
- **U#9** ★ (唯一 A-faithful produce-task, 逐字):
  > 现在需要你把代码写入test.py，具体功能是，对于当前路径下的所有文件，捕捉dlyg开头的文件作为待处理对象，其他文件不处理。对于dlyg开头的文件，如果是软链接，先把他copy到本地，删去软链接。然后对这些文件按规则处理：以dlyg2s2a.spf_RC为例子，将
  > R_mid mid mid_sw 0.001
  > R_out out out_sw 0.001
  > 这两行加到文件中去。加入的位置是.ends  dlyg2s2a 这行之前。注意大小写不敏感，以及.ends可能是.end。
  > 待处理的文件名有三种格式，以.spf_RC或.cdl.spf或.cdl为后缀，以dlyg2s2a这种为cell名字。
  > 脚本执行后，打印处理了多少个文件以及运行时间
- **U#27** (refinement 非 produce): "很好，功能实现了，现在把脚本里的所有中文注释都换成英文"
- **U#48** (trivial): "帮我取个脚本名字吧，结合实现的功能"

判定：U#9 纯提需求，未给根因/修复 → **A-faithful**。U#27/U#48 是细化/收尾，不作 task 说明。

## agent 工具链
list_allowed_files → read_files(5 文件) → get_agent_policy_status → editor 写 test.py（policy-engine 限制 writableRoots，最终写到 /home/thomasz/.cline/scripts/data/test.py）→ 多轮 editor 把中文注释换英文 → read_files 核验。

## 真实产物（agent 最终 test.py，英文版）
```python
LINES_TO_INSERT = ["R_mid mid mid_sw 0.001\n", "R_out out out_sw 0.001\n"]
END_PATTERN = re.compile(r"^\s*\.ends?\b", re.IGNORECASE)

def replace_symlink_with_real_file(path):
    if not os.path.islink(path): return
    target = os.path.realpath(path)
    with open(target, ...) as f: data = f.read()
    os.unlink(path)
    with open(path, "w") as f: f.write(data)

def process_file(path):
    lines = f.readlines()
    end_index = None
    for i, line in enumerate(lines):
        if END_PATTERN.match(line): end_index = i   # LAST match = top-level
    if end_index is None: return False
    new_lines = lines[:end_index] + list(LINES_TO_INSERT) + lines[end_index:]
    f.writelines(new_lines); return True

def main():
    directory = os.path.dirname(os.path.abspath(__file__))
    for name in sorted(os.listdir(directory)):
        if not name.startswith("dlyg"): continue
        path = os.path.join(directory, name)
        if not (os.path.isfile(path) or os.path.islink(path)): continue
        replace_symlink_with_real_file(path)
        if process_file(path): processed += 1
    print("Processed {} file(s) in {:.3f}s".format(processed, elapsed))
```

## 合成策略（B-grade synthesized）
真实 /proj 网表不可附加 → B-grade 参数化生成 A/B/B2 三套目录。
**核心难度轴**：
1. **last .ends/.end 匹配**（顶层 vs 子电路 .ENDS）— naive 取首个会错插到子电路结束前
2. **大小写不敏感** — .ENDS/.End/.end 都要识别
3. **三种后缀过滤** — .spf_RC / .cdl.spf / .cdl（endswith 任一）
4. **软链接转实体** — read target → write local → unlink
5. **数据驱动反硬编码** — prompt 贴 A 的 dlyg/R_mid/R_out，task_brief 要求读 config.json；B/B2 不同 prefix/lines/suffixes 测泛化

**A**：prefix=dlyg, lines=[R_mid mid mid_sw 0.001, R_out out out_sw 0.001], suffixes=[.spf_RC,.cdl.spf,.cdl]
**B** (hidden)：prefix=invgx, lines=[C_load out out_gnd 1e-12, R_drv in in_sw 50], suffixes=[.spf_RC,.cdl,.spi]
**B2** (hidden)：prefix=ampz, lines=[L_match mid mid_sw 1e-9], suffixes=[.cdl.spf,.spf_RC]

## 金标 dlyg_insert_res_ref.py
CLI `<config.json> <directory>`：load_config → 遍历 sorted(listdir) → 过滤 prefix+suffix+isfile/islink → replace_symlink_with_real_file → process_file(last .ends? IGNORECASE, insert lines before) → print "Processed N file(s) in X.XXXs"。

## check.py 条件清单（16 条 a-p）
a zip 含 .py 无禁 import + 无硬编码 /proj /rundata /home 路径
b py_compile 通过
c B run exit0 + 非空 stdout
d stdout 含 "Processed" + 数字 + "s" 运行时间格式
e B 所有 invgx+匹配后缀文件被插入 2 行；非匹配（README/test.py/错后缀）未动
f B 软链接被转实体（不再是 link，内容==原 target 内容）
g 插入行在最后一个 .ends/.end 行**之前**（位置正确）
h 每文件仅 1 处插入块（最后一个 .ends 前），中间子电路 .ENDS 前不插
i 大小写不敏感：.ENDS / .End / .end 全识别（B 含混合大小写）
j .ends 后 cell 名保留（如 ".ENDS invgx2b" 整行保留，插入在其前）
k 反硬编码 A：A-config 重跑产 R_mid/R_out + dlyg，且源码无 B 特有名（invgx/C_load/1e-12/out_gnd）
l 跨输入 B2：B2-config 产 L_match + ampz，源码无 B2 特有名（ampz/L_match/1e-9）
m CLI sys.argv/argparse 接 config+directory；缺参报错；无硬编码 config 路径
n 确定性 3 次重跑 sha256 一致
o 后缀过滤：prefix 匹配但后缀错（如 invgx2b.txt）不被处理；正确后缀被处理
p .end（非 .ends）变体识别（B 含 .end 行，插入在其前）

## negatives（≥8）
empty_shell / syntax_err / no_output / print_expected_B / hardcode_a（只硬编码 dlyg+R_mid，B 上 0 处理）/ first_ends_only（插首个 .ends 前非末个）/ no_symlink_handle / no_suffix_filter / case_sensitive（无 IGNORECASE）/ wrong_position（插 .ends 之后）/ ref_core_deleted / no_cli / nondeterministic
