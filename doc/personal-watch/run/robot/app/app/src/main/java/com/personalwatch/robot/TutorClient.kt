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

data class ProfileReply(
    val totalWrong: Int,
    val totalPractice: Int,
    val knowledgeCount: Int,
    val weakPoints: String,
    val practiceSummary: String,
    val raw: String
)

data class PracticeReply(
    val ok: Boolean,
    val totalPractice: Int,
    val error: String
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

    fun postProfile(baseUrl: String): ProfileReply {
        val conn = URL(baseUrl.trimEnd('/') + "/profile").openConnection() as HttpURLConnection
        conn.requestMethod = "POST"
        conn.doOutput = true
        conn.connectTimeout = 30_000
        conn.readTimeout = 30_000
        conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")

        OutputStreamWriter(conn.outputStream, Charsets.UTF_8).use { it.write("{}") }
        val code = conn.responseCode
        val stream = if (code in 200..299) conn.inputStream else conn.errorStream
        val resp = stream?.bufferedReader(Charsets.UTF_8)?.use(BufferedReader::readText) ?: "{}"
        conn.disconnect()

        val o = JSONObject(resp)
        val p = o.optJSONObject("profile") ?: JSONObject()
        val weakList = mutableListOf<String>()
        val wp = p.optJSONArray("weak_points")
        if (wp != null) {
            for (i in 0 until wp.length()) {
                weakList.add(wp.getJSONObject(i).optString("knowledge"))
            }
        }
        // 正样本：从合并画像里挑作答次数 > 0 的知识点，拼成「知识点 次数/正确率」摘要
        val practice = mutableListOf<String>()
        val kps = p.optJSONArray("knowledge_points")
        if (kps != null) {
            for (i in 0 until kps.length()) {
                val kp = kps.getJSONObject(i)
                val attempts = kp.optInt("attempt_count", 0)
                if (attempts > 0) {
                    val pct = (kp.optDouble("correct_rate", 0.0) * 100).toInt()
                    practice.add("${kp.optString("knowledge")} ${attempts}次/${pct}%")
                }
            }
        }
        return ProfileReply(
            totalWrong = p.optInt("total_wrong", 0),
            totalPractice = p.optInt("total_practice", 0),
            knowledgeCount = p.optInt("knowledge_count", 0),
            weakPoints = weakList.joinToString("、"),
            practiceSummary = practice.joinToString(" · "),
            raw = resp
        )
    }

    fun postPractice(
        baseUrl: String,
        question: String,
        correct: Boolean,
        knowledge: String,
        studentAnswer: String
    ): PracticeReply {
        val conn = URL(baseUrl.trimEnd('/') + "/practice").openConnection() as HttpURLConnection
        conn.requestMethod = "POST"
        conn.doOutput = true
        conn.connectTimeout = 30_000
        conn.readTimeout = 30_000
        conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")

        val body = JSONObject()
        body.put("question", question)
        body.put("correct", correct)
        if (knowledge.isNotBlank()) body.put("knowledge", knowledge)
        if (studentAnswer.isNotBlank()) body.put("student_answer", studentAnswer)

        OutputStreamWriter(conn.outputStream, Charsets.UTF_8).use { it.write(body.toString()) }
        val code = conn.responseCode
        val stream = if (code in 200..299) conn.inputStream else conn.errorStream
        val resp = stream?.bufferedReader(Charsets.UTF_8)?.use(BufferedReader::readText) ?: "{}"
        conn.disconnect()

        val o = JSONObject(resp)
        return PracticeReply(
            ok = o.optBoolean("ok", false),
            totalPractice = o.optInt("total_practice", 0),
            error = o.optString("error", "")
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
