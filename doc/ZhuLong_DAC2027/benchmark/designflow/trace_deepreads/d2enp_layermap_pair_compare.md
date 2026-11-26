# d2enp — layermap 文件对比 (gokuguo@hfeg0plg54)

trace_source: `gokuguo@10.129.35.69` (hfeg0plg53) session `1794275240977_d2enp`
- mc=15, agent='lead', 18 msgs (10 user / 8 assistant), 2026-11-10, cwd 未明确（操作 /proj/lacaa/...）
- keywords (summary_1118): virtuoso:55;techfile:4;pdk:4;mosfet:4 — 真实信号 (layermap=Virtuoso techfile)

## 用户意图（逐字）
- U#0: "compare /proj/lacaa/V0_FS_Virtuoso_test/libs/35HFS/35HFS.layermap and /proj/lacaa/TV1_FS_Virtuoso/libs/35HFS/35HFS.layermap"
- (trace 末尾无后续用户轮；助手给出对比结论 = trace-end-gold)

## 助手工具链
1. A#1: get_agent_policy_status + list_allowed_files 探 `/proj/lacaa/V0_FS_Virtuoso_test/libs`
2. A#4: list_allowed_files 两边 `libs/35HFS` (includeOwnership) → 发现都是 symlink
3. A#7: read_files 读 `/apps/imctf/cad/techlib/als/lacaa/0.2.9/fs_vir/35HFS/35HFS.layermap` (symlink 解析后的真实路径)
4. A#9/A#13: run_approved_command python-runner 跑 `compare_layermap.py` (自建)
5. A#15: shell-runner `rm -f /home/gokuguo/compare_layermap.py` 清理
6. A#17: 给结论表

## 助手真实写过的工具 (gold 子交付)
`/home/gokuguo/compare_layermap.py` (editor 创建, run_approved_command 执行):
- 输入两个路径 (sys.argv[1], sys.argv[2])
- `os.path.realpath` 解析 symlink
- `os.path.samefile` (inode 等价)
- 文件 size + MD5
- 输出 PATH1/realpath/PATH2/realpath/same_inode/size/md5

## trace-end-gold 结论
两个 `35HFS.layermap` 路径的 `libs/35HFS` 都是 symlink → 同一真实文件
`/apps/imctf/cad/techlib/als/lacaa/0.2.9/fs_vir/35HFS/35HFS.layermap`
- same_inode: true, size 99034 bytes, MD5 `1e37a3a36e233bf5b8f45224de46d695` (两边相同)
- 结论: identical (the very same file, via symlink)

## 档 B reframe (A 档不可行)
- A 档 gold = 对真生产 99KB layermap 的对比结论；SUT 不可达 /proj/lacaa 生产 fs，且 99KB layermap 不宜整包外发
- 抽离可离线复刻的子交付 = **通用文件对等价审计器** `file_pair_audit.py`
- 用户底层意图 = "这两个文件是不是同一个/有没有差异" — trace 内助手真实写过 compare_layermap.py
- 2026-11-15 §二 reaudit: file-compare Q&A 类恢复为可造
- reframe = 纯 stdlib (os/hashlib/sys/json)，输入两路径 → realpath/samefile/inode/size/md5/行级diff/文本或二进制判定 → 确定性 JSON

## 子型
file-pair-equivalence-audit (layermap-pair-compare)

## 隐藏 B vs 可见 A (anti-hardcode)
- 可见 A: 一对 layermap 风格的小文本文件，内容不同（差异行）+ 一对 symlink 指向同源
- 隐藏 B: 完全不同结构 — 含 symlink 对(同 inode)、文本差异对(added/removed/changed 行)、二进制对、缺失路径 — 全换 anti-hardcode

## 域归属判定
layout_virtuoso (layermap = Virtuoso layout techfile 映射文件；techfile/pdk 关键词印证)。真 C 域。
（对照：r802 备选 vrctd 真任务=liberal merge_libs .lib → characterization=B 域，已留 B 不取）
