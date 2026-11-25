# LLM 额度/鉴权自动轮换 — personal-watch 接入方案

> **为什么需要**：2026-10-04 09:31 → 10-05 12:20，**personal-watch 两条线静默 ≈27 小时**（同期 BaiZe/ZhuLong 全线正常）。
> 最可能原因 = **LLM 额度/鉴权**（BaiZe 现场实测：`deepseek-v4-pro-fp4` → **429 额度耗尽**，其余 7 个 → 200；**base 必须与模型匹配**：`deepseek-v4-flash@/v1`=200 但 `@/cloud/v1`=**403**）。
> ⚠️ 而我们 loop 里的"失败兜底"（命中致命特征 → **60s 短睡重试**）会把这种情况变成 **"静默空转、零产出"** —— 不丢东西，但**没有任何可观测性**。

## 0. 前置：先确认是不是额度问题（**别急着改**）

在运行机上：
```bash
cd ~/super_intelligence_2035/doc/personal-watch/run
pgrep -af 'watch_(news|research)_loop.sh'          # 进程在不在
tail -30 /tmp/watch_news_loop.log
tail -30 /tmp/watch_research_loop.log              # 找 "额度已用完" / "403" / "429"
```

## 1. 复用 BaiZe 的现成 helper（**它已经踩平了坑**）

`llm_rotate.sh` 由 BaiZe 线交付（`doc/BaiZe-ISEDA2027/run/llm_rotate.sh`，112 行），提供：

| 函数 | 作用 |
|:--|:--|
| `llm_parse_candidates <keys.txt>` | 解析 `doc/keys.txt` → 8 个 chat/coding LLM（**排除 ASR / 文生图**） |
| `llm_probe <base> <key> <model>` | 探针 → `200` 可用 / `429` 额度 / `403` base 不匹配 |
| `llm_pick <state_file> <keys.txt>` | **挑第一个可用者**，设 `LLM_MODEL` / `LLM_KEY`，并在 base 不同时**改写** `~/.cline/data/globalState.json` 的 `openAiBaseUrl`（**自动备份 `.llmrot.bak`**） |

> 🔑 **关键事实**（BaiZe 实测，省得我们再踩）：cline 的 LLM base 来自 **`~/.cline/data/globalState.json` 的 `openAiBaseUrl`**，
> **不是** env `CLINE_API_BASE_URL`（那是 Cline 平台自己的 API）。

## 2. 建议做法：**复制**到本线（不跨线引用，保持两线独立）

```bash
cp doc/BaiZe-ISEDA2027/run/llm_rotate.sh doc/personal-watch/run/llm_rotate.sh
```

## 3. 补丁（对 `watch_news_loop.sh` / `watch_research_loop.sh` 各一处）

**改前**（现状）：
```bash
        prompt="$(< "$TASK_MD")"
        cline -c "$CWD" --auto-approve true -m "$MODEL" -t "$CLINE_TIMEOUT" --thinking "$THINKING" "$prompt" < /dev/null 2>&1 | tee "$CLINE_LOG"
```
**改后**：
```bash
        prompt="$(< "$TASK_MD")"
        # 额度/鉴权体检 + 自动轮换（BaiZe llm_rotate.sh）
        if llm_pick "$LLM_STATE" "$KEYS_TXT"; then
            cline -c "$CWD" --auto-approve true -m "$LLM_MODEL" -k "$LLM_KEY" -P openai-compatible \
                  -t "$CLINE_TIMEOUT" --thinking "$THINKING" "$prompt" < /dev/null 2>&1 | tee "$CLINE_LOG"
        else
            echo "[loop] $(date '+%F %T') ⚠️ 无可用 LLM（全部 429/403）—— 本轮跳过"
            FORCE_SHORT=1
        fi
```
**并在脚本顶部**（`MEMORY=` 附近）加：
```bash
KEYS_TXT="$GIT_ROOT/doc/keys.txt"
LLM_STATE="/tmp/watch_news_llm_idx"          # research 线改成 watch_research_llm_idx
. "$SCRIPT_DIR/llm_rotate.sh"
```

## 4. ⚠️ 两个注意

1. **改 `loop.sh` 必须重启 loop 才生效** —— 且**同一条 loop 不要"边跑边改"**（bash 增量读取脚本，行为未定义）。→ **先 `pkill`，再改，再启动**。
2. **跨线干扰风险**：`llm_pick` 会改写 **全局** `~/.cline/data/globalState.json` 的 `openAiBaseUrl`。
   若 personal-watch 与 BaiZe **跑在同一台机、同一个 HOME**，两边的轮换**会互相改 base** → 可能"我改好你又改回去"。
   → **缓解**：给本线加 `--config <独立目录>` / 用独立 HOME；或**把轮换的 state file 分开**（`/tmp/watch_*_llm_idx`，已按线命名）。

## 5. 与「心跳」的分工（**两者都要**）

| 机制 | 解决什么 | 落点 | 是否需重启 |
|:--|:--|:--|:--|
| **心跳**（已在任务书 §快照 强制） | **可观测性**：静默期能区分"在跑 / 停了" | 任务书（agent 每轮写一行） | ❌ **不需要**（下一轮生效） |
| **llm_rotate** | **可用性**：额度耗尽**自动换 LLM**，不再空转 | loop.sh | ✅ **需要重启** |

> 心跳先上（零成本、立刻能诊断）；llm_rotate 在工作时段重启时一并接上。
