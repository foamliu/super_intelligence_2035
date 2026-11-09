# app/ · 家教机器人 Android 客户端（Kotlin + CameraX + 系统 TTS）

> 22:50 用户令：做**可安装的真 App**（不再是 PC demo）。本目录是手机端工程，
> 交付**可安装 APK**（debug 签名）+ 安装运行说明 + 模拟器录屏。
> 红线：不代写作业（App 只显示/朗读「分步引导」，最终答案由服务端硬约束不给）。

## 能力（闭环）

拍照 / 选图 -> 降采样 -> base64 -> `POST http://10.0.2.2:8765/tutor`（PC 侧 `host/tutor_server.py`）
-> 收到 `{reply_text, tts_text, question_text, ...}` -> 屏幕显示 + 系统 TTS 朗读 -> 「打断」按钮停播。

第 16 轮新增 **L2 工具 / 追问**（对应 host 侧 `POST /tool`、`POST /agent`）：
- 「换一题」→ `/tool question_bank`；「记错题」→ `/tool wrong_book_add`；「报告」→ `/tool parent_report`；
- 文字输入框 + 「发送」→ `/agent`（多轮追问，无题干时回退 `/tutor` 文字题）。

第 17 轮新增 **L3 学情**（对应 host 侧 `POST /profile`）：
- 「学情」→ `/profile`，显示「错题总数 / 涉及知识点 / 薄弱点」（本地错题本画像，不上传、不泄答案）。

第 19 轮新增 **L3 正样本（作答对错）**（对应 host 侧 `POST /practice`）：
- 「答对」「答错」→ `/practice`，记录一次作答（作答次数 / 正确率）；
- 「学情」升级为**合并画像**：错题（负样本）+ 作答（正样本）→ 显示「错题总数 / 练习次数 / 涉及知识点 / 薄弱点 / 作答摘要」，掌握等级新增「已掌握」。

第 20 轮新增 **语音打断（barge-in）+ 静音真关麦 + 常听态指示**（对应 host 侧 `vad.py`）：
- 新增 `MicVad.kt`（`AudioRecord` 16kHz 端侧 VAD），朗读中检测到人声 → 自动停播（语音打断）；
- 「静音」按钮 = 真关麦（释放 AudioRecord），不是软件忽略；
- 顶部状态指示（常听/听/说/静音）对齐 INTERACTION_SPEC §3 状态机；需 `RECORD_AUDIO` 权限。

## 技术栈

| 项 | 选型 |
|:--|:--|
| 语言 | Kotlin 1.9.24 |
| 构建 | Gradle 8.7 + Android Gradle Plugin 8.4.2 |
| SDK | compileSdk 34 / minSdk 26 / targetSdk 34 |
| 相机 | CameraX 1.3.4（拍照 / 预览） |
| 选图 | Activity Result `GetContent` |
| 网络 | 系统 `HttpURLConnection` + `org.json`（零第三方依赖） |
| TTS | 系统 `TextToSpeech`（端侧，中文 `Locale.CHINA`，可 `stop()` 打断） |

## 目录

```
app/
├── settings.gradle.kts / build.gradle.kts / gradle.properties
└── app/
    ├── build.gradle.kts
    └── src/main/
        ├── AndroidManifest.xml
        ├── java/com/personalwatch/robot/MainActivity.kt / TutorClient.kt
        └── res/ (layout / values / drawable / mipmap)
```

## 构建（本机已装 JDK 17 + Android SDK，见 `C:\Android`）

```powershell
# 环境变量（SYSTEM 账户 PATH 不可靠，用绝对路径）
$env:JAVA_HOME = 'C:\Android\jdk17\jdk-17.0.16+8'
$env:ANDROID_HOME = 'C:\Android'
$env:ANDROID_SDK_ROOT = 'C:\Android'
# 直连（本机系统代理 127.0.0.1:7897 对 Gradle 拉依赖会卡死，必须清掉）
$env:HTTP_PROXY = $null; $env:HTTPS_PROXY = $null; $env:http_proxy = $null; $env:https_proxy = $null

cd D:\Users\Administrator\code\super_intelligence_2035\doc\personal-watch\run\robot\app
& 'C:\Android\gradle-8.7\bin\gradle.bat' --no-daemon :app:assembleDebug
```

产物：`app/build/outputs/apk/debug/app-debug.apk`。

## 安装到模拟器

```powershell
& 'C:\Android\platform-tools\adb.exe' install -r app\build\outputs\apk\debug\app-debug.apk
& 'C:\Android\platform-tools\adb.exe' shell am start -n com.personalwatch.robot/.MainActivity
```

## 运行前提

1. PC 侧先起服务：`py -3.10 -W ignore host\tutor_server.py`（监听 0.0.0.0:8765）。
2. 模拟器内 App 默认服务地址 `http://10.0.2.2:8765`（`10.0.2.2` = 宿主 PC，**不是** 127.0.0.1）。
3. 模拟器无摄像头时点「选图」，把 `eval/*.png` 题图推入模拟器相册（`adb push` + 媒体扫描）。

## 模拟器能信 / 不能信（防止把模拟器结论当真机结论，22:30 令 §3）

| ✅ 可作证据 | 🚫 必须真机复测 |
|:--|:--|
| App UI/状态机流转、拍照/选图→上传→引导→朗读的功能闭环 | 真实语音打断（AEC 自听回声，模拟器音频链路不同） |
| WebSocket/HTTP 协议正确性、录屏过程证据 | 首字时延真实值、端侧 ASR/TTS 真实 CER 与音色 |
| 权限/异常路径 | 华为 Kit 在真机的可用性、热与功耗 |

## 红线自检

- 服务端 `host/tutor_server.py` 复用 `tutor_agent.py` 的 `TUTOR_SYSTEM`（不代写、只分步引导）；
- 题图上云默认走 DeepSeek（学生题目外发，可切纯本地 `ROBOT_VISION_BACKEND=ollama`）；
- 密钥只在 PC 侧 `secrets.json`/环境变量读取，**App 与仓库不含任何 key**。
