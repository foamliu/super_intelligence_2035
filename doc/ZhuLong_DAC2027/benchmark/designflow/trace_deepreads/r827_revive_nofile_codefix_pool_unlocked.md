# r827 — phantom-check subdir code-fix 兑现 + NOFILE-parked revival 池解锁

> 类型：governance 轮（兑现 discuss/A.md r826 承诺 + D r969 §建议动作1）
> 日期：2026-11-20
> A 作 trace_ledger.py 共享 code owner。

## 一、问题（path-bug 假阴性 · 第四威胁轴）

cline session 文件实际在子目录 `~/.cline/data/sessions/<id>/<id>.messages.json`，
旧 peek / revival 用 flat 路径 `~/.cline/data/sessions/<id>.messages.json` 必 NOFILE
⇒ 大量活候选被误判 parked。三域实证：
- C r836 hypothesis（461oe「NFS stale」实为路径拼错）
- D r969 实测确认（6iuo6 / fz05e 子目录可读，D 台账 106 unique NOFILE-parked）
- A r820-r826 直接 revival 8 例（5 case 落库 r821-r825）

旧 revival 全靠手审单条 → 系统性杠杆缺失。

## 二、code-fix：`trace_ledger.py revive-nofile` 子命令

新增子命令（纯本机 dry-run，emit ready-to-run SSH 探测块）：
1. 扫 shard 台账 NOFILE-parked 行（status=parked + note 命中 `NOFILE|file-deleted-postscan|file-deleted`）；
2. **JOIN scan summary.tsv 恢复 (ip, host, user)** —— 台账 host 常为空（D263-peek 丢映射），
   但 summary.tsv 保留全量 ip/host/user/mc，可恢复探测坐标（关键设计）；
3. 按 (ip, user) 分批，emit subdir-aware SSH 探测命令（`</dev/null` 防 hang，TASK §2 坑3），
   每条同时探 flat + subdir，输出 `slug \t flat_size|NOFILE \t subdir_size|NOFILE`；
4. `subdir_size != NOFILE ⇒ 活候选 ⇒ un-park + deep-read + 造题`。

实现：`designflow/trace_ledger.py` `cmd_revive_nofile` + `_latest_local_summary` +
`_load_summary_coords` + `_NOFILE_RE`，注册 argparse + dispatch。

## 三、revival 池规模（11-15 summary.tsv JOIN，4543 slugs）

| shard | NOFILE-parked | recoverable | lost | ssh-groups |
|:--|--:|--:|--:|--:|
| A | 23 | 17 | 6 | 16 |
| B | 0 | 0 | 0 | 0 |
| C | 1 | 0 | 1 | 0 |
| D | 95 | 75 | 20 | 46 |
| **合计** | **119** | **92** | **27** | **62** |

92 recoverable revival 候选 ≫ A 手动 revival 8 例。lost=27 = summary 无此 slug（早于
11-15 扫描或 rotation 蒸发，坐标不可恢复）。

## 四、端到端验证（eda_flow session r827 · 4 候选实测）

| slug | shard | ip | user | mc | flat | subdir | 判定 |
|:--|:--|:--|:--|--:|:--|:--|:--|
| 6iuo6 | D | 10.129.2.10 | reedchen | 16 | NOFILE | **325798** | ALIVE（= D r969 手动 325798 ✓ 正控吻合） |
| yicdk | A | 10.129.8.226 | hengbow | 120 | NOFILE | **482470** | ALIVE（NEW A 域 lead） |
| g8en5 | A | 10.129.2.14 | jinsongl | 73 | NOFILE | **1115154** | ALIVE（NEW A 域 lead, 1.1MB） |
| zg7xg | A | 10.129.2.14 | jinsongl | 65 | NOFILE | **816732** | ALIVE（NEW A 域 lead） |

4/4 subdir-ALIVE。正控 6iuo6 与 D r969 手动结果逐字节吻合 ⇒ 工具正确性确证。

## 五、新 A 域 revival 矿脉（下轮造题 DEBT）

r826 判 A-pure 三矿脉全枯（mc≥10 fresh + mc≥5 并集 + r528 revival 末 2 weak）。
本轮 code-fix 解锁**第四矿脉** = NOFILE-parked 子目录 revival，A 域 17 recoverable
中 3 条新高 mc 已实测 ALIVE，未深读未碰撞：

- **yicdk** mc120 hengbow@10.129.8.226 482KB — 最高 mc，优先深读
- **g8en5** mc73 jinsongl@10.129.2.14 1.1MB — 偏大可分轮
- **zg7xg** mc65 jinsongl@10.129.2.14 817KB

（其余 A recoverable 多为 r826 已评 weak 的 r528 parked：06htj mc275/w4uy2 mc169/
gf2ud mc213 碰撞/h8pcp D 碰撞/7j1bw D 碰撞，或低 mc5-7 薄料。）

下轮：对 yicdk fetch + deep-read + 判域 + 合成（若 A 域且 intent 可造）。
revive-nofile 工具会重新扫出这些 parked 候选，不丢。

## 六、复现

```bash
# 全 shard revival 池概览
python3 designflow/trace_ledger.py revive-nofile
# 单 shard + 逐条坐标
python3 designflow/trace_ledger.py --shard A revive-nofile --verbose
# 探测块复制到 eda_flow run_commands（cwd=workdir）跑
# subdir_size != NOFILE ⇒ un-park:
#   python3 designflow/trace_ledger.py --shard <X> mark --session <slug>.messages.json \
#       --status parked --note 'subdir-ALIVE <size> revival r827, 待 deep-read'
```

## 七、纪律

- 🚫 未改题/图/check；🚫 未碰他 shard jsonl/MEMORY/台账
- ✅ 仅改 shared code `trace_ledger.py`（A 是 code owner，D r969 §建议动作1 明请）
- ✅ 未改任何台账行（3 A leads 留 parked，工具可重扫，下轮深读时再 mark）
- eda_flow session r827 close cleaned
