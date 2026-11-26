# 深读笔记 — k5jti (e0046913 / hfeg0pkn003 / mc45)

- session: 1792399896024_k5jti.messages.json (26 msgs, 298KB, 10.129.2.12)
- domain: pnr_signoff (PrimeTime STA 版本选择 / install 目录侦察)
- level: L1 (离线 python，读 fixture 目录树，结构判分，不跑 PT 二进制)
- track: A-faithful

## UI#1 (idx 0, 逐字原文) — clean 提出需求
`<user_input mode="act">分析此目录/apps/synopsys/primetime下的各项文件夹有什么区别；如果我想使用primetime 来调试STA flow，我应该选择哪个版本去使用？</user_input>`
- 规则②核：用户只提需求（分析目录 + 推荐版本），未指出根因/未给修复方案 → A-faithful ✓
- 仅 1 条 user_input，trace 末尾为 cleanup 工具被拒（idx 25），无「用户接受最终回答」文本 —— 但助手真实产物（inspect_pt.py / inspect_pt2.py + 发现的事实）= 工具真实产物，作金标。

## 助手真实工具链 / 产物
1. list_allowed_files(/apps/synopsys/primetime) → 解析为 /apps/synopsys/pts（PrimeTime Suite 安装根）
2. list_allowed_files(/apps/synopsys/pts, depth=1) → 7 个顶层条目：
   - 真实安装目录(5): L-2016.06-SP2 / O-2018.06-SP5-1 / P-2019.03-SP3 / U-2022.12-SP5 / V-2023.12-SP4.new
   - 符号链接(2): V-2023.12-SP4 (→../primepower/prime/V-2023.12-SP4) / V-2023.12-SP5 (→../primepower/prime/V-2023.12-SP5)
3. read_files 各版本 install.log → 解析格式：
   `Synopsys Installer: 5.0.0` / `STANDALONE : pts` / `INSTALLING pts product, common package, <version> version.`
   → product=pts, version=<dir name>
4. editor 写 inspect_pt.py (os.lstat/os.readlink/os.path.realpath) → 解析 symlink：
   - V-2023.12-SP4: islink=True, readlink→../primepower/prime/V-2023.12-SP4, realpath→/apps/synopsys/primepower/prime/V-2023.12-SP4（**指向 pts 树外**，primepower 产品）
   - V-2023.12-SP5: 同理 → primepower/prime/V-2023.12-SP5
5. inspect_pt2.py 验证 primepower/prime/V-2023.12-SP4(SP5) 存在 + V-2023.12-SP4.new 顶层含 admin/bin/doc/install.log/libraries/...
6. bin/ 检查：每个真实版本 bin/pt_shell + bin/primetime 均存在
7. (idx 20 thinking) 编译分析：真实 pts 安装=5 个；V-2023.12-SP4/SP5 symlink 指向 primepower（不同产品）；推荐 = 最新真实 pts 安装 V-2023.12-SP4.new 用于 STA flow。cleanup 被拒，trace 结束。

## 金标 (faithful 复刻助手方法论)
交付件 = pt_version_recon.py：CLI 接受 install root 路径 → 枚举 depth-1 条目 → 分类(real_install / symlink) → symlink 解析 readlink+realpath+检测指向树外 → 真实安装解析 install.log(product/version/installer) → 检查 bin/pt_shell+bin/primetime → 输出 JSON {versions:[...], recommendation:<最新真实 pts 安装>} → 推荐 = 最新真实(非 symlink/非树外) pts 版本用于 STA flow。

## fixture (合成 PT-like 目录树，不依赖真实 /apps/synopsys/pts)
- fixture_A (assets/primetime_install/, SUT 可见): pts root + 5 真实安装(L-2016.06-SP2/O-2018.06-SP5-1/P-2019.03-SP3/U-2022.12-SP5/V-2023.12-SP4.new) + 2 symlink(V-2023.12-SP4→../primepower/prime/V-2023.12-SP4, V-2023.12-SP5→../primepower/prime/V-2023.12-SP5, 指向树外 primepower/)；每真实版本 install.log + bin/pt_shell + bin/primetime stub。
- fixture_B (reference/hidden/, 不进 SUT 沙箱): 不同版本名 [S-2017.09-SP1/W-2024.06-SP2/X-2025.03-SP1.new] + 不同 symlink [W-2024.06-SP2→../primepower/prime/W-2024.06-SP2, Y-2025.06-SP1→../primepower/prime/Y-2025.06-SP1] + 不同最新版 → cross-input guard + anti-hardcode。
- A/B 在版本名/symlink 名/目标路径/最新版/真实安装数 均不同。

## check.py 16 条断言 (a)-(p) — 见 MEMORY 顶部 / jsonl test_rationale
