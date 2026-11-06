# 深读笔记 — 1789708302199_on45q (bensonh@10.129.8.236, mc=49, netlist:146 .cdl:1)

**选料**：fresh_D306_pool.tsv peek rank 166-185（peek_D313.py 经 .75 ssh 并发 20 候选）。逐条审 20 候选：cmr7h=mid-conv 调试「你说得对，我不再创新了」(诊断非 produce)·9imo1/erhym/wzpd1=ssh EXC·epctt=NOFILE·4auih=代码改善+根因「时间对不上」(诊断)·6vy3t=报错粘贴诊断·brrc3/3qe6x=读项目讲流程 Q&A·y6ito=「加载了哪些 Skill」Q&A·3kgd5=用户给修复「移除 PostInstanceEditDialog」(非 A-faithful)·2gxuy=how-to 打开 vscode·8rxb1=高亮 net (L2 virtuoso skill 依赖)·6i68m=Spice_Agent skill·xyw6o=how-to Aether LE·1lote=GUI CMP 操作·1nuuf=「你可以对比电路网表吗」模糊提问·vg3v4=GUI 启动·8nqgg=vam-agent skill。**唯一 clean A-faithful produce-task = on45q**★(bensonh)。

## trace 概况
- 42 msgs, 1 真实 user produce-turn (U#0, 重复为 U#1 — 同内容)。
- agent 受 policy-engine 约束（禁 raw shell / 禁动态 python，仅 hello_world profile 且 owner mismatch 拒绝）→ 只能 edit 文件，不能实跑验证。逐块 edit 建 `/home/bensonh/Desktop/rename_netlist_signals.py`（200 行）。
- U#40/U#41 = 无关新需求（XMMN 网表平均电流法），非本轮 produce 任务，忽略。

## U#0 逐字（A-faithful 任务说明，唯一真实 user_input）
```
写一个脚本，将网表文件中名字为RdEnL
EqIoL
RwEnNL
WrEnL
SapEnAmid
SapEnBmid
SanEnAmid
SanEnBmid
SapEnCmid
PreEqL
IsoL_E
OcEnL_E
SelL
EqMsamid
SanEnCmid
PCSL
NCSL
的信号名全部替换为RdEn

EqIo
RwEnN
WrEn
SapEnA
SapEnB
SanEnA
SanEnB
SapEnC
PreEq


Iso


OcEn


Sel


EqMsa
SanEnC
PCS


NCS


，然后将修改后的文件重新命名为原文件名+.prcsim，要求精确匹配，例如RdEnL
```
- 纯提需求（写脚本），未给根因/修复 → A-faithful ✓
- "要求精确匹配，例如RdEnL" = 整词匹配约束（example RdEnL 为首个映射）

## 真实 agent 产物（rename_netlist_signals.py 关键设计）
- **17 对映射 REPLACEMENTS dict**（A 映射，后缀模式 L/mid/_E）：
  RdEnL→RdEn · EqIoL→EqIo · RwEnNL→RwEnN · WrEnL→WrEn · SapEnAmid→SapEnA · SapEnBmid→SapEnB · SanEnAmid→SanEnA · SanEnBmid→SanEnB · SapEnCmid→SapEnC · PreEqL→PreEq · IsoL_E→Iso · OcEnL_E→OcEn · SelL→Sel · EqMsamid→EqMsa · SanEnCmid→SanEnC · PCSL→PCS · NCSL→NCS
- **整词边界正则**：`(?<![A-Za-z0-9_])(?:LONGEST_FIRST_ALT)(?![A-Za-z0-9_<[(])`
  - 前面非 word char（避免 xRdEnL / foo_RdEnL）
  - 后面非 word char 且非位选开头 `<[(`（避免 RdEnL<1> → RdEn<1>）
  - 故 `RdEnL<1>` / `RdEnL[3:0]` / `RdEnL(0)` / `RdEnLfoo` / `xRdEnL` 全保留不变
- **process_file(input, output=None)**：读全文 subn，默认输出 `input + ".prcsim"`，返回 (out, count)
- **transform(text)**：供 selftest
- **selftest()**：27 用例（17 映射 + 边界不变 + 混合行）
- **main()**：argparse，files nargs=*，-o/--output，--selftest；-o 需恰好 1 文件；无文件报错；打印 `<path> -> <out> (N replacement(s))`；exit 0
- 注意：真实脚本映射**硬编码在源码**（dict 字面量），非数据驱动。

## 合成策略（B-grade synthesized）
真实 /home/bensonh 网表文件未附加（trace 内无附件）→ B-grade 合成。
**核心难度点**：(1) 整词精确匹配（位选/前缀/后缀边界）—— naive str.replace 必败；(2) 数据驱动 —— prompt 把 A 映射贴在正文里（诱使硬编码），但 task_brief 要求脚本从 mapping.tsv 读映射，B/B2 用不同映射测泛化。

**金标 `rename_signals_ref.py`**（CLI `<netlist> <mapping.tsv> [-o out]`）：
- load_mapping：跳 `#` 注释/空行，`old<TAB>new` 解析
- build_pattern：`(?<![A-Za-z0-9_])(?:len-desc alt)(?![A-Za-z0-9_<[(])`（同真实 agent 边界规则）
- process_file：默认输出 `<netlist>.prcsim`，打印 `path -> out (N replacement(s))`
- argparse：netlist + mapping 位置参，-o 可选

**A**（SUT 看）：prompt.txt(U#0 逐字) + task_brief.md(3 行接口) + mapping_A.tsv(17 真实对) + netlist_A.sp(含 17 信号整词 + 位选 RdEnL<1> + 前缀 xRdEnL + 后缀 RdEnLfoo + 非目标 clk/vdd + 混合行 + 注释行)
**B**（hidden 主判）：mapping_B.tsv(14 对 DRAM bank 域：BankAddrMid→BankAddr/RowSelL→RowSel/...，含 # 注释+空行) + netlist_B.sp(不同拓扑，含位选 BankAddrMid<7:0> + 前缀 xBankAddrMid + 后缀 ColEnLxyz + 非目标 dqs_p + 混合行)
**B2**（hidden 跨输入）：mapping_B2.tsv(12 对 clock/PLL 域：ClkBufL→ClkBuf/PllVcoL→PllVco/...，后缀 L/PL/mid) + netlist_B2.sp(时钟树拓扑)
**反硬编码三轴**：信号名不相交(A=RdEn*/B=BankAddr*/B2=ClkBuf*) + 后缀模式组合不同 + 映射规模不同(17/14/12)。
**特有名集不相交**：A={RdEnL,EqIoL,SapEnAmid,IsoL_E,...} B={BankAddrMid,RowSelL,DataBit_E,ColEnL,...} B2={ClkBufL,PllVcoL,DivNMid,ClkGatePL,...}。

## check.py 16 条件 a-p
a zip 含 rename_signals.py 无禁 import/引用/泄漏路径 · b py_compile · c B 运行 exit0+写 netlist_B.sp.prcsim · d 输出非空 · e B 旧名 BankAddrMid 整词归零+新名 BankAddr 出现 · f 位选 BankAddrMid<7:0> 原样保留 · g 前缀 xBankAddrMid 保留 · h 后缀 ColEnLxyz 保留 · i 非目标 dqs_p 整词计数不变 · j B 替换计数==金标(含#注释/空行跳过) · k 反硬编码 A：A 重跑 RdEnL→RdEn+源码无 A 特有名 · l 跨输入 B2：ClkBufL→ClkBuf+ClkBufL<3> 保留+源码无 B2 特有名 · m -o 自定义输出 · n 确定性 3 次 sha256 · o CLI argparse/sys.argv+缺参报错+无硬编码路径 · p 混合行 RowSelL+wl 仅替换 RowSelL

## negatives（10）
empty_shell(b)·syntax_err(b)·no_output(c,d)·print_expected_B(j,k,l,m)·hardcode_a(e,j,k,l)·substring_replace(f,g,h,j)·wrong_boundary(f,j)·ref_core_deleted(e,j)·no_cli(k,l,m,o)·always_copy(e,j)·nondeterministic(n)
§4.9 三假{empty_shell,print_expected_B,ref_core_deleted}全 FAIL。
