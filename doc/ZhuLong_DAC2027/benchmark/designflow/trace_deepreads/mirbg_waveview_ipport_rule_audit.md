# Deepread: 1793272965134_mirbg (yohannw @ hfeg0pnd001 / 10.129.32.189)

- mc=225, kw: waveview:1041;pyaether:962;virtuoso:277;aether:199;analog:48;synopsys:21;schematic:7;mixed-signal:3
- tools: 401 pyAether, 277 virtuoso, 6 schematic, 1 cellview
- messages.json: 2.2MB, 454 msgs, 45 user text turns
- 旧台账状态: parked "D262-peek-unfit" (2026-11-05 06:49, 跨 shard C 也 parked 2026-11-09)
- 旧判定: 不可造 (peek-unfit, 旧规则下 setup/infra 类)
- 新判定 (2026-11-15 reaudit): **可造** — 真实 EDA-sandbox infra 工作 + waveview bridge 开发, 有具体 spec + 可验证交付物

## 会话主线 (真实用户意图链)

yohannw 在构建 zhulong EDA-sandbox 的 waveview 桥接框架 (1029_zl_frame_deploy)。会话从代码理解→注释→ip_port 方案设计→waveview bridge (dev_server.tcl) 实现→风险分析→优化。

### 关键用户轮

| msg | 用户原话 | 意图类型 |
|---|---|---|
| U#0 | `/home/yohannw/workdir_26Q4/1029_zl_frame_deploy，理解该目录下所有代码文件，加注释` | 代码理解+注释 |
| U#199 | `绘制一份启动路由说明，多图讲解，html，我用来学习消化，以快速上手` | 文档生成 |
| U#248 | `目前ip_port是这种格式...针对pyAether、virtuoso、waveview(待上线）分别生成ip_port，给我方案` | 方案设计 |
| U#345 | `generate_ip_port.py,检查下，是否遵循如下规则，先不动代码 ... port = 20000 + ((UID × multiplier) % 45533) ... aether 10008 / virtuoso 10009 / waveview 10010` | **规则验证 (A档选用)** |
| U#399 | `waveview比较特殊...在server程序中加功能...写回~/.cline/data/settings/ip_port.json文件中的tcl部分...先不改代码，确认你是否理解` | 方案讨论 |
| U#407 | `开始执行，执行完标注改了哪些` | 实现 |
| U#421 | `检查程序，是否有潜在导致卡死的逻辑` | 风险分析 |
| U#433 | `R1：给每个 exec 包 timeout 2...R4：把顶层写回改成 after 0...执行` | 优化实现 |

### 选用 A档轮: U#345 (规则验证)

**用户原话**:
```
generate_ip_port.py,检查下，是否遵循如下规则，先不动代码
注意一下 三个服务的动态端口计算公式（唯一差异是乘数 multiplier）：

    port = 20000 + ((UID × multiplier) % 45533)

| 服务 | 计算公式 |
| --- | --- |
| aether | 20000 + ((UID × 10008) % 45533) |
| virtuoso | 20000 + ((UID × 10009) % 45533) |
| waveview | 20000 + ((UID × 10010) % 45533) |

其中：
- UID = os.getuid()（当前 Linux 用户 ID）
- 20000 = 端口基数（base）
- 45533 = 65535 − 20000 以下的最大素数
- 10008 / 10009 / 10010 = 三个服务各自的乘数
```

**选轮合规性**: 用户轮分类 = 提出需求 (验证请求) ✓。用户给出的是 **期望规则 (spec)**, 不是根因或修复方案 → 符 A档选轮规则。

### 资产 A (真实 generate_ip_port.py, msg 347 tool_result)

文件实际状态 (非合规):
- `SERVICE_MULTS = {pyAether:10008, skill:10009, waveview:10010, virtuoso:10011}` — 服务名错 (pyAether/skill 应为 aether/virtuoso), virtuoso 乘数错 (10011 应为 10009)
- `main()` 输出 cfg = {pyAether, skill, waveview} — virtuoso 被注释掉 (spec 要求输出)
- `port(uid, mult, base=20000, mod=45533) = base + ((uid*mult)%mod)` — 公式结构 ✓ 匹配 spec
- `uid = os.getuid()` ✓

### 金标准 (审计结论)

对照 spec:
1. 公式结构: base + (uid*mult)%mod ✓ 匹配
2. base=20000 ✓, mod=45533 ✓, uid=os.getuid() ✓
3. aether: **缺失** (文件用 "pyAether" 命名, 非 spec 的 "aether"); 乘数 10008 ✓
4. virtuoso: **未输出** (main 中注释掉); 乘数 10011 ≠ spec 10009 ✗
5. waveview: 输出 ✓, 乘数 10010 ✓
6. 额外服务: skill (spec 无), pyAether (应为 aether)
7. overall_compliant = false

### 交付物设计 (C第三范式 produce-task)

- prompt = U#345 原话 (A档 trace-faithful, 不脱敏)
- asset A = generate_ip_port_A.py (真实非合规文件)
- 交付 = audit_ip_port.py (通用审计脚本) + audit_report_A.json (A 上输出)
- hidden B = B1 (合规) / B2 (不同偏差) / B3 (mod 错) — check() 跑 agent 脚本 + reference 脚本 on B, 比对
- reference = audit_ip_port_ref.py (importlib 加载目标, 实跑 port(), 比对 spec)
- 反硬编码: B 与 A 服务名/乘数/结构全不同, agent 必须真解析代码不能背 A 的答案

## domain 判定

- waveview:1041 (最高 kw) + pyaether:962 → 真实 waveview 桥接 + pyAether 脚本工作
- D-purity: waveview 主导, 笔记归 D (waveform domain)
- 跨 shard C parked: C 旧判 peek-unfit, 本质是 waveview infra (D 域), D revival 合规 (note 记录)
