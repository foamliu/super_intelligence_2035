# deepread: 1792977240005_1mvxt · yohannw · hfeg0pnd001 (10.129.32.189) · mc=761

## trace basics
- session: `1792977240005_1mvxt.messages.json` (dir layout: `.../sessions/1792977240005_1mvxt/1792977240005_1mvxt.messages.json`)
- 688 msgs / 352 user msgs / 2.6 MB — large multi-day interactive dev session
- domain: **physical_verify** (LVS / aether.rc) + layout_aether
- keywords: aether:2691; lvs:2156; drc:1970; netlist:743; .cdl:442; lib.defs:247

## user intent (real)
yohannw 在迭代开发 `dev_CXMT_Aether_ip_package.py` —— 一个 IP 打包工具，核心痛点：打包后跑 LVS 时 `emp-short-cell-list` / `emp-multi-short-cell-list` 里的 idd/PRC 宏实例被重定向到打包库 `CADTestxxx/宏`，但 aether.rc 的 short 列表前缀仍是源库名（drcoa_analog / drcoa_digital / commonIP_G5CIPanalog），匹配不上 → LVS INCORRECT。
前辈（部门）的解法：直接在 aether.rc 里把 short 列表所有非 TECHLIB 条目的 `<源库>/<宏>` 前缀改成打包库名 `CADTestxxx`（TECHLIB 条目如 parasiticRC*/probeI/RCM* 保持不变），LVS 即过。
用户最终要求：**把这个替换规则做成代码里的标准化机制**（`sync_lvs_short_aether_rc(ip_lib)`），每次跑 LVS 前自动同步、跑完（用户 U#22 决定）不还原。

## 关键替换规则（assistant 调查 aether.rc.bak vs setup 模板后确认）
- `emp-short-cell-list` (line 196, 4138 chars, ~148 cell)：条目形如 `lib/cell`
- `emp-multi-short-cell-list` (line 197, 552 chars, 9 条)：条目形如 `(lib/cell short(pin...) short(pin...))`（带嵌套括号）
- 规则：**非 TECHLIB** 的 `lib` 前缀 → 本次打包库名 `ip_lib`；**TECHLIB** 条目逐字保留
- 确保 `emp-cdl-lvsignore-short=1` 存在
- 去重保序
- backup (.bak) → sync → (用户决定不 restore)

## 用户接受的结果
- U#38「很棒 lvs pass了」(assistant 用改进方法改 aether.rc 后)
- U#22「aether.rc 跑完不许要还原」→ 最终代码删掉 _backup/_restore try-finally，跑完保留同步后配置
- 落地函数：`sync_lvs_short_aether_rc(ip_lib)` + `_re_prefix_short_entry` + `_dedup_preserve_order` + `_aether_rc_path`，在 onSubmit `os.system(run_lvs_cdl_gds)` 之前调用

## 真实 aether.rc 数据（line 196/197 原文，已抽到 /tmp/line196.txt /tmp/line197.txt）
- 源库前缀：TECHLIB / drcoa_analog / drcoa_digital / commonIP_G5CIPanalog
- 非 TECHLIB cell：AG_SetIDDGBias / AG_SetIDDSense / AG_SetIDDAmpOopen / AG_SetIDDAmpIn / AG_SetIDDAmpO / *_IPD 变体 / D_prc* / YsDec* / DqPrc* / RWCBprc* ...
- multi-short TECHLIB: `(TECHLIB/parasiticRC4 short(PLUS MINUS))`

## 造 case 决策（B 档 grounded reframe）
- 真实工具沙盒（.75 上跑 aether LVS）不可达 → 把「离线可验证子步骤」抽离为 SUT 任务：实现 `aether_rc_short_sync.py`，对任意 aether.rc 做上述前缀同步
- 资产 A：真实 aether.rc（源库前缀，faithful）
- 隐藏 B：不同库名 (analog_lib/digital_lib/common_lib) + 不同 cell + 缺 emp-cdl-lvsignore-short + 含重复条目（测「补 lvsignore」+「去重」分支）
- check 14 条独立断言 a-n，真跑 SUT 于 B
- 不是加难：grounding = 真实工具沙盒不可达 → 纯 stdlib 实现，spec 不改变用户真实意图

## 与其他 case 区分
- AutoViaBatchLogMon-001 = via 生成批处理+日志分类；本 case = aether.rc LVS short 前缀同步，physical_verify/LVS 域，互补不重叠
