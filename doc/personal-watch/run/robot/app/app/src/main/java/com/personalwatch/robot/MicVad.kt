package com.personalwatch.robot

import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import kotlin.math.sqrt

/**
 * 端侧 VAD（能量阈值 + debounce）· AudioRecord 16kHz 单声道 PCM16。
 *
 * 对应 host/vad.py 的纯逻辑实现；这里提供 Android 真机/模拟器的麦克风采集 + 帧能量判定：
 *   - TTS 播放（说态）时监听：连续 [minFrames] 帧能量超阈 -> onSpeechDetected()（语音打断源）
 *   - 静音 = stop() 真关麦（释放 AudioRecord），不是软件忽略（INTERACTION_SPEC 红线 5）
 *   - 无麦克风/无权限/初始化失败 -> onMicError() 回调，优雅降级纯文字（不崩溃、不静默）
 */
class MicVad(
    private val thresholdDb: Double = -40.0,
    private val minFrames: Int = 2,
    private val frameMs: Int = 30,
    private val onSpeechDetected: () -> Unit,
    private val onMicError: (String) -> Unit
) {
    private var record: AudioRecord? = null
    @Volatile private var running = false
    private var thread: Thread? = null

    private val sampleRate = 16000
    private val frameSize = sampleRate * frameMs / 1000  // 480 samples

    fun start() {
        if (running) return
        val minBuf = AudioRecord.getMinBufferSize(
            sampleRate, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT
        )
        if (minBuf <= 0) {
            onMicError("无可用录音输入（无麦克风）")
            return
        }
        val rec = try {
            AudioRecord(
                MediaRecorder.AudioSource.MIC, sampleRate,
                AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT,
                maxOf(minBuf, frameSize * 2)
            )
        } catch (e: Exception) {
            onMicError("麦克风初始化失败：${e.message}")
            return
        }
        if (rec.state != AudioRecord.STATE_INITIALIZED) {
            onMicError("麦克风未就绪（可能无权限或无设备）")
            return
        }
        record = rec
        rec.startRecording()
        running = true
        thread = Thread { loop() }.also { it.start() }
    }

    fun stop() {
        running = false
        thread?.join(500)
        thread = null
        try { record?.stop() } catch (_: Exception) {}
        try { record?.release() } catch (_: Exception) {}
        record = null
    }

    private fun loop() {
        val buf = ShortArray(frameSize)
        var consecutive = 0
        while (running) {
            val n = record?.read(buf, 0, frameSize) ?: break
            if (n <= 0) continue
            val db = rmsDb(buf, n)
            if (db >= thresholdDb) {
                consecutive++
                if (consecutive >= minFrames) {
                    consecutive = 0
                    onSpeechDetected()
                }
            } else {
                consecutive = 0
            }
        }
    }

    private fun rmsDb(buf: ShortArray, n: Int): Double {
        var sum = 0.0
        for (i in 0 until n) {
            val s = buf[i].toDouble()
            sum += s * s
        }
        val rms = sqrt(sum / n) / 32768.0  // 归一化到 0..1
        return if (rms > 0.0) 20.0 * kotlin.math.log10(rms) else -100.0
    }
}
