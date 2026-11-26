# 选料复核轮 #409 · shard D · 2026-11-08 ~15:55

## 背景
#399-#408 已确认 mc>=15 fresh 池（11-05 summary.tsv）对 shard D 枯竭。
#407/#408 通过 post-summary ssh 扫描 hfeg0pkn001-4 + hfeg0pnd002 找到 x8v81（已交付 #408）。
本轮扫描**新主机 hfeg0pkn005**（summary.tsv 中 D-domain 命中第 1，436 sessions，未被 #407 覆盖）。

## 扫描
- eda_flow open_session(hfhds201) → ssh hfeg0pkn005 (10.129.2.14) `find /home/*/.cline/data/sessions/ -name "*.messages.json" -mtime -30` → **376 sessions**
- cross-ref all-shard ledger (1660 sids, A+B+C+D) → **208 not-in-ledger**
- scp paths.txt + peek.py 到 hfeg0pkn005:/tmp/，远程 python3 批量解析首 2 user 消息
- 结果：约 90 条 JSONDecodeError（文件 >200KB 截断），约 118 条成功解析

## D-domain 候选评估（成功解析的）
| sid | user | U0 摘要 | 判定 |
|---|---|---|---|
| 11cny | clwang | "看下mr27 在哪配置的"（verilog 路径） | Q&A locate，非 seed |
| mn1f7/z7niq/sax7n/u9tql/vmnh4/9vjrk/7b4kj | e0014566 | "请返回当前top cell名称" virtuoso API | one-liner demo，非 design-flow |
| y6sbk/qx7gd | e0031982 | "帮我在 WaveView 中打开波形文件" | **自测**（agent 本人用户），跳过 |
| yyk0s | e0027609 | "DEJOA 的act 信号怎么实现" | Q&A，非 seed |
| 4p1z2 | ronghu | cdl.spf inst 描述 power_meas_supplies | 1 msg/8KB，过短无 gold |
| d328b/9q3m7 | rongjiez | "@compare_wave_new.pl 脚本输入参数/功能说明" | 解释脚本 Q&A，非 build |
| 1uhpn | qiang3xu | "waveview eye-diagram external trigger how to set" + "marker 字体大小" | config how-to Q&A，非 seed |
| msv4x/jqnx3/pqwcu | yqlu | "帮我优化 Python 脚本验证 TCP-CT-M1 优先连 TCP" | **用户给出根因+修复**→A 档不可用；B 档可但 1-2 msg 无完整 gold |
| 0mkow | yixiaow | "qualib tcl" + "生成检查 STD 的 tcl" | 过于 terse |
| 277nq | jinsongl | "drgqx 项目 ERC 路径...结果没有 vdll" | ERC = physical_verify，非 D |
| 3v5rl | ellawu | "水平 dummy 怎么插入" + DRC | physical_verify/DRC，非 D |
| wlraf | eunicef | "nicap_qa WARNING Short circuit Different names on one net" | net warning Q&A，marginal |
| mikng | haoxu | read primesim 路径 | spice_sim，非 D |
| 75n4g | jingjiew | "signal 文件添加 OSC timing 检测 tclk2dqo" | spice_sim/tb stimulus，非 D |
| 其余 ~80 | e0014566/e0046686/ellawu/rongjiez/sxdong/t0002987 等 | bsub env / anasimpro-gui / skill-creator / hi/nihao / "你好" / workflow-controller meta | 非 D / 非 seed / 元任务 |

## 结论
- **0 fresh D synthesizable A-grade seed** on hfeg0pkn005（208 not-in-ledger 全 peek）
- D-domain 命中要么 Q&A / config-how-to / locate（非 build），要么用户已给根因（A 档不可用），要么过短无 gold，要么 wrong-shard（spice_sim/physical_verify），要么 agent 自测
- 跨 2 批新主机扫描（#407: hfeg0pkn001-4+pnd002；#409: hfeg0pkn005）均无 fresh A-grade D seed
- **真外部阻塞**：需运维 ①全量 rescan summary.tsv（11-05 已 3 天陈旧）②放宽 D-domain 关键词 ③考虑跨 shard domain 重分配（spice_sim/waveform 部分回流 D）

## 未碰
- 未碰 shard A/B/C 在飞文件
- 未动 EDA-Flow-Bench assets/reference
- 0 case 落 jsonl
