# 深读笔记 · yx1e1 (e0045144 @ hfeg0pkn005[10.129.2.14], mc39, digital)

> session: `1794394698715_yx1e1.messages.json` · 49 msgs · 124KB · 3 real user turns
> scp .75→workdir 可读。deliverable=写私有 /home/e0045144/jtag/ACC/run/ → .75 Permission denied → INFEASIBLE → B档合成

## 用户意图与对话流

**U#0（RTL 语法检查 Q&A，不纳入 case）**：用户贴了一段 `xorTstCHaIn xorTstCHaIn_i ( .SI(tstStrucIN1), .SE(SE), .ck1(clk1) `ifndef FPGA , .ck2(clk2) `endif , .rstn(rstn) ... );` 的 Verilog 实例化代码，问「语法有问题吗」。agent 答：**语法合法**——采用前置逗号（leading comma）风格，恰好和 `ifndef/endif` 条件编译配合得好（无论 ck2/SCAN_OUT 是否被编译，前置逗号都能对上），结尾端口无尾逗号 + `);` 也正确。纯 Q&A，无 produce-task。

**U#1（核心 produce-task，本 case 选用）**：「帮我写一个 power iso 的 design」。agent 用 ask_question 澄清，用户选「一个隔离单元（ISO cell）的行为级 RTL 模型（含 enable 保持/取值逻辑）」。

agent 产出（位于 /home/e0045144/jtag/ACC/run/）：
1. **`power_iso.v`** — 三个模块：
   - `power_iso_clamp`（钳位型 ISO_CLAMP）：参数 WIDTH/CLAMP_VAL/ISO_EN_ACTIVE；`wire iso_act = (ISO_EN_ACTIVE==1'b1) ? iso_en : ~iso_en;` + `assign dout = iso_act ? {WIDTH{CLAMP_VAL}} : din;`（隔离生效→输出钳到 WIDTH 位全 CLAMP_VAL，否则透明）。纯组合 assign。
   - `power_iso_keep`（保持型 ISO_KEEP）：参数 WIDTH/INIT_VAL/ISO_EN_ACTIVE；同样的极性 wire；时序 always `@(posedge clk or negedge rstn)`：`if (~rstn) dout <= {WIDTH{INIT_VAL}}; else if (iso_act) dout <= dout; else dout <= din;`（复位→INIT_VAL，隔离→保持，否则→跟随 din）。
   - `power_iso`（顶层选择）：参数 WIDTH/ISO_TYPE(默认"CLAMP")/CLAMP_VAL/INIT_VAL/ISO_EN_ACTIVE；用 `generate` 块按 `ISO_TYPE=="KEEP"` 切换：KEEP 例化 `power_iso_keep`（g_keep 分支），否则例化 `power_iso_clamp`（g_clamp 分支）。
2. **`tb_power_iso.v`** — testbench（验证 CLAMP/KEEP 两种隔离语义 + 使能极性）。
3. **`verify_model.py`** — Python 行为级自校验器，镜像 RTL 逻辑：`clamp_iso(iso_en,din,clamp_val,den_actual,active,width)` + `keep_iso(iso_en,din,cur,active)` + 11 个 check。**关键 bug 修复**：初版 clamp_iso 忘记像 RTL 的 `{WIDTH{CLAMP_VAL}}` 那样把 clamp_val 复制到全位宽（clamp_val=1 时只返回 1 而非 (1<<width)-1）→ 修为 `mask=(1<<width)-1; return mask if clamp_val else 0`。修复后 11 check 全 PASS（`ALL TESTS PASSED`）。

agent 还尝试用 iverilog 编译运行 testbench，但环境无 iverilog → 改用 Python 行为模型验证。最后清理了 iverilog 探测脚本，修正了 power_iso.v 头部一条误导注释（删掉未实现的 "HALF" 模式描述）。

**U#2（后续 Q&A，不纳入 case）**：「/proj/lacaa/.../FSP51H204L6W35T6_BASE_LVT_ssgnp_cworst_ccworst_v0p675_0c_ccs.lib 这个 lib 内有没有 iso cell」。agent 写 `scan_lib_iso.py` 扫描 .lib（Liberty）文件里 cell 块名匹配 iso 关键字。

## A-faithful 评估
**合格**。用户给的是高层需求（「写一个 power iso design」）+ 澄清「ISO cell 行为级 RTL 模型，含 enable 保持/取值逻辑」（即 WHAT：隔离单元、行为级、两种隔离语义、使能极性）。agent 自行决定了 HOW：三模块分解（clamp/keep/top）、参数命名（WIDTH/CLAMP_VAL/INIT_VAL/ISO_EN_ACTIVE/ISO_TYPE）、generate 切换、Python 行为自检器的函数分解与 11 个测试用例。用户未指定模块分解/参数名/generate 结构/自检算法。

## 合成（B档）
deliverable 命中私有 /home/e0045144/jtag/ACC/run/ → .75 Permission denied → INFEASIBLE → B档自包含参数化重构。

**EDA-Eval-DesignFlow-PowerIsoCellRtlGen-001**（digital L1-B, k=16 B档, 新 archetype=power-isolation-cell-behavioral-rtl-model-generator）：
- 交付 power_iso.v（参数化三模块）+ verify_model.py（行为自检，签名固定 `clamp_iso(iso_en,din,clamp_val,active,width)` / `keep_iso(iso_en,din,cur,active)`）。
- A 配置（可见）：WIDTH=8, ISO_TYPE="CLAMP", CLAMP_VAL=0, INIT_VAL=1, ISO_EN_ACTIVE=1（高有效）。
- B 配置（隐藏，跨输入守卫）：WIDTH=16, ISO_TYPE="KEEP", CLAMP_VAL=1, INIT_VAL=0, ISO_EN_ACTIVE=0（低有效）——位宽/模式/钳位值/极性全不同。
- check.py 16 条件：①zip 含两文件 ②stdlib only ③-⑨RTL 结构（三模块/参数/generate/钳位 assign {WIDTH{CLAMP_VAL}}/保持 always 复位 {WIDTH{INIT_VAL}}+保持+跟随/极性 wire）⑩⑪import 行为函数在 B 配置正确 ⑫subprocess ALL TESTS PASSED ⑬跨输入守卫 B≠A(击败 hardcoded_A) ⑭3-seed 随机化 vs 独立 oracle ⑮结构平衡 module/endmodule+generate/endgenerate+begin/end ⑯双极性守卫。
- 自验：ref SELFTEST PASS 16/16；5 neg（naive_empty/print_only/hardcoded_A/core_removed）+ 3 fake（empty_zip/garbage/print_string）全 FAIL；NEG_RC=0；断言闸门 k_rationale=k_check=16 ✓。
