# Trace Deep-read — hxfhy (VTH override how-to Q&A)

- **session**: 1793264956869_hxfhy.messages.json
- **user / host**: jasminej @ hfeg0plg52
- **match_count**: 14 (1115 scan)
- **agent**: lead
- **trace size**: 134 KB / 24 msgs
- **substantive user turns**: 1
- **domain**: spice_sim
- **旧判定**: parked (r375, 旧判 debug-Q&A)
- **重审**: r694 复活 (#73, 11-15 用户令 reaudit 182 真可造变现)

## 用户真实意图（verbatim）

msg 0 (user):
> 「./v0p12/hlmc_cl022ul_io25_spice_v0p12_0d10_for_vodka_shrink0d855.lib访问这个lib，在.sp中如何才能重新定义阈值电压值？」

意图：访问一个 IO Pad SPICE 库后，在 `.sp` 网表中重新定义阈值电压值。属 **how-to Q&A**（SPICE 模型参数覆盖操作指南）。

## agent 行为摘要

1. msg1-4: 尝试 find/list_allowed_files 定位 lib 文件 → run_commands 被策略禁用，list_allowed_files 只列出 /home/jasminej 下文件。
2. msg7-13: search_codebase 超时；read_files 读 .sp 文件失败；写 find_lib.py 遍历 /home/jasminej 找 lib → TOTAL: 0（lib 不在工作站上）。
3. msg14-19: 查 agent-policy 状态；写 find_lib2.py 扩大搜索到 /proj /rundata /data /models /tmp → python-runner 超时被 SIGKILL。
4. msg20-22: 尝试 fetch_web_content（被策略禁）+ search_codebase（JSON 解析失败）。
5. msg23 (最终答案): 无法在本机读取 lib 内容，但基于 BSIM4 通用格式给出 how-to 指南：
   - 关键点：vth0 是模型参数（非全局 .param）；直接 `.param vth0=0.4` 无效；用同名 `.MODEL` 覆盖（model parameter override）。
   - 方法1（最常用）：`.lib` 引用后追加同名 `.MODEL` 卡覆盖 vth0（全局生效）；模型名须与网表实际用名一致，level 须一致，PMOS vth0 为负。
   - 扫多 VTH 点：`.param myvth=0.4` + `.step param myvth 0.35 0.45 0.01` 或 `.alter` 分 corner。
   - 方法2：单器件 M 实例行追加 `vth0=0.44`（仅 M 器件有效，X 子电路不可）。
   - 坑：模型名必须匹配 / level 须一致 / PMOS vth0 负 / 查 .lis 模型回显验证 / 加密库读不到名 / vth0 vs vdsth0。
   - 仿真器：HSPICE / FineSim，BSIM4 level 14/54。

## 合成决策

- 形态：how-to Q&A → 产出生成式结构化指南（produce-deliverable，使 check 有牙）。
- A 档 trace-faithful：用真实用户原话 + 真实 lib 路径/器件/仿真器作 A 场景。
- 交付：`vth_override_guide_generator.py(workdir, out_dir)` 读 `input_manifest.json` 产 `vth_override_guide.json`（11 顶层键）。
- cross-input guard：A=HSPICE/IO Pad/X subcircuit/level54；hidden B=Spectre/Core Logic/M direct/level14。关键区分：instance_level_param.applicable 在 A(X)=False / B(M)=True，simulator 语法随输入变。
- check：21 断言（a0-a20），含 cross-input guard + A-leak + B-grounding + 确定性 + 4 假提交。
- 自验：ref 21/21 PASS，4 negs 全 FAIL。

## case_id
EDA-Eval-DesignFlow-VthOverrideHowtoGuide-001
