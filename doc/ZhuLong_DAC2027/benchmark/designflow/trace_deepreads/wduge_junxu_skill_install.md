# 深读笔记 — 1789629093789_wduge（EDA skill 统一 git 管理 + install 脚本 · env-config/flow-driving produce-task）

- **trace**: `/home/junxu/.cline/data/sessions/1789629093789_wduge/1789629093789_wduge.messages.json`（junxu @ hfeg0pkn005=10.129.2.14, mc=155, 112 msgs, 460KB, 52 assistant）
- **来源**: r1075 fresh D-pure 候选（waveview:1380 + virtuoso:906 主导，D-domain waveform/analog_context）
- **keywords**: waveview:1380;virtuoso:906;schematic:37;netlist:16;techfile:7;adexl:7;cadence:5
- **domain**: waveform（skills 含 wv-cli WaveView CLI + virtuoso-cli + block-sim + block-design，EDA 设计流 skill 管理）

## 用户意图轮（U#0 = msg 0，A档合规：提出需求✓ 未给根因/修复✗）

> 「- /home/junxu/.cline/skills/block-design
> - /home/junxu/.cline/skills/block-sim
> - /home/junxu/.cline/skills/wv-cli
> - /home/junxu/.cline/skills/virtuoso-cli
>
> 是我开发的一套 skill，我想要把这些 skill 放到 ~/Agents/custom_design_skill 进行统一的 git 管理，并用一个 install 脚本将这些 skill 安装到 skill 目录中。那些开发过程中的东西留在 custom_design_skill中，仅将 skill 运行所需的文件进行安装即可。这个 skill 安装脚本需要有通用性，别人 clone 我的仓库要能直接使用。
> 有一个问题，这些 skill 已经有一些建立了 git 仓库，合并之后可以保留仓库历史吗」

## assistant 工具链（52 assistant msgs）

- `run_commands` 探索 4 skill 结构 + git 状态（block-sim 1 commit, virtuoso-cli 66 commits, block-design/wv-cli 无 git）
- `read_files` 读 SKILL.md 了解依赖关系
- `run_commands` 创建 ~/Agents/custom_design_skill/ + git init
- `git read-tree --prefix` + `git commit-tree -p` 手动 subtree 导入（git subtree 不可用）保留历史
- `write_file` 分段写 install.sh（因内容过大被拒绝，分多次写）
- `run_commands` 测试 install.sh（--list, --link, --target, --uninstall）
- 最终验证 git log 保留 70 commits

## GOLD（assistant 最终交付，msg ~33-34）

### 仓库结构
```
~/Agents/custom_design_skill/
├── skills/
│   ├── block-design/       # 仅 SKILL.md
│   ├── block-sim/          # SKILL.md + scripts/ + finesim_doc/
│   ├── virtuoso-cli/       # SKILL.md + scripts/ + references/
│   └── wv-cli/             # SKILL.md + scripts/ + server/
├── install.sh              # 通用安装脚本
├── .gitignore
└── README.md
```

### install.sh 功能
| 命令 | 说明 |
|------|------|
| `./install.sh` | 复制模式安装到 ~/.cline/skills/（默认） |
| `./install.sh --link` | 符号链接模式（开发用） |
| `./install.sh --target /path` | 自定义安装目录 |
| `./install.sh --uninstall` | 卸载已安装的 skill |
| `./install.sh --list` | 列出将要安装的 skill |
| `./install.sh --help` | 帮助 |

环境变量 `CLINE_SKILLS_DIR` 也可覆盖目标目录。

### 安装时排除的开发文件
- `tests/` — 测试代码
- `docs/` — 设计文档
- `HANDOFF.md`、`REVIEW.md` — 开发过程文件
- `__pycache__/`、`*.pyc` — Python 缓存
- `.git/`、`.gitignore` — git 元数据
- `build_*.py` — 构建脚本

### Git 历史保留 ✅
通过 `git read-tree --prefix` + `git commit-tree -p` 手动实现了 subtree 导入：
- virtuoso-cli: 66 个 commit 全部保留
- block-sim: 1 个 commit 保留
- 总计 70 个 commit（68 原有 + 2 个导入合并 commit）

## 判定：buildable（L1 produce-task，synthesized-reframe）

- ✅ 真实 trace + D-domain（EDA 设计流 skill 管理，waveview/virtuoso 相关）
- ✅ A-faithful U#0=msg0（提出需求：统一 git 管理 + install 脚本 + 保留历史，未给根因/修复）
- ✅ GOLD = msg 33-34 完整交付（仓库结构 + install.sh 6 命令 + 排除清单 + git 历史保留）
- ✅ L1 produce-task：判分只需 bash 跑 install.sh + 文件系统断言，**无需 EDA 沙盒**
- ⚠️ 真实 skill 不可沙盒复用（含 WaveView/Virtuoso/FineSim 依赖）→ synthesized-reframe：合成 A/B/A' 三集 mock skill repo（token 结构性不相交），候选产 install.sh，check 在 B+A' 上跑

## 合成方案

- case_id: `EDA-Eval-DesignFlow-SkillInstallScriptProduce-001`
- A repo（visible）: 4 mock skills (block-design, block-sim, wv-cli, virtuoso-cli) 含 runtime + dev 文件
- B repo（hidden, judge 从 JSON spec 生成）: 4 不同 mock skills (drc-linter, lvs-checker, pex-extractor, rc-analyzer)，skill 名/文件名/目录结构与 A 全不相交
- A' repo（hidden, judge 从 B 派生）: 4 又不同 skills (timing-check, power-analysis, em-simulator, thermal-sim)，击穿 B-hardcode stub
- 交付: `submit.zip` 含 `install.sh`
- check k=15: a-zip含install.sh / b-shebang可执行 / c---list输出B skill名 / d---help显示选项 / e-安装B后runtime文件齐 / f-安装B后dev文件无 / g---link符号链接 / h---uninstall删除 / i---target自定义路径 / j-CLINE_SKILLS_DIR环境变量 / k-3-seed确定性 / l-A'安装exit0 / m-A'安装文件≠B(anti-hardcode) / n-A'---list输出A'名 / o-A'dev文件排除
- 3 neg: empty_shell / print_only / hardcode_a → 全 FAIL
- §4.9 三假 FAIL + anti-hardcode A' 交叉校验
