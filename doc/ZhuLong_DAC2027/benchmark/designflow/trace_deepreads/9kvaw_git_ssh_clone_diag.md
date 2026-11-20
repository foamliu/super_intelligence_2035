# 9kvaw — git clone SSH 失败诊断 (deepread)

**session**: `1793004297782_9kvaw` · user `harrys` @ `10.129.2.11` · mc=7 (rtl:34;netlist:2;systemverilog 隐含)
**session json**: 159,591 B / 123 msgs · agent `lead` · model glm-5.2 / deepseek-v4-flash · 2026-10-27 06:59 (status=failed, exit 1)
**liveness**: r794 标 ALIVE(flat-path) → r803 标 ssh-timeout → **r816 复测推翻:r810 path-bug**, subdir `/home/harrys/.cline/data/sessions/1793004297782_9kvaw/*.messages.json` = ALIVE (159,591 B, mtime Oct 27)。r803 的「rotation 蒸发 / host 不可达」结论同 r760/r761/r773/r794 一并作废 = path bug 非真枯竭。

## 真实用户意图(逐条原话)

- **U0** (ts 1793004299213): `https://workspace.cxmt.com/folder?guid=551789134444789810 upload file` (agent 因 fetch_web_content 不在 allowedTools 无法访问该网盘,转而问澄清)
- **U17** (ts 1793084046): `git clone git@10.129.8.11:ddvp/gddr7_tb.git`  ← **核心任务: 克隆 GDDR7 testbench 仓库**
- **U82/U103** (ts 1793084173 / 1793084240): 重复 `git clone git@10.129.8.11:ddvp/gddr7_tb.git` (前序尝试超时,用户重发)

## agent 工具链与产物

1. list_allowed_files `/home/harrys/Desktop` → 见 digital_rtl_design/ nand/ sim/ vcd2fsbLog/ verdiLog/ novas.conf simvisdbutil.log (EDA 仿真工程师桌面)
2. ask_question 澄清上传需求 → 用户改要 git clone
3. editor ×N 写 `/home/harrys/Desktop/clone_gddr7.sh` (cd Desktop + git clone --depth 1 + GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30" + nohup 后台 + rm -rf gddr7_tb 重试 + tee clone_log.txt)
4. run_approved_command(profile=shell-runner) ×N → 反复 SIGKILL 超时 (shell-runner 超时限制 + SSH 卡住)
5. read_files clone_log.txt → "正克隆到 'gddr7_tb'..." + "fatal: 目标路径 'gddr7_tb' 已经存在" + Exit code 128
6. editor 写 `check_clone.sh` (ps -p PID + 检查 gddr7_tb 内容) + `cleanup_clone.sh` (pkill -f "git clone.*gddr7_tb" + rm -rf)
7. **关键诊断**: editor 写 `test_ssh.sh` → `ssh -vvv -o BatchMode=yes git@10.129.8.11 "echo SSH_OK"` → read_files ssh_debug.txt
8. read_files `/home/harrys/.ssh` → 只有 known_hosts,**无私钥**
9. 最终诊断 (msg 122): 从 SSH verbose 日志锁定根因:
   - `debug1: identity file /home/harrys/.ssh/id_rsa type -1` (5 种 key 全 -1 = 无私钥)
   - `debug1: pubkey_prepare: ssh_get_authentication_socket: No such file or directory` (无 ssh-agent)
   - `debug1: Authentications that can continue: publickey,password` (服务器要 publickey 或 password)
   - `debug1: Trying private key: ...` ×5 (全失败)
   - `debug1: Next authentication method: password`
   - `debug1: read_passphrase: can't open /dev/tty: No such device or address` (无 tty 无法输密码)
   - `git@10.129.8.11: Permission denied (publickey,password).`
10. 给出 3 方案: A) ssh-keygen 生成密钥 + 加公钥到 git 服务器 / B) 复用已有私钥 / C) HTTPS 替代。session 终因用户未确认而 failed。

## 关键产物字段(真实 ssh -vvv 日志,作为 input A)

- 连接: `Connecting to 10.129.8.11 [10.129.8.11] port 22.` → `Connection established.`
- 主机密钥: `Server host key: ecdsa-sha2-nistp256 SHA256:/OuF7I8HZEgfV5jGDI+2+4MeetONbiX6V8Fasr6hL9o` → `Host '10.129.8.11' is known and matches` (host key OK,非本根因)
- 身份文件: 5 种 (`id_rsa/id_dsa/id_ecdsa/id_ed25519/id_xmss`) + 各自 `-cert` 全 `type -1` (无私钥)
- ssh-agent: `ssh_get_authentication_socket: No such file or directory` (无 agent)
- 认证方法: `Authentications that can continue: publickey,password` → 尝试 `publickey` (5 私钥全缺) → `password` (`read_passphrase: can't open /dev/tty`)
- 终态: `Permission denied (publickey,password).`
- 用户/路径: ssh 用户 `git`,本地 home `/home/harrys`,远程 `10.129.8.11:22`

## 选料判定

- **域**: `eda_other` (EDA 工程师日常 dev-ops / env-config: 内部 git 仓库 SSH 克隆是 IC 设计流常用工具链操作;trace 关键词 rtl:34/netlist:2 来自 gddr7_tb 仓库内容,但本任务实质=git/SSH 环境配置诊断,归 eda_other)。
- **A-pure**: 是 (无 finesim/hspice/PEX/virtuoso layout/calibre DRC 等 C/D 工具调用;整个会话是 git clone + ssh 诊断)。
- **A档为何不可行**: 用户字面请求 = `git clone git@10.129.8.11:ddvp/gddr7_tb.git` (克隆私有 GDDR7 testbench 仓库)。该任务**无法在 SUT 沙盒忠实复现**: SUT 无 10.129.8.11 git 服务器访问权、无私钥、gddr7_tb 是组私有仓库;判分也无法验"克隆成功"(沙盒里那个仓库不存在)。按 §3「单轮闭环 + A/B 双档」与 11-15 意图审计「env-config/debug-Q&A 全部恢复为可造」, 转 **B档 synthesized produce-task reframe**: 把 agent 真实做的诊断子任务(解析 ssh -vvv 日志 → 定位根因 → 给修复方案)固化成可复用 `git_ssh_diag.py`,**input A 用 trace 里真实的 ssh_debug.txt 全文**(trace-faithful 资产),hidden-B 换不同根因(host key changed / connection timeout / auth succeeded)验通用性。
- **判分有牙**: check.py 在 3 个 hidden-B 日志上真跑脚本,断言 root_cause 分类正确 + evidence 是 B 日志真实子串 + 认证方法/私钥/agent/tty/clone_succeeded 布尔正确 + 确定性 + 反硬编码(B 特定 host IP 必现、A 特定 gddr7_tb/10.129.8.11/harrys 必不现)。

## case 落点

- **CID**: `EDA-Eval-DesignFlow-GitSshCloneDiag-001` (shard A, eda_other, B档 synthesized, k=15/15)
- **A 资产** (SUT 可见, `assets/<id>/original/`): `ssh_debug_A.txt` (trace 真实 ssh -vvv 日志, 75 行) + `config_a.json` + `task_brief.md` + `prompt.txt`
- **B hidden** (`assets/<id>/hidden/`, 不进 SUT 沙箱): `ssh_debug_B1.txt` (host key changed, host 10.129.99.42) + `ssh_debug_B2.txt` (connection timeout, host 10.129.77.13 port 2222) + `ssh_debug_B3.txt` (auth succeeded, host 10.129.55.88) + 3 config_bN.json + hidden_manifest.json
- **ref**: `git_ssh_diag_ref.py` (stdlib only, 正则解析 + 根因优先级分类 + evidence/auth/bool 提取 + remediation)
- **check.py**: 15 独立断言 (zip+script+size / py_compile+stdlib / 3 B 跑通 / 11 字段齐 / B1 root_cause / B2 root_cause / B3 root_cause / B3 auth_offered / B3 auth_attempted+has_private_key / clone_succeeded B3 True & B1/B2 False / remediation 对应根因 / evidence 真实子串 / remote_host/port/user / 确定性 / 反硬编码)
- **5 negatives**: neg_empty / neg_print_only / neg_hardcode_a / neg_core_deleted / neg_stub_success (全 FAIL)
