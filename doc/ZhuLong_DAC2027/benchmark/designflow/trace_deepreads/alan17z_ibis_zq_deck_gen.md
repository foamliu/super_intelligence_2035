# deepread — alan17z@hfeg0plg10 IBIS ZQ 校准 deck 生成 (1795000059890_2xqbx)

- session: `1795000059890_2xqbx` · user `alan17z` · host `hfeg0plg10` (172.16.8.176) · mc=145
- keywords: hspice:571; netlist:248; waveview:36; synopsys:36; aether:13 (spice-dominant, ratio 0.62)
- 169 msgs, 613KB messages.json

## 用户真实意图（原话）
1. (msg0, 经 skill-creator 命令) "你能找到跟抽ibis相关的skill吧"
2. (msg56) "你能读到/rundata/SIPI/alanzhang/SI/1_IBIS_extract下的AI_try文件夹吧…先干到ZQ校准文件生成，然后通过 bsub -q SIPI 'source /rundata/SIPI/setup.sh; hspice {sp路径} -o {lis}' 指令运行一个ZQ校准文件，提取出ZQ校准码为止，让我确认"
3. (msg73) "不用确认source文件里除了stimulus之外的内容，默认这部分是正确的，继续进行即可"
4. (msg121) 给出精确 bsub 命令 "bsub -q SIPI 'source /rundata/SIPI/setup.sh; hspice /rundata/.../pdt_rpd40_pre_ff -o /rundata/.../result'"

## agent 做了什么
- 找到 3 个 IBIS skill (ibis-t2b-gen / ibis-zq-sim-gen / ibis-zq-calib)，读完，提议合并为 `ibis-extract`
- 写 `run_sims.py`（直接在服务器跑 hspice，替代旧的"拷去平台跑"断点）
- **关键修正**：给 `gen_zq_decks.py` 加 RCC 文件名自动发现 —— 实源是 `DqFinalDrvNAM6IP.spf.TYP_98_RCC`，旧 skill 硬编码 `DqOutTopM6IP.spf.TYP_98_RCC` 会跑不通
- 造合成测试场景验证 gen→check→run_sims(--dry-run)→merge_zq 全链路
- 在 AI_try/zq_run 下用真实 corner.txt + 真实 Tx stimulus 生成 6 个 ZQ deck，check_decks 全 PASS，run_sims --dry-run 6 个 deck 全发现
- bsub 提交 hspice job（job EXIT，hspice 启动失败，user 给精确命令后仍 EXIT，诊断 hspice 可达性中 —— 会话在此处进行）

## 合成 case 取哪一段
取"ZQ 校准文件生成"段 → produce 参数化 `gen_zq_decks.py`：
- 输入：corner.txt（多 corner block：.temp/.lib/.param pv*）+ stimulus（电源 on 段）+ 运行目录里 RCC 文件
- 自动发现 RCC 文件名（不硬编码）
- 输出 6 个 hspice sweep deck（3 corner × PU/PD），每个 deck 对 ZQ 码 0..63 做 .dc sweep + .measure 测电阻

## "有牙"判分设计
- 隐藏 B：电压不同（pvcc=0.95 vs A 的 0.89）、信号名不同（VPWRUP vs VPUPMOSENN/VSWEN2）、RCC 文件名不同（DqFinalDrvNAM6IP... vs DqOutTopM6IP...）
- 5 负样本全 FAIL：empty_shell / print_expected / naive_hardcode_a（硬编码 A 值）/ core_deleted（删 .dc sweep）/ no_rcc_discovery（硬编码 A 的 RCC 名）
- 12 断言 (a-l)，3 随机种子各抽 4 deck 深检
- ref 12/12 PASS，NEG_RC=5/5

## trace-faithful 要点（写进 prompt）
- 真实用户名 alan17z / 真实路径 /rundata/SIPI/alanzhang/SI/1_IBIS_extract/AI_try / 真实源文件名 model.sp/incFile_lp/stimulus/DqFinalDrvNAM6IP...RCC
- 真实 bsub 命令原话
