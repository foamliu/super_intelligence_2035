package com.personalwatch.robot

import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import okio.ByteString
import org.json.JSONObject
import java.util.concurrent.TimeUnit

/**
 * Android 端 WebSocket 流式会话客户端（11:40 令 §5 #2 的 App 端落地）。
 *
 * 对应 host/ws_session.py 的协议（JSON 文本帧，utf-8）：
 *   上行：hello / asr_partial / asr_final / audio_chunk / barge_in / mute / unmute / reset
 *   下行：state / meta / asr / hint / tts_sentence / done / stopped / error
 *
 * 用 OkHttp 做 WebSocket；回调在 OkHttp 后台线程，调用方需自行 runOnUiThread 更新 UI。
 * 静音真关麦（muted 态丢弃输入）由服务端保证，本类只负责按协议收发。
 */
class WsTutorClient(private val listener: Listener) {

    interface Listener {
        fun onOpen()
        fun onMessage(type: String, obj: JSONObject)
        fun onClosed(code: Int, reason: String)
        fun onFailure(msg: String)
    }

    private val client: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(0, TimeUnit.MILLISECONDS) // 长连接，不设读超时
        .pingInterval(20, TimeUnit.SECONDS)
        .build()

    @Volatile
    private var ws: WebSocket? = null

    @Volatile
    var connected: Boolean = false
        private set

    fun connect(uri: String) {
        if (connected) return
        val req = Request.Builder().url(uri).build()
        ws = client.newWebSocket(req, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                connected = true
                listener.onOpen()
                sendType("hello") // 握手 -> 服务端回 state + meta
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                val o = runCatching { JSONObject(text) }.getOrNull() ?: return
                listener.onMessage(o.optString("type", ""), o)
            }

            override fun onMessage(webSocket: WebSocket, bytes: ByteString) {
                // 协议用文本帧；二进制帧忽略
            }

            override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                webSocket.close(code, reason)
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                connected = false
                ws = null
                listener.onClosed(code, reason)
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                connected = false
                ws = null
                listener.onFailure(t.message ?: "ws error")
            }
        })
    }

    private fun sendType(type: String, fields: Map<String, Any?> = emptyMap()): Boolean {
        val o = JSONObject()
        o.put("type", type)
        for ((k, v) in fields) o.put(k, v)
        return ws?.send(o.toString()) ?: false
    }

    fun sendAsrPartial(text: String) = sendType("asr_partial", mapOf("text" to text))
    fun sendAsrFinal(text: String) = sendType("asr_final", mapOf("text" to text))
    fun sendBargeIn() = sendType("barge_in")
    fun sendMute() = sendType("mute")
    fun sendUnmute() = sendType("unmute")
    fun sendReset() = sendType("reset")

    fun close() {
        ws?.close(1000, "bye")
        ws = null
        connected = false
    }
}
