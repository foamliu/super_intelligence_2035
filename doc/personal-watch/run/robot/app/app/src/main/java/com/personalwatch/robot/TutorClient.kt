package com.personalwatch.robot

import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL

/**
 * 与 PC 侧 host/tutor_server.py 通信的轻量客户端（零第三方依赖，用系统 HttpURLConnection + org.json）。
 * 模拟器内访问宿主 PC 用 http://10.0.2.2:8765 。
 */
data class TutorReply(
    val replyText: String,
    val ttsText: String,
    val questionText: String?,
    val step: Int,
    val hintLevel: Int,
    val needs: String?,
    val latencyS: Double?,
    val raw: String
)

data class ToolReply(
    val ok: Boolean,
    val reply: String,
    val error: String,
    val raw: String
)

data class AgentReply(
    val kind: String,
    val tool: String?,
    val reply: String,
    val raw: String
)

object TutorClient {

    fun postTutor(
        baseUrl: String,
        imageB64: String?,
        text: String?,
        history: List<Pair<String, String>> = emptyList()
    ): TutorReply {
        val conn = URL(baseUrl.trimEnd('/') + "/tutor").openConnection() as HttpURLConnection
        conn.requestMethod = "POST"
        conn.doOutput = true
        conn.connectTimeout = 30_000
        conn.readTimeout = 90_000
        conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")

        val body = JSONObject()
        if (!imageB64.isNullOrEmpty()) body.put("image_b64", imageB64)
        if (!text.isNullOrEmpty()) body.put("text", text)
        val hist = JSONArray()
        for ((s, a) in history) {
            hist.put(JSONArray().put(s).put(a))
        }
        body.put("history", hist)

        OutputStreamWriter(conn.outputStream, Charsets.UTF_8).use { it.write(body.toString()) }
        val code = conn.responseCode
        val stream = if (code in 200..299) conn.inputStream else conn.errorStream
        val resp = stream?.bufferedReader(Charsets.UTF_8)?.use(BufferedReader::readText) ?: "{}"
        conn.disconnect()
        return parse(resp)
    }

    fun health(baseUrl: String): String {
        val conn = URL(baseUrl.trimEnd('/') + "/health").openConnection() as HttpURLConnection
        conn.requestMethod = "GET"
        conn.connectTimeout = 10_000
        conn.readTimeout = 10_000
        val code = conn.responseCode
        val resp = conn.inputStream?.bufferedReader(Charsets.UTF_8)?.use(BufferedReader::readText) ?: "{}"
        conn.disconnect()
        return "HTTP $code $resp"
    }

    fun postTool(baseUrl: String, tool: String, params: Map<String, String>): ToolReply {
        val conn = URL(baseUrl.trimEnd('/') + "/tool").openConnection() as HttpURLConnection
        conn.requestMethod = "POST"
        conn.doOutput = true
        conn.connectTimeout = 30_000
        conn.readTimeout = 30_000
        conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")

        val body = JSONObject()
        body.put("tool", tool)
        val p = JSONObject()
        for ((k, v) in params) p.put(k, v)
        body.put("params", p)

        OutputStreamWriter(conn.outputStream, Charsets.UTF_8).use { it.write(body.toString()) }
        val code = conn.responseCode
        val stream = if (code in 200..299) conn.inputStream else conn.errorStream
        val resp = stream?.bufferedReader(Charsets.UTF_8)?.use(BufferedReader::readText) ?: "{}"
        conn.disconnect()
        val o = JSONObject(resp)
        return ToolReply(
            ok = o.optBoolean("ok", false),
            reply = o.optString("reply", ""),
            error = o.optString("error", ""),
            raw = resp
        )
    }

    fun postAgent(
        baseUrl: String,
        question: String,
        utterance: String,
        history: List<Pair<String, String>> = emptyList()
    ): AgentReply {
        val conn = URL(baseUrl.trimEnd('/') + "/agent").openConnection() as HttpURLConnection
        conn.requestMethod = "POST"
        conn.doOutput = true
        conn.connectTimeout = 30_000
        conn.readTimeout = 90_000
        conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")

        val body = JSONObject()
        body.put("question", question)
        body.put("utterance", utterance)
        body.put("use_llm", false)   // 确定性路由优先，离线可用
        val hist = JSONArray()
        for ((s, a) in history) {
            hist.put(JSONArray().put(s).put(a))
        }
        body.put("history", hist)

        OutputStreamWriter(conn.outputStream, Charsets.UTF_8).use { it.write(body.toString()) }
        val code = conn.responseCode
        val stream = if (code in 200..299) conn.inputStream else conn.errorStream
        val resp = stream?.bufferedReader(Charsets.UTF_8)?.use(BufferedReader::readText) ?: "{}"
        conn.disconnect()
        val o = JSONObject(resp)
        return AgentReply(
            kind = o.optString("kind", "guide"),
            tool = if (o.has("tool") && !o.isNull("tool")) o.optString("tool") else null,
            reply = o.optString("reply", o.optString("error", "")),
            raw = resp
        )
    }

    private fun parse(json: String): TutorReply {
        val o = JSONObject(json)
        val err = o.optString("error", "")
        return TutorReply(
            replyText = o.optString("reply_text", err),
            ttsText = o.optString("tts_text", o.optString("reply_text", "")),
            questionText = if (o.has("question_text")) o.optString("question_text") else null,
            step = o.optInt("step", 1),
            hintLevel = o.optInt("hint_level", 1),
            needs = if (o.has("needs")) o.optString("needs") else null,
            latencyS = if (o.has("latency_s")) o.optDouble("latency_s") else null,
            raw = json
        )
    }
}
