# vision VQA SSH bridge — 方案与实测 (任务书 §2026-11-15 07:2x 任务①)

> 生成: 2026-11-15 08:3x · vision 线 (.17=10.252.32.17) · 落盘证据见 `run/vision_ssh_bridge_proof.txt`

## 1. 问题

评测跑在 36.15(hfeg0tedaap02), VQA 服务在 .17(:30001 基模 / :30002 MCP / :30003 +rft2_adapter)。
36.15 → .17 的 TCP(22/30001/30002/30003) 全超时; 运维不会再放行, **只保证 .17:3333 ↔ 36.15 的 SSH**。
=> 由 vision 自己基于 SSH 建通道。判分/防作弊全不变, 只换传输层。

## 2. 方案选择 (择优 + 理由)

选 **SSH 反向端口转发 + 本地 TCP forwarder 暴露给容器** (任务书选项1+2 合体):

- **反向转发**(`ssh -R`, 跑在 .17): `ssh -p 3333 -N -R 127.0.0.1:1300x:127.0.0.1:3000x app.e0031982@localhost`
  在 36.15 loopback 开 13001/13002/13003 → 转发回 .17 的 30001/30002/30003。
  理由: 36.15 不可达 .17, 但 .17 可经 :3333 隧道登录 36.15; `-R` 把端口「开在 36.15 侧」,
  正好让 36.15 评测进程就近访问。`GatewayPorts` 不需要(只需 loopback + 网关)。
- **forwarder**(`/tmp/vqa_fwd2.py`, 跑在 36.15): `0.0.0.0:3000x → 127.0.0.1:1300x`。
  理由: 反向转发只绑 36.15 loopback(127.0.0.1:1300x); 评测容器(bridge 网络)走 docker0 网关
  10.247.64.1 访问宿主, 故再起一个 0.0.0.0:3000x 转发, 让容器经网关 IP 命中。
  (`--network host` 容器则直接用 127.0.0.1:3000x。)

未选 HTTP-over-SSH 桥(选项3): 当前三端口已是干净 HTTP/MCP, 反向转发+forwarder 更简单且抗断
(watchdog 秒级重连); 选项3 留作退化路径。

## 3. 断线自愈

`vision/vqa_tool/vqa_ssh_bridge_watchdog.sh` (跑在 .17, setsid detached):
```bash
while true; do
  ssh -p 3333 -N -o BatchMode=yes -o ExitOnForwardFailure=yes \
      -o ServerAliveInterval=15 -o ServerAliveCountMax=3 \
      -R 127.0.0.1:13001:127.0.0.1:30001 -R 13002:...30002 -R 13003:...30003 \
      app.e0031982@localhost
  sleep 5   # 退出后 5s 重连

done
```
日志 `/tmp/vqa_ssh_bridge_watchdog.log`。实测: 杀 ssh -R 子进程 → `[exited] rc=0` → 6s 后 `[launch]` →
1300x 重新 LISTEN, /health 恢复 ok(见 proof §5)。forwarder(vqa_fwd2.py)本身常驻, 隧道断时它仅转发失败,
隧道一恢复即恢复, 无需重启。🚫 不建一次性连接。

## 4. 三方证据 (实测, 详见 proof.txt)

| 视角 | 30001/health | 30002(MCP initialize) | 30003/health |
|:--|:--|:--|:--|
| 36.15 宿主 (127.0.0.1:1300x) | ok Qwen3.5-2B | protocolVersion 2024-11-05 + tools | ok +rft2_adapter |
| 评测容器路径 (10.247.64.1:3000x) | ok | initialize 成功 | ok |
| 断线重连后 | ok | — | ok |

容器内 `docker run` 因 app.e0031982 不在 36.15 docker 组(sudo 需密码)无法执行;
以 docker0 网关 IP(容器实际走的地址)curl 三端口全 ok 替代, 并已诚实标注。

designflow 评测 harness `run_one_D.sh` 实为 36.15 宿主 headless 跑 cline + PreToolUse hook(非容器隔离),
故宿主/网关视角即评测视角。

## 5. VQA tool 真实可用 (桥接后从 36.15 调 VQA 答对真题)

从 36.15 经桥对真实 WaveView-002 `wv_sigs_A.png`(5 路堆叠信号)提问:
- `http://10.247.64.1:30001/vqa` → `{"ok":true,"answer":"5","elapsed_s":0.473}`
- `http://127.0.0.1:13001/vqa` → `{"ok":true,"answer":"5","elapsed_s":0.465}`

answer="5" = 真题正确值。=> VQA tool 在评测环境里真的可用。

## 6. image_path 口径 (跨机 NFS 差异)

36.15 与 .17 **不挂同一 NFS inode**: .17 的 `/nas_data/...` 在 36.15 不存在(`/nasdata/...` 是 36.15 本地)。
故评测侧若调 VQA, image_path 需传 **.17 服务端可读**的路径; 真题 PNG 已只读复制到
`run/vision/real_waveview_images/<case>/<png>`(共享 NFS, .17 可读; 36.15 经 git 同步可见)。
MCP `vqa(image_path=<绝对路径>, query=...)` 同理。🚫 不传 base64(防作弊口径不变)。

## 7. 复现命令

```bash
# .17: 起带自愈的桥
setsid bash vision/vqa_tool/vqa_ssh_bridge_watchdog.sh > /tmp/vqa_ssh_bridge_watchdog.out 2>&1 < /dev/null &
# 36.15: 起 forwarder(已常驻, 若需重启)
nohup python3 /tmp/vqa_fwd2.py > /tmp/vqa_fwd2.log 2>&1 &
# 验证(36.15)
curl -sS http://127.0.0.1:13001/health
python3 -c 'import urllib.request,json;print(urllib.request.urlopen(urllib.request.Request("http://10.247.64.1:30001/vqa",data=json.dumps({"image_path":"<abs>","question":"..."}).encode(),headers={"Content-Type":"application/json"})).read())'
```
