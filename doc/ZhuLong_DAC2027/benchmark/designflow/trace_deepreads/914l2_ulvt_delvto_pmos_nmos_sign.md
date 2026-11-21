# Deepread: 1794807865026_914l2 (joeyl, hfeg0pkn004, mc220, spice_sim)

## Trace source
- session_file: `1794807865026_914l2.messages.json`
- user: joeyl · host: hfeg0pkn004 (10.129.2.13) · match_count: 220
- keywords: netlist:1036; schematic:70; hspice:62; opamp:24; cmos:2 → **netlist/spice-dominant, low schematic noise**
- live path: `/home/joeyl/.cline/data/sessions/1794807865026_914l2/` (recovered from hourly snapshot 2026-11-20_2000)
- 140 msgs / 84 user msgs

## 工具背景 (pre-existing)
`/home/joeyl/ulvt_delvto/reduce_vth.py` + `config.cfg` + `AI_USAGE.md` — 参数化 netlist delvto patcher:
- 扫描 HSPICE/FineSim netlist, 找模型为 `pulvt_ckt`(PMOS ULVT) / `nulvt_ckt`(NMOS ULVT) 的 X 实例语句
- 在语句末尾追加 `_delvto=<值>` (负值降 vth); 已有 `_delvto=` 则替换值 (幂等)
- 支持 `+` 续行 (`_delvto` 追加到最后一条物理行末尾)
- 行尾 `$`/`//` 注释时插到注释之前 (不破坏注释)
- token 精确匹配 (不误碰 `delvto_user`)
- 跳过 `.subckt` 定义行 / `*` `//` 注释行 / 非 X 开头行
- cfg: `netlist`(必填,多行/逗号) · `delvto`(必填) · `models`(默认 pulvt_ckt,nulvt_ckt) · `in_place`(默认 no→`<stem>_delvto<val>.sp`) · `require_x_prefix`(默认 yes)
- 实例行样例: `XM10 out inn vcm vcc! pulvt_ckt w=32e-6 l=length2 sd='length2>90e-9?120e-9:100e-9' as='...'`

## 用户请求序列 (12 条 real user_input)
- U0: 用 `/home/joeyl/ulvt_delvto/` 给 netlist `…/simulation/Bias/…/netlist` 加 vth=-0.2v
- U13: 我更新了 netlist, 再替换一次, 无需备份
- U18: 再替换, 这次 vth 只 -0.1
- U25: 也替换 `…/CML_C2C/…/netlist`, vth -0.2
- U34: 又抽了一次 netlist, 照原样替换
- U38: 替换 `…/Solo_Divider/…/netlist`, 只给替换后 path, vth -0.2
- U45: 这次替换 WCKTop_netlist
- **U52 (关键转折): 对 PMOS, Vth 应该 +0.2! 重新替换** ← 核心: PMOS+/NMOS− 反号
- U69: 把 WOWTOP 的 vth 数值改到 0.05
- U70: `pulvt_ckt:+0.05, nulvt_ckt:-0.05` (保持 PMOS+/NMOS− 方向, 幅度 0.2→0.05)
- U76: 再替换一次
- U80: 也换一下 -0.2V 的 WCKTOP

## 关键技术齿 (转 check 断言)
1. **per-model 反号** (U52/U70): 原 tool 对 pulvt+nulvt 一律加同一 `_delvto=<值>`. 用户发现 PMOS 阈值应向 +, NMOS 向 −. agent 加 `delvto_by_model = pulvt_ckt:+0.2, nulvt_ckt:-0.2` 配置项, 优先级高于全局 `delvto`. → check 核心齿: PMOS 实例 `_delvto=+<mag>`, NMOS 实例 `_delvto=-<mag>`.
2. **幅度可调** (U69/U70): 幅度从 0.2 降到 0.05, 方向不变. → check 齿: delvto magnitude 来自 config, 改 config 值输出随之变.
3. **幂等** (U13/U18 反复替换): 已有 `_delvto=` 替换值不重复追加. → check 齿: 跑两次输出 byte-identical.
4. **续行 `+` 追加到末物理行** → check 齿.
5. **行尾 `$`/`//` 注释插前** → check 齿.
6. **token 精确 (不误碰 delvto_user)** → check 齿.
7. **跳过 `.subckt` 定义行** → check 齿.
8. **report 含 per-model 计数** (stdout `L59 inst=XM10 model=pulvt_ckt -> _delvto=...`) → check 齿: report JSON 结构含 per-model count.

## Reframe (deliverable)
produce 模式: 交付参数化 `reduce_vth.py` + `config` 打包 `submit.zip`. layer L1, 纯 Python 文本处理无 EDA 二进制.
- A (visible): netlist_A (pulvt_ckt/nulvt_ckt X 实例, `+` 续行, `$` 注释, `.subckt` 定义行, `delvto_user=` 干扰 token) + config_A (`delvto=0.2`, `delvto_by_model=pulvt_ckt:+0.2,nulvt_ckt:-0.2`)
- B (hidden, anti-hardcode-A): netlist_B 不同模型名 (`pulvt_ckt_v2`/`nulvt_ckt_v2`) + 不同实例名 + 不同 magnitude (0.15) + 多一个 `.subckt` 定义含目标模型名(防误改) + config_B

## 与已有 case 区别
- r981 `DelvtoCktWiringPatch`: ckt 子电路 header 默认参数 + 内部 `delvto=_delvto` 转发接线 patch. 本 case 是 **X 实例行末尾追加 `_delvto=` + per-model 反号**, 机制完全不同.
