# r1009 trace deepread: bax7w (jkxu@hfeg0pkn004) — EYE_CHECK simlist generator

## trace meta
- sid: 1795085787568_bax7w.messages.json
- user: jkxu, host: hfeg0pkn004
- mc: 154, keywords: verilog:8765;drc:8487;analog:44;netlist:16;aether:4;pyaether:3;cmos:3
- ⚠️ drc:8487 关键词来自项目路径 `drcpa` (DDR5 DRCPA post-silicon) 而非真实 DRC 操作; 实际意图是 EYE_CHECK 仿真目录梳理 + owner 映射 + CSV 生成
- 235 msgs, 12 干净用户问
- scp 1.84MB (ssh e0031982@hfeg0pkn004 BatchMode)

## 用户意图序列
- U#1: 抓取 log.reg.1117 下属于 EYE_CHECK 的仿真 (上级目录带 eyecheck 关键字)
- U#2/U#3: 明确想要 16Gb/Legacy/EYE_CHECK + 16Gb/PRAC/EYE_CHECK 下的仿真
- U#4: log.reg.1105 全部
- U#5/U#6: **「我想把仿真和目录对应上 owner，然后形成脚本，自动生成 EYE_CHECK 仿真 list」** ← 核心 produce-task 意图
- U#7: 你是怎么知道 owner 的 (质问 owner 来源)
- U#8: 提供 cmds_* → owner 中文对应表 (cmds_mpc→雷昊天, cmds_odt→许靖康, tm_compress→徐小明 等 30+ 条)
- U#9: **「avl 给许靖康，然后固化成脚本，生存 csv 文件」** ← CSV 固化
- U#10: **「density 和 category 去掉，然后 dirname 改成绝对路径」** ← CSV 列收窄
- U#11: 「再加一栏是否确认完毕」(列名未定, trace 结束未解决)

## trace gold (m166 最终版 gen_eyecheck_list.py ~3.5KB)
```python
OWNER_RULES = [
    (lambda n: n.startswith('tm_compress'), 'sxiaomin'),
    (lambda n: n.startswith('tm_fuse_'), 'zhengh'),
    ...
    (lambda n: n.startswith('avl_'), 'xujk'),
]
def get_owner(d): ...  # 首条匹配, 未匹配 'unknown'
def scan(root):
    for sub in ['16Gb/Legacy/EYE_CHECK','16Gb/PRAC/EYE_CHECK',
                '24Gb/Legacy/EYE_CHECK','24Gb/PRAC/EYE_CHECK','DFT/EYE_CHECK']:
        ...os.scandir, skip noregression...
# 输出: eyecheck_simlist_all.txt / grouped.txt / eyecheck_simlist.csv
# CSV (m166): owner,density,category,group,dirname
# U#10 refinement 后: owner,group,abspath
```

## 本 case 提炼
通用 `gen_eyecheck_simlist.py <root> <config.json> <outdir>`:
- config.json: {scan_subpaths:[...], owner_rules:[{match_type,pattern,owner}]}
- 扫描 root/sub, 跳 noregression, 首条 owner 规则匹配 (未匹配 unknown)
- 输出 CSV(owner,group,abspath) + all.txt + grouped.txt
- 按 (owner,group,dirname) 排序, 确定性

## A/B 分离
- A: drcpa 项目 (16Gb + DFT, pinyin IDs, 10 sim dirs) — 可见
- B: 不同项目 (24Gb/8Gb, alice/bob/.../judy, 12 sim dirs 含 orphan→unknown) — 隐藏
- anti-hardcode 锚点: B owner 名全异于 A, B 有 zqcal_→judy (A 无此规则), A 有 16Gb groups (B 无)

## 选料决策
- 39 fresh 候选, top 4 归因:
  - 3byhk (mc243, drc:3404 主导) → C 域 skip
  - dxxm5 (mc106, drc:1599 主导) → C 域 skip
  - wcio5 (ericw mc125, verilog:476 debug-Q&A stimulus.list) → 需 proprietary fixture, 备选
  - bax7w (jkxu mc154, verilog:8765 — drc 关键词来自项目名非真 DRC) → clean produce-task 选中
