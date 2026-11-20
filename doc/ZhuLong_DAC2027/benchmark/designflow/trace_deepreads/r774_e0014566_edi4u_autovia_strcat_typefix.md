# Deepread r774 — `1783336974544_edi4u` (AutoVia strcat type-fix)

- **trace**: `1783336974544_edi4u.messages.json` (138KB, 50 msgs, 1247 lines)
- **user/host**: `e0014566` / `hfeg0plg58`
- **cwd**: `/home/e0014566/test_power_analysis_3`
- **model**: deepseek-v4-flash
- **date**: 2026-07-06
- **match_count**: 29 (physical_verify; drc:319 / calibre:38 / virtuoso:30)
- **ledger**: shard C, claimed r774 → marked case `EDA-Eval-DesignFlow-AutoViaStrcatTypeFix-001`

## 用户真实意图（verbatim）

U#0 (act):
> 你调用你的run_code工具，跑一下你的read_open_layout.il，看下连接是不是通

U#10 (act):
> 调用你的run_code工具，运行 run_autovia_agent.il

用户想把一套 AutoVia SKILL 脚本（`run_autovia_nogui.il` + `run_autovia_config.il` + `run_autovia_agent.il`）用 `run_autovia_agent.il` 跑起来。先确认 layout 连接通，再执行 AutoVia flow。

## 根因定位

执行 `RunAutoViaNoGui()` 在 Step 6「For each power net, run Calibre DRC」段炸：

```
*Error* strcat: argument #6 should be either a string or a symbol (Type Template = "S") - 4
```

- SKILL `strcat` 要求参数为 string/symbol（Type Template = "S"）。
- `coreNum` 在 config 里是 integer（`coreNum = 4`）。
- bug 出现在两处 `bsub` Calibre DRC 调用行（`run_autovia_nogui.il` 的两个 strcat call site）：
  - `bsub -I -n <coreNum> -q pv calibre -drc -hier -turbo <coreNum> <drcDeck>` —— `<coreNum>` 是 integer 直接拼进 strcat。
- 报错「argument #6」对应 strcat 第 6 个参数即裸 coreNum。

## 用户接受的修法（trace MSG #28 editor diff）

把两处 strcat 里的裸 `coreNum` 用 `sprintf(nil "%d" coreNum)` 包起来转成字符串：

```skill
;; before (buggy)
system(strcat("cd " runDir "/" pwrnet "; bsub -I -n " coreNum " -q pv calibre -drc -hier -turbo " coreNum " " drcDeck " > drc.log 2>&1"))

;; after (fixed)
system(strcat("cd " runDir "/" pwrnet "; bsub -I -n " sprintf(nil "%d" coreNum) " -q pv calibre -drc -hier -turbo " sprintf(nil "%d" coreNum) " " drcDeck " > drc.log 2>&1"))
```

两处 call site（`projName == "ddcpb"` 分支与 else 分支）都修。用户接受此 diff，后续 trace 无回退。

## 真实工件状态

- 真实 `run_autovia_nogui.il`（603 行 / 29973 bytes）在 host 上**已被此修法修好**（post-trace），故 A 资产需**合成**保留 bug 的版本。
- 真实 `run_autovia_config.il`（cxmt10G4plus / train / austin / layout_austin6 / vss! / coreNum=4）+ `run_autovia_agent.il`（21 行 orchestrator）按 verbatim 用作 A 资产。

## reframe 决策

- 原始意图是「run 起来」，trace 中核心可复现工件 = strcat 类型 bug 的定位与修法。
- reframe 为 debug-Q&A 的 `solve.py` 自动修 bug 任务：保留 run 意图的判分（修后脚本能跑 DRC 段：DRC 命令结构保留 + sprintf 包装 + 过程体/via 逻辑 intact）。
- A-faithful：buggy nogui.il 按真实脚本结构/参数合成保留 bug；config/agent verbatim。
- B 反硬编码：不同 process/lib/cell/pwrnets/coreNum/via-selection 的自包含脚本（参数内联 vs config-load，结构亦不同）。

## 判分（k_check=13）

13 条独立断言 a-m：zip/compile/产出/bug 消失/sprintf 双 site/DRC 结构/过程体/via 逻辑/B 跑通/B sprintf/B 非硬编码/§4.9 三退化 FAIL。
- reference `solution.py`（正则包裸 coreNum）→ **PASS 13/13**
- 3 退化样本（empty_stub / print_only / core_deleted）→ **全 FAIL**（negative_selftest OK）
