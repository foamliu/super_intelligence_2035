# r1137 (2026-11-24) — 7xub5 case 合成轮 · WaveformPwlStimGenProduce-001 落库

## 背景
r1137 单 case 产出轮。从 .75 scan (20261124_023802) 的 spice/char 候选池里筛出首个 FRESH 高 mc 会话 `1795402743159_7xub5` (yinyus@hfeg0plg67, mc417, drc:680/waveview:434/hspice:356)。top-250 去重候选里 mc≥395 band 仅此 1 条 fresh (其余 62 条全 used), mc417 远超 B 门槛 5。deepread 后确定可封装为 L1 纯 Python stdlib SPICE 工具复制器。

## deepread 要点 (291 msgs, agent=lead)
真实任务: yinyus 把 finesim 20GB FSDB 提取的 isub(inh_vblh) 衬底电流波形 (低精度 Custom WaveView dump, 13828 点, t 0..2.458µs, -1.654e-3..1.251e-1 A) 转成 HSPICE PWL 电流激励 `ivblh vblh! 0 pwl(...)`, 波形平移到 200µs 后、前面保持 0。核心难点:
1. **低精度时间戳重复**: dump 时间只 3-4 位有效数字, 快瞬态区 (native 10-100ps 步) 多行共享同一打印时间戳 → 13828 点塌缩成 1760 个 distinct group。HSPICE pwl() 要求严格递增, agent 把每个等时间戳 batch 在"本→下一点"区间内均匀展开, 全部点保留不丢弃。
2. **%.12E 时间格式**: 早期细步 (1e-11 相对 1.2e-4 平移) 用 %.6E 会塌缩, 改 %.12E 保持可分辨。
3. **环境坑**: WaveView/fscript license DNS 在沙箱解析不了 → 用 pyAether 沙箱解析 license IP → python-runner(glibc 2.28) 里 `wv -ace_no_gui` 按 `sx_export_precision 10` 精确导出 → 后台跑+轮询 (20GB 文件载入超 120s 前景限制)。最终封装成可复用 SKILL 脚本 `ivblhBuildPwlCurrent.il` (pwlCUReadWave/pwlCUFixMonotonic/pwlCUToStartAt/pwlCUEmitPwl)。
4. 后续对 v(vblhacten_u)/v(enn)/v(ens) 等电压信号做同样处理, 并对 v(enn) 做电平反向 (v'=(vmax+vmin)-v)。

## 本轮动作 (合成 + 自验 + 落库)
1. 选定可自包含的核心: "波形 dump → HSPICE PWL 激励" 通用转换 (不依赖 20GB FSDB, 只需文本 dump)。domain=spice_sim。
2. 构造 input A (忠实重建): `isub_dump.txt` — Custom WaveView 低精度 dump 格式 (`#` 注释 + XVAL/YVAL 列头 + `+` 续行 + SI 后缀 u/n/m/p), 2082 点 (稀疏早区 40 + 密集瞬态 0.55-0.75µs/100ps步 + 稀疏晚区), t 1.25e-8..2.44e-6, v -5.23e-6..1.251e-1 A, 3-sig-fig 时间戳产生 582 distinct group (max batch 10)。
3. 构造 hidden B: `vctrl_dump_B.txt` — 电压控制信号 v(vblhacten_u), 1091 点, t 0..2.45µs, v -1.87e-2..1.116V, 287 distinct group (max batch 90, 瞬态 0.95-1.05µs/100ps步)。测试生成器对"不同信号类型/值域/点数/重复模式"的通用性。
4. **修复 dump 生成器 SI 后缀 ULP 问题**: 最初 SI 后缀 (0.9502u, 全精度) 与 %.2e (9.50e-07, 3-sig-fig) 混用导致同 batch 内 float ULP 差异 (0.950u→9.4999...e-7 vs 9.50e-07→9.5e-7) 把连续 batch 拆散 → fix_monotonic 失效。修复: SI 后缀只洒在非 batch (稀疏) 点上, batch 内统一 %.2e 记法。
5. ref `pwl_stim_gen.py` (7304B, 纯 stdlib): parse_dump (解 #/XVAL/+/SI后缀 u/n/m/p/k/M/g + 科学计数法) + fix_monotonic (连续等时间戳 batch 均匀展开, 末 batch 用 eps) + emit_pwl (%.12E 时间 + `+ 0 0` hold + `<src> <nodep> <noden> pwl(...)` 卡)。CLI: --dump/--src/--nodep/--noden/--tstart/--out。
6. check() 13 条独立断言 (a-m): zip完整+py+size / exit0+stim.sp / 首行卡 / +0 0 hold / 结构+/) / 严格递增 / 首数据@tstart / 末数据@tstart+tmax / 点数==oracle_n(全保留) / 值域匹配 / %.12E格式 / 无重复时间戳 / oracle交叉比对。oracle 独立重解析 B (不依赖 ref)。
7. 自验 (local, Python3): REF 13/13 PASS ✓; 3 假 (empty/only_print/core_deleted) 全 FAIL ✓; negative_selftest.py 全 FAIL ✓。

## 交付物
- case: `benchmarks/EDA-Eval-DesignFlow/cases/B/EDA-Eval-DesignFlow-WaveformPwlStimGenProduce-001.json` (19711B)
- A 资产: `assets/.../A/{isub_dump.txt, task_brief.md}` + `_gen_dumps.py` (生成器, 可复跑)
- B 隐藏: `assets/.../hidden/{vctrl_dump_B.txt, hidden_manifest.json}`
- 参考: `reference/.../{pwl_stim_gen.py, check.py}`
- 负样本: `reference/.../negative/{empty.py, only_print.py, core_deleted.py, negative_selftest.py}`

## trace 溯源
user=yinyus · host=hfeg0plg67 · session=1795402743159_7xub5.messages.json · mc=417 · domain=spice_sim
real_task_summary: 把 finesim 20GB FSDB 提取的 isub(inh_vblh) 波形转成 HSPICE PWL 电流激励, 平移到 200µs 后, 低精度时间戳重复 batch 均匀展开保证严格递增; 后续封装成可复用 SKILL 脚本

## 资产可访问性备注
真实 .sp 输入文件 (`/proj/drcpa/V0/simdir/hspice/yinyus/vblh_SF/sim/tran/current_ability/ivblh_idd5b2.sp`) 与 agent 工作区 (`/ai_sandbox/drcpa/V0/agentdir/yinyus/`) 对 t0002965 均 permission denied (不同用户)。input A 为基于 trace 中真实数据特征 (13828 点/t 0..2.458µs/-1.654e-3..1.251e-1 A/3-4 sig fig 时间戳/13828→1760 distinct group) 的忠实重建, 保留真实信号名/路径/格式。trace_source 记录真实 session/user/host。

## 指标
- 📊 covered=594/4529=13.1% (+1)
- 🎯 最近20条 (本轮未 pi 实跑, 不变)
- 台账 B: 7xub5 claimed→case
- DEBT: 0

## 体积
📦 MEMORY_B < 32KB ✓
