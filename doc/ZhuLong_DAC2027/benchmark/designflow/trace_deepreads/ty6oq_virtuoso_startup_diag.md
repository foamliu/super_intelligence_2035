# Deepread · ty6oq — Virtuoso IC617ISR23 启动失败诊断 (RHEL 8.10)

- **trace**: `1793872363785_ty6oq` (chengleiy @ hfeg0pkn005, mc=90, layout_virtuoso)
- **meta**: cwd=/home/chengleiy, status=pending, model=glm-5.3-flash, title="PCELL 路径整理"
- **size**: 261 msgs, 1.78 MB messages.json
- **case**: EDA-Eval-DesignFlow-VirtuosoStartupDiag-001 (B-synthesized, L1-boundary, k=14)

## 用户意图演进（10 个真实用户轮）

- U#1 (msg#0): "这个路径 /home/pdk/chengleiy/e_innovus/from_out/linux/PCELL 和 .../scripts 是我做的一些 pcell 的东西和 QA 的脚本，你来整理一下，看看是不是有能用的"
- U#2 (msg#33): 三个任务——①根据手册/pdf/ppt 形成 pcell skill；②两个 pcell QA 脚本对比防覆写；③服务器 virtuoso 不能直接启动，需要特殊命令，看 python-virtuoso 对接小程序
- U#4 (msg#81): 以 smic28 PDK 为例，删器件/加器件/改值验证 PDK QA 脚本准确性
- U#6 (msg#155): **核心需求**——"提取新版 pdk 里面的器件，导出 cdf 参数，根据 cdf 参数编写 config 信息，对新旧平台生成 pattern，跑 lvl 查看结果"
- U#7/U#8 (msg#184/185): 反复纠正——"virtuoso 启动不能直接启动，需要 `virtuoso -nocdsinit`"，"我之前不是有 lde pattern 的脚本吗？你都不借鉴一下吗？"

## 诊断主线（msg#156–235，本案 grounding 来源）

用户核心意图是 PDK QA 全链路（device→CDF→config→pattern→LVL），但 agent 卡在 **virtuoso 启动环境** 上整整 ~80 条消息。最终锁定 **4 层失败链** 并给出可工作配方：

1. **OA sysname unknown** (msg#175/179): `virtuoso -nocdsinit -nograph` rc=1，stderr 报 `sysname returned an error status: unknown`；IC617ISR23 的 `share/oa/bin/sysname` 只认到 rhel60，RHEL 8.10 不识别 → 返回 `unknown`。log 都没写出。sysname 脚本注释明确支持 `OA_UNSUPPORTED_PLAT` 环境变量强制平台名。
2. **OA 平台候选无 lib 目录** (msg#183): 先试 `OA_UNSUPPORTED_PLAT=linux_rhel60` → sysname 接受(rc=0) 但 `share/oa/lib/linux_rhel60_64/opt` 不存在 → virtuoso 仍 rc=1，stderr 报 `OA2.2 library directory ... does not seem to exist`。改试 `linux_rhel50_gcc48x` → lib 目录存在 ✓。
3. **cdsXvncd 缺 32 位 libnsl** (msg#215–223): `-nograph` 模式 IC617 仍需 X display，自动尝试启 `cdsVncserver :96` → `cdsXvncd` 是 32 位二进制，加载 `libnsl.so.1` 失败（RHEL8 移除了 32 位 libnsl）。`Trying another display...` 无限重试。解法：用系统 `Xvnc :96 -securitytypes=none` + `DISPLAY=:96`。
4. **Cadence libstdc++ 缺 CXXABI** (msg#231–235): Xvnc 起来后，virtuoso 64 位动态链接报缺 `CXXABI_1.3.8/1.3.9`（Cadence 自带 libstdc++ 太老，系统 libGLU 需要新 CXXABI）。解法：`LD_PRELOAD=/usr/lib64/libstdc++.so.6` + `CDS_AUTO_64BIT=ALL`。

**最终配方 (msg#235)**，4 个环境变量：
```
OA_UNSUPPORTED_PLAT=linux_rhel50_gcc48x
DISPLAY=:96  (系统 Xvnc)
CDS_AUTO_64BIT=ALL
LD_PRELOAD=/usr/lib64/libstdc++.so.6
```
冒烟通过：SKILL `HELLO_FROM_SKILL` 输出，license 0.07s，rc=0。

PDK QA 全链路本身 (pdk_compare.py) 因 sandbox 2 分钟时限 + virtuoso 单次启动 43s 未在本 session 跑完（msg#242/258 在后台轮询中），故本案**只抽启动诊断部分**作 case，不抽未完成的 LVL 链路。

## 关键探针输出（本案 manifest_A 数据源）

| 探针 | msg# | 关键值 |
|---|---|---|
| which virtuoso / env | 160 | bin=/apps/cdsmgr/CRB/IC617ISR23/.../virtuoso, CDSHOME, LM_LICENSE_FILE |
| virtuoso 冒烟 stderr | 175 | `ERROR: sysname returned unknown`, log 未创建 |
| OS + sysname 脚本 | 179 | RHEL 8.10, sysname rc=1 output=unknown, 支持列表含 rhel60/rhel50_gcc48x |
| OA_UNSUPPORTED_PLAT=rhel60 | 183 | sysname rc=0 → 但 OA lib dir 不存在 → rc=1 |
| OA_UNSUPPORTED_PLAT=rhel50_gcc48x | 199–203 | sysname rc=0, OA lib dir 存在 ✓ |
| cdsXvncd/X display | 215–223 | `Trying another display`, cdsXvncd 缺 libnsl.so.1 |
| libstdc++ CXXABI | 231 | Cadence 缺 CXXABI_1.3.8/1.3.9, 系统 /usr/lib64/libstdc++.so.6 有 |
| 最终冒烟 | 235 | HELLO_FROM_SKILL, license 0.07s, rc=0 |

## 选料与去重

shard C mc>=15 + layout-affinity 打分(LAYOUT×2 − SIM×1.2 + PG×1.5) 排除 ledger_C 381 session。顶部候选深读：y8881(xiwang mc192)=sandbox 检查 Q&A 6 msgs 非 seed parked；4xt0p(zhigangw mc152)= canned scene launch "启动业务场景:模拟电路优化·二次执行" 仅 1 真实用户轮 非 seed；qiqs7(alan3zh mc204)=test_chip_v1 APR 续作，U#2 floorplan-FAILED 与 r224 InnovusPwrRtDiag 同项目重叠，U#4 v2lvs 请求未被 agent 执行（msg#82 是最后一条）无 golden；ty6oq(chengleiy mc90 NEW user)=真 virtuoso 启动 4 层失败链完整诊断+可工作配方 → layout_virtuoso(51→52)。

DISTINCT from r223 VirtuosoLaunchRecipeGen（如有，Virtuoso 启动配方生成）/ r218b DrcQaWidthTypeGeom（DRC QA pattern 几何生成）—— 本案首次 ground on **Virtuoso -nograph 启动 4 层失败链诊断**(OA sysname→OA 平台 lib dir→cdsXvncd libnsl→libstdc++ CXXABI)，输出 failure_chain + env recipe，与 DRC QA pattern / Virtuoso recipe 生成互补不重叠。

## case 设计

SUT 写 `virtuoso_startup_diag.py` (CLI 2 参 `<manifest.json> -o <diagnosis.json>`, stdlib only, 解析探针 manifest，按 5 条诊断规则检测失败层，输出 8 顶层键 JSON)。
- A_run=trace grounded (IC617ISR23, RHEL 8.10, sysname=unknown, rhel60 候选无 lib dir→rhel50_gcc48x, cdsXvncd 缺 libnsl, libstdc++ 缺 CXXABI, 4 层, recipe 4 keys, smoke PASS)
- 隐藏 B=IC618.320/RHEL 7.9 (sysname unknown 但 rhel70 候选 lib dir 存在直接用, 无 Xvnc 问题因 RHEL7 有 libnsl, 仅 libstdc++ 问题 → 2 层, recipe OA_UNSUPPORTED_PLAT=linux_rhel70+LD_PRELOAD+CDS_AUTO_64BIT) 击穿硬编码 A
- B2 干净守卫=IC231.43/RHEL 9.2 (sysname ok, 无任何失败 → 0 层, recipe {}, smoke PASS) 杀 always-detect
- B3 重载守卫=IC617/RHEL8.10 + 2 个坏 OA 候选(rhel60+rhel50_gcc44x) → 5 层 杀 always-4

14 条 a-n: 见 check.py 与 test_rationale。k_check=14=k_rationale≥8 ✓
