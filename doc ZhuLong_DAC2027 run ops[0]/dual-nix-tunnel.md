# dual-nix-tunnel

使用 Windows 11 作为 SSH 中继，打通两台 Linux 服务器之间的通信隧道。

## 网络拓扑

```
                          Windows 11 (本机)
                       172.19.195.133  (IPv4)
                       ┌─────────────────┐
                       │  tunnel.ps1     │
                       │  ssh -R 2222    │── SSH 隧道 ──┐
                       │  ssh -R 3333    │── SSH 隧道 ──┤
                       └─────────────────┘              │
                              │ SSH                     │
            ┌─────────────────┼─────────────┐           │
            ▼                 │              ▼           │
   ┌──────────────┐          │    ┌──────────────┐      │
   │  Server 1    │          │    │  Server 2    │      │
   │ 10.251.36.15 │          │    │ 10.252.32.17 │      │
   └──────┬───────┘          │    └──────┬───────┘      │
          │                   │           │              │
          │  localhost:2222 ──┘           │  localhost:3333
          │  → Server2:22                │  → Server1:22
          └───────────────────────────────┘
```

## 运行条件

- 本机: Windows 11 系统，已安装 OpenSSH 客户端（系统自带 `C:\Windows\System32\OpenSSH\`）
- SSH 密钥: 已在 `~/.ssh/id_ed25519` 配置 SSH 密钥对
- 服务器: 两台 Linux 服务器均可从本机通过 SSH 密钥登录
  - Server 1: `10.251.36.15` (用户: `app.e0031982`)
  - Server 2: `10.252.32.17` (用户: `app.e0031982`)
- 网络: 两台服务器之间的 SSH 端口(22)被防火墙阻挡，但 ICMP(Ping) 互通

## 快速开始

### 1. 启动隧道

以管理员身份打开 **PowerShell**，进入项目目录，执行：

```powershell
.\tunnel.ps1
```

启动后会自动建立两个 SSH 反向隧道：
- 隧道 1: Server 1 监听 `localhost:2222` → 本机 → Server 2 `:22`
- 隧道 2: Server 2 监听 `localhost:3333` → 本机 → Server 1 `:22`

### 2. 检查隧道状态

```powershell
.\tunnel.ps1 -Status
```

### 3. 停止隧道

```powershell
.\tunnel.ps1 -Stop
```

## 服务器间 SSH 通信

### Server 1 → Server 2

在 **Server 1**（10.251.36.15）上执行：

```bash
ssh -p 2222 app.e0031982@localhost
```

### Server 2 → Server 1

在 **Server 2**（10.252.32.17）上执行：

```bash
ssh -p 3333 app.e0031982@localhost
```

### 传输文件（SCP）

从 Server 1 复制文件到 Server 2：

```bash
scp -P 2222 /path/to/file app.e0031982@localhost:/path/to/destination/
```

从 Server 2 复制文件到 Server 1：

```bash
scp -P 3333 /path/to/file app.e0031982@localhost:/path/to/destination/
```

## 技术架构

### SSH 反向隧道原理

```
Server 1 (10.251.36.15)         本机 Windows               Server 2 (10.252.32.17)
─────────────────────────      ────────────────           ─────────────────────────

端口 2222 监听 ←──── ssh -R ─── SSH 连接 ──────────────── 发起连接 → 端口 22
localhost:2222                 2222→10.252.32.17:22

                               SSH 连接 ──── ssh -R ───→   端口 3333 监听
                               3333→10.251.36.15:22       localhost:3333
```

- `-R <remote_port>:<target_host>:<target_port>`: 在远程服务器上监听端口
- 连接到达远程端口后，数据通过 SSH 隧道传回本机
- 本机再作为客户端连接到目标服务器完成通信

### 自动重连

隧道包含 `ServerAliveInterval=30` 和 `ServerAliveCountMax=3` 参数，连接断开时会自动检测。

### 日志

隧道日志保存在同目录下的 `tunnel.log` 文件中。

## 文件说明

| 文件 | 用途 |
|------|------|
| `tunnel.ps1` | 隧道启动/停止/状态检查脚本 |
| `askpass.bat` | SSH 密码辅助（用于 Server 2 的初始密钥部署） |
| `deploy_key.ps1` | 部署 SSH 公钥到服务器的辅助脚本 |
| `tunnel.log` | 隧道运行日志（自动生成） |
| `tunnel.pid` | 隧道进程 PID 记录（自动生成） |
