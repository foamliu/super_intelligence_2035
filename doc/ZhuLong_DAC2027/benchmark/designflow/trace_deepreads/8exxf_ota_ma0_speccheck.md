# Deepread: 1792573529929_8exxf (zhukaic / hfeg0plg58, mc=24, spice_sim)

**Date**: 2026-11-13 r472
**Session**: 36 msgs, 21 user turns
**Source host**: 10.129.35.82 (hfeg0plg58)

## User intent
zhukaic 使用 cline agent 的 `/workspace-upload` skill 将两级 OTA（`ota_2stg_sim`）的 HSPICE 前仿测量数据文件 `ota_2stg_sim.ma0_data.md` 上传到 Workspace 平台（workspace.cxmt.com）。

## Trace flow
1. **U0**: `/workspace-upload` 上传 `ota_2stg_sim.ma0_data.md`
2. **A1-A12**: agent 寻找 upload 脚本（`find_ws_script.py` 超时被 SIGKILL），通过 `list_allowed_files` 发现 `/home/zhukaic/.cline/skills/workspace-upload/scripts/upload_to_ws.py`
3. **A22**: 首次上传失败 — AK 权限错误（code=84107017: AK 未加入项目 549894522386034750）
4. **A27-A28**: 列目录也失败（同权限问题）
5. **A29**: agent 反馈失败原因（AK 认证通过但项目未授权）
6. **U30**: 用户再次执行同一上传命令
7. **A33-A35**: 第二次上传成功（doc_id=550004378822537267），权限已生效

## Key artifact: ota_2stg_sim.ma0_data.md
两级 OTA HSPICE 前仿测量数据（PrimeSim HSPICE V-2023.12-SP1-1, temp=85°C, vcc!=1.025V）：

| 字段 | 含义 | 值 |
|---|---|---|
| gain | 低频开环增益 | 55.776202 dB |
| pm | 相位裕度 | 80.722124° |
| gbw | 单位增益带宽 | 973.293 kHz |
| f_3db | -3dB 带宽 | 1.81897 kHz |
| gain_margin | 增益裕度 | -44.448713 dB |
| psr_min | PSR(最差) | -6.625865 dB |
| psr_dc | PSR(DC) | -70.390492 dB |
| temper | 仿真温度 | 85.0°C |
| alter# | 参数编号 | 1 |

## Case 化决策
- **Domain**: spice_sim（HSPICE .ma0 测量数据解析 + 指标合规判定）
- **Layer**: L2（真跑 subprocess 在隐藏 B 上执行候选 parser，非纯文本匹配）
- **A 档 trace-faithful**: 使用真实 .ma0 数据作可见输入 A
- **Hidden B**: 3-corner post-layout .ma0（−40°C/27°C/125°C），不同数值/不同 spec，alter#3 故意 FAIL（gain<45 & GBW<400k）
- **check.py**: 12 条独立断言（a-l），真跑 parser 在 A+B 上，逐值校验 + malformed 拒绝 + 报告格式
- **自验**: ref 12/12 PASS, 2 neg + 3 §4.9 fake 全 FAIL
