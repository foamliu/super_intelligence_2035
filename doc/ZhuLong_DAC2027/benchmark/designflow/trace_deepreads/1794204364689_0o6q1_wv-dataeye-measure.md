# Deepread: 1794204364689_0o6q1 — wv-dataeye-measure (waveform)

- session: 1794204364689_0o6q1  user: e0023936  host: hfhds201  mc: 60
- source: /home/e0023936/.cline/apps/kanban/sessions/1794204364689_0o6q1.jsonl (918KB, 5853 lines)
- domain: waveform (waveview:200 dominant; lang=tcl)
- model: deepseek-v4-flash (cline kanban)

## Real task
用户在 `/home/e0023936/devops/wv-dataeye-measure/` 有一套 WaveView 数据眼图测量流水线。FSDB
`sslvht_10667.fsdb`（信号 `v(dq)`，数据速率 10667 Mbps → UI≈93.75ps）。用户要"测量 v(dq) 的
最大眼宽"，并进一步在 WaveView 里显示眼图、对 fsdb 的 v(dq) 做 VREF 扫描。

## 关键发现 / 真正难点
1. **.rep 表头 `Max Width` 是假峰**：表头写 `Max Width : Vref=0.061 Width=68.33p Skew=35.12p`，
   但 35ps skew 对真实眼中心物理不可能 → 是边沿假峰。`wv_batch_collect.py` 因此**忽略表头**，
   从完整 VREF 扫描表里用 dual jitter gate + 邻域支持重新选点。
2. **选点算法**（来自 `wv_batch_collect.py` parse_rep）：
   - 只保留 Width>0 且 Skew>0 的行
   - min_skew = min(Skew)
   - rel_gate = 3×min_skew；abs_gate = 15.0ps；行通过当且仅当 Skew≤rel_gate **且** Skew≤abs_gate
   - 候选间互相统计 support = ±0.010V 内**其它候选**数量
   - 选 width 最大者（并列取 support 大者）
3. **真实结果**：min_skew=5.37ps（@VREF≈0.101），gate=15.0ps，候选 30 个（VREF 86~115mV），
   最佳 = VREF=0.100V → **56.99ps / 100mV / 5.38ps**（与 `wv_test/wv_out/wv_summary.csv` 一致）。
   技能目录里随包的旧 `wv_summary.csv`（64.25/109/3.89）是旧示例，非本次运行。
4. agent 还在 WaveView 里复现扫描（131 行），并用 python 读 .rep 跑选点逻辑，结果一致。

## .rep 格式（measEyeMaxWidth.tcl 产出）
```
*************************************************************************
*                     CXMT Data Eye Width Measurement
* Signal Name: v(dq)
* Data Rate  : 10667M
* VDC        : 0.040
* VAC        : 0.040
* Max Width  : Vref=0.061 Width=68.33p Skew=35.12p   <- 假峰，不可信
* Min Skew   : Vref=0.030 Width=0.00p Skew=0.00p
*************************************************************************
Vref       Width      Skew
0.030      0.00p      0.00p
...
0.100      56.99p     5.38p   <- 真实眼中心
...
```
表行正则：`^\s*<float>\s+<float>p\s+<float>p\s*$`。

## 合成 case 方向（L1 parse+transform，waveform）
SUT = `eye_width_select.py`：解析 .rep，按 dual-jitter-gate + neighborhood-support 选真实最大眼宽，
输出 `name,corner,aperture_ps,vref_mV,skew_ps` CSV。A=真实表( sanitized )，B/C=不同信号/速率的
合成表（假峰在不同 vref 区），check.py 内嵌 B/C + 独立 oracle + ≥12 断言 + 反硬编码。
