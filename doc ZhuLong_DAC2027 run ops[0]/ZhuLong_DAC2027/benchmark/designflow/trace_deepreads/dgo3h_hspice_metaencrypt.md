# trace_deepread: 1794459781454_dgo3h (zhenglu @ hfeg0pkn003, mc215, spice_sim)

**session**: 1794459781454_dgo3h  **user**: zhenglu  **host**: hfeg0pkn003 (10.129.2.12)
**mc**: 215  **keywords**: hspice:1022;synopsys:143;pdk:21;netlist:14;mosfet:11;aether:9;lvs:6;.spi:5
**msgs**: 251  **size**: 824KB  **date**: 2026-11-12 ~ 2026-11-17

## 用户真实意图（trace verbatim）

zhenglu 在 `/home/zhenglu/HL_hspice/` 下有一份加密的 HSPICE PDK 模型库
（`hlmc_cl022ul_spice_v0p5_0d13_for_vodka_*.lib.enc1.decrypt`），正在研究 Synopsys hspice
自带的 `metaencrypt` 工具的加密格式。trace 是一个长 Q&A + 动手实验 session，主要用户原话：

- U[0]「/home/zhenglu/HL_hspice 这个目录下的文件可以梳理下吗」
- U[15]「你能解密这些加密文件吗」
- U[17]「我给你个思路 就是可以去软件包nm objdump查找软件包内部的密钥」
- U[29]「...这个文件什么格式」
- U[42]「...看起来是个压缩文件试试各种解压缩的方式如zlib bzip等」
- U[56]「这个项目是做什么的给我一个readme描述一下」
- U[62]「hpice如何加密lib和sp sp和lib有什么区别吗」
- **U[64]/U[69]「你帮我写个简单的lib然后用当前的版本的metaencrypt 做key的加密 创建一个工作目录在我的家目录下」** ← 主交付任务
- U[139]「/apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/linux64/metaencrypt 解析这个elf文件的常量哪些可能是密钥」
- U[147]「你用下-z对比一下输出的内容和大小还有没有开头的.PROT」
- U[151]「大概是用的什么压缩zlib吗」
- U[181]「private key都是33字节吗」← 关键发现：.key 文件 33 字节
- U[219]「gdb 运行那个metaencrypt看下调用栈」

## agent 工具链 / 产物

agent 共 25+ 次 `run_approved_command`，产出脚本（在 `/home/zhenglu/metaencrypt_demo/`）：
- `do_encrypt.py` (1498B) —— **主交付**：写 `my_devices.lib` → 调 `metaencrypt -i <lib> -o <out> -t privkey <48B-hex-key>` 加密
- `do_encrypt_z.py` (1545B) —— 加 `-z` 压缩对比
- `test_keylen.py` (1738B) —— 探测 key 长度（32/48/64/96/128 字符）
- `test_keypath.py` (797B) —— key 文件路径
- `test_after_key.py` (1901B), `analyze_z.py` (2162B), `test_combos.py` (2203B), `export_hex.py` (1282B)
- `libs/my_devices.lib` (731B, trace-verbatim: tt_demo + ss_demo 两角, resxy/capxy subckt, nmos_t/pmos_t/nmos_s/pmos_s models)
- `libs/my_devices.lib.enc` (880B, header `.PROT PRIVKEY $Metaencrypt U-2023.03-SP1-2 <timestamp>`)
- `libs/my_devices.lib.enc.key` (33B binary)

## 真实任务 = produce one-off script（U[69]）

用户要的是「写一个简单 lib + 用 metaencrypt 做密钥加密 + 建工作目录」。agent 完整交付了
`do_encrypt.py`（参数化程度低，但功能完整：写 lib + 调真实 metaencrypt + 建工作目录 + 列输出）。

## reframe 决策

- **形态**：debug-Q&A + one-off script → produce（harness-for-teeth reframe，与 r871/r872/r879 同模式）
- **判分有牙**：参数化 .lib 生成 + 确定性可逆模拟加密（round-trippable）+ manifest 含真实 metaencrypt 命令行
- **asset A**：trace-verbatim `my_devices.lib`（format-faithful, tt/ss 两角）+ task_spec + expected_manifest_A
- **hidden B**：全维度差异（lib_name io_devices / PVT ff:3.3:io,tt:2.5:io5 / key FEDCBA... / metaencrypt /proj/shdc/... / use_z true）
- **k_check = k_rationale = 15**（a-o，含 anti-hardcode-A + determinism + round-trip + anti-stub）
- **5 neg 全 FAIL** NEG_RC=5/5（empty/print_expected/hardcoded_a/core_deleted/always_stub）
- **layer L1**：纯 python 文本/二进制流处理，无 EDA 仿真运行

## 为什么之前被 parked（reaudit 复活）

台账 parked note (r481 peek 2026-11-13 09:29)：「non-B mislabel: PDK HL_hspice model library usage guide + example deck gen, hspice kw=355 from reading .lib files not sim run, no run_approved_command」。
**这条 parked note 是错误的**——深读 trace 显示有 25+ 次 `run_approved_command`（do_encrypt.py 等真实运行），且 U[69] 是明确的 produce 交付任务（不是 analysis-only）。按 2026-11-15 用户令重审，旧 weak-filter 误杀的候选应全部复活。本 case 即复活实证。

## metaencrypt 真实格式（trace 实证）

- 加密文件头：`.PROT PRIVKEY $Metaencrypt U-2023.03-SP1-2 <MM-DD-YYYY HH:MM:SS>\n` + 二进制 body
- `.key` 文件：33 字节二进制（key 派生指纹，非明文 key）
- 真实命令：`metaencrypt -i <lib> -o <enc> -t privkey <48B-hex-key> [-z]`
- `-z` 触发 zlib 压缩
- metaencrypt 在 .75 上有多个版本：`/apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/bin/metaencrypt`、`/proj/shdc/cad/script/bin/metaencrypt` 等

本 case 的模拟加密格式 `METAENC_SIM_V1\n + base64(zlib(lib) XOR repeating-key)` 是为判分可逆而设计的简化格式，与真实 metaencrypt 格式不同；manifest 同时给出真实 metaencrypt 命令行供用户在真实环境运行。
