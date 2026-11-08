package com.personalwatch.robot

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Bundle
import android.speech.tts.TextToSpeech
import android.util.Base64
import android.util.Log
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.ImageProxy
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import java.io.ByteArrayOutputStream
import java.util.Locale
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

/**
 * 家教机器人 · 手机端主界面（R3 路线：手机只做「眼耳口」采集+播放，推理在 PC/云）。
 * 能力（22:50 令）：拍照 / 选图 -> base64 上传 POST /tutor -> 收到分步引导（不含最终答案）
 * -> 系统 TTS 朗读 -> 「打断」按钮停播（barge-in 的应用层实现）。
 */
class MainActivity : AppCompatActivity(), TextToSpeech.OnInitListener {

    private lateinit var tvStatus: TextView
    private lateinit var tvReply: TextView
    private lateinit var etServer: EditText
    private lateinit var etInput: EditText
    private lateinit var previewView: PreviewView

    private var imageCapture: ImageCapture? = null
    private lateinit var cameraExecutor: ExecutorService
    private var tts: TextToSpeech? = null
    private var ttsReady = false
    private var currentTtsText: String = ""
    private var currentQuestion: String = ""
    private val history = mutableListOf<Pair<String, String>>()
    private val followUps = mutableListOf<Pair<String, String>>()

    private val pickImage =
        registerForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
            if (uri != null) {
                val bytes = readBytes(uri)
                if (bytes == null) {
                    setStatus("读取图片失败")
                    return@registerForActivityResult
                }
                setStatus("已选图，正在识别…")
                sendImage(bytes)
            }
        }

    private val requestPermission =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            if (granted) startCamera() else setStatus("未授予相机权限，可用「选图」模式")
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        tvStatus = findViewById(R.id.tvStatus)
        tvReply = findViewById(R.id.tvReply)
        etServer = findViewById(R.id.etServer)
        etInput = findViewById(R.id.etInput)
        previewView = findViewById(R.id.previewView)
        cameraExecutor = Executors.newSingleThreadExecutor()

        etServer.setText(
            getSharedPreferences("robot", MODE_PRIVATE)
                .getString("server", "http://10.0.2.2:8765")
        )

        findViewById<Button>(R.id.btnCapture).setOnClickListener { capturePhoto() }
        findViewById<Button>(R.id.btnPick).setOnClickListener { pickImage.launch("image/*") }
        findViewById<Button>(R.id.btnSpeak).setOnClickListener { speakCurrent() }
        findViewById<Button>(R.id.btnStop).setOnClickListener { stopSpeaking() }
        findViewById<Button>(R.id.btnHealth).setOnClickListener { checkHealth() }
        findViewById<Button>(R.id.btnNext).setOnClickListener {
            callTool("question_bank", mapOf("subject" to "", "keyword" to ""))
        }
        findViewById<Button>(R.id.btnWrong).setOnClickListener {
            val q = currentQuestion.ifBlank { history.lastOrNull()?.first ?: "" }
            if (q.isBlank()) {
                setStatus("先拍一道题，才能记错题")
            } else {
                val ans = etInput.text.toString().trim().ifBlank { "（标记为错题）" }
                callTool("wrong_book_add", mapOf("question" to q, "student_answer" to ans))
            }
        }
        findViewById<Button>(R.id.btnReport).setOnClickListener {
            callTool("parent_report", emptyMap())
        }
        findViewById<Button>(R.id.btnSend).setOnClickListener { sendFollowUp() }

        tts = TextToSpeech(this, this)

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
            == PackageManager.PERMISSION_GRANTED
        ) {
            startCamera()
        } else {
            requestPermission.launch(Manifest.permission.CAMERA)
        }
    }

    // ── 相机（CameraX）────────────────────────────────────────────
    private fun startCamera() {
        val future = ProcessCameraProvider.getInstance(this)
        future.addListener({
            val provider = future.get()
            val preview = Preview.Builder().build().also {
                it.setSurfaceProvider(previewView.surfaceProvider)
            }
            val capture = ImageCapture.Builder().build()
            imageCapture = capture
            provider.unbindAll()
            try {
                provider.bindToLifecycle(
                    this, CameraSelector.DEFAULT_BACK_CAMERA, preview, capture
                )
            } catch (e: Exception) {
                Log.w(TAG, "绑定后置相机失败，尝试前置相机", e)
                try {
                    provider.bindToLifecycle(
                        this, CameraSelector.DEFAULT_FRONT_CAMERA, preview, capture
                    )
                } catch (e2: Exception) {
                    Log.w(TAG, "绑定相机失败", e2)
                    setStatus("相机不可用（无摄像头设备），请用「选图」模式")
                }
            }
        }, ContextCompat.getMainExecutor(this))
    }

    private fun capturePhoto() {
        val capture = imageCapture ?: run {
            setStatus("相机未就绪，请用「选图」")
            return
        }
        setStatus("拍照中…")
        capture.takePicture(
            ContextCompat.getMainExecutor(this),
            object : ImageCapture.OnImageCapturedCallback() {
                override fun onCaptureSuccess(image: ImageProxy) {
                    val bytes = imageProxyToJpeg(image)
                    image.close()
                    setStatus("已拍照，正在识别…")
                    sendImage(bytes)
                }

                override fun onError(exception: ImageCaptureException) {
                    setStatus("拍照失败：${exception.message}")
                }
            }
        )
    }

    // ── 上传 + 引导 ──────────────────────────────────────────────
    private fun sendImage(jpegBytes: ByteArray) {
        val server = etServer.text.toString().trim()
        getSharedPreferences("robot", MODE_PRIVATE).edit()
            .putString("server", server).apply()

        cameraExecutor.execute {
            try {
                val scaled = downscaleForUpload(jpegBytes, 1600)
                val b64 = Base64.encodeToString(scaled, Base64.NO_WRAP)
                val reply = TutorClient.postTutor(server, imageB64 = b64, text = null, history = history)
                runOnUiThread {
                    val q = reply.questionText ?: ""
                    tvReply.text = buildString {
                        if (q.isNotBlank()) {
                            append("【识别题干】").append(q).append("\n\n")
                        }
                        append(reply.replyText)
                    }
                    currentTtsText = reply.ttsText
                    currentQuestion = q
                    history.add(q to reply.replyText)
                    followUps.clear()
                    val lat = reply.latencyS?.let { " · ${it}s" } ?: ""
                    setStatus("引导就绪${lat}（点「朗读」出声）")
                    speakCurrent()
                }
            } catch (e: Exception) {
                Log.e(TAG, "POST /tutor 失败", e)
                runOnUiThread {
                    setStatus("识别失败：${e.message}")
                    Toast.makeText(this, "无法连接服务，请检查地址", Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    private fun checkHealth() {
        val server = etServer.text.toString().trim()
        cameraExecutor.execute {
            try {
                val r = TutorClient.health(server)
                runOnUiThread { setStatus("连接正常：$r") }
            } catch (e: Exception) {
                runOnUiThread { setStatus("连接失败：${e.message}") }
            }
        }
    }

    // ── L2 工具（换一题 / 记错题 / 报告）→ POST /tool ──────────────
    private fun callTool(tool: String, params: Map<String, String>) {
        val server = etServer.text.toString().trim()
        cameraExecutor.execute {
            try {
                val r = TutorClient.postTool(server, tool, params)
                runOnUiThread {
                    if (r.ok) {
                        tvReply.text = buildString {
                            append("【工具·").append(tool).append("】\n")
                            append(r.reply)
                        }
                        currentTtsText = r.reply
                        setStatus("工具已处理（点「朗读」出声）")
                        speakCurrent()
                    } else {
                        setStatus("工具拒绝：${r.error}")
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "POST /tool 失败", e)
                runOnUiThread { setStatus("工具调用失败：${e.message}") }
            }
        }
    }

    // ── 追问（文字多轮）→ POST /agent ──────────────────────────────
    private fun sendFollowUp() {
        val server = etServer.text.toString().trim()
        val text = etInput.text.toString().trim()
        if (text.isBlank()) {
            setStatus("先输入一句话再发送")
            return
        }
        val q = currentQuestion.ifBlank { history.lastOrNull()?.first ?: "" }
        if (q.isBlank()) {
            // 无题干上下文：当作一道新的文字题走 /tutor
            cameraExecutor.execute {
                try {
                    val reply = TutorClient.postTutor(server, imageB64 = null, text = text, history = history)
                    runOnUiThread {
                        currentQuestion = reply.questionText ?: text
                        history.add((reply.questionText ?: text) to reply.replyText)
                        followUps.clear()
                        tvReply.text = reply.replyText
                        currentTtsText = reply.ttsText
                        etInput.setText("")
                        setStatus("文字题已回应")
                        speakCurrent()
                    }
                } catch (e: Exception) {
                    runOnUiThread { setStatus("发送失败：${e.message}") }
                }
            }
            return
        }
        cameraExecutor.execute {
            try {
                val r = TutorClient.postAgent(server, q, text, followUps)
                runOnUiThread {
                    tvReply.text = buildString {
                        append("【追问】").append(text).append("\n\n")
                        append(r.reply)
                    }
                    currentTtsText = r.reply
                    followUps.add(text to r.reply)
                    etInput.setText("")
                    setStatus("已回应追问（点「朗读」出声）")
                    speakCurrent()
                }
            } catch (e: Exception) {
                Log.e(TAG, "POST /agent 失败", e)
                runOnUiThread { setStatus("追问失败：${e.message}") }
            }
        }
    }

    // ── TTS（系统 TextToSpeech，端侧）─────────────────────────────
    override fun onInit(status: Int) {
        ttsReady = status == TextToSpeech.SUCCESS
        if (ttsReady) {
            tts?.language = Locale.CHINA
            setStatus("语音就绪。拍一道题，或点「选图」。")
        } else {
            setStatus("系统 TTS 初始化失败，仅文字模式")
        }
    }

    private fun speakCurrent() {
        if (!ttsReady || currentTtsText.isBlank()) {
            if (currentTtsText.isBlank()) setStatus("还没有可朗读的引导")
            return
        }
        tts?.speak(currentTtsText, TextToSpeech.QUEUE_FLUSH, null, "tutor_tts")
        setStatus("朗读中…（点「打断」可停）")
    }

    private fun stopSpeaking() {
        tts?.stop()
        setStatus("已打断（停播）。可继续追问或拍新题。")
    }

    // ── 工具 ─────────────────────────────────────────────────────
    private fun setStatus(s: String) {
        tvStatus.text = s
    }

    private fun readBytes(uri: Uri): ByteArray? {
        return try {
            contentResolver.openInputStream(uri)?.use { it.readBytes() }
        } catch (e: Exception) {
            Log.w(TAG, "读取 URI 失败", e)
            null
        }
    }

    private fun imageProxyToJpeg(image: ImageProxy): ByteArray {
        val buffer = image.planes[0].buffer
        val bytes = ByteArray(buffer.remaining())
        buffer.get(bytes)
        return bytes
    }

    private fun downscaleForUpload(jpeg: ByteArray, maxDim: Int): ByteArray {
        val opts = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        BitmapFactory.decodeByteArray(jpeg, 0, jpeg.size, opts)
        var sample = 1
        while (opts.outWidth / sample > maxDim || opts.outHeight / sample > maxDim) {
            sample *= 2
        }
        val opts2 = BitmapFactory.Options().apply { inSampleSize = sample }
        val bmp = BitmapFactory.decodeByteArray(jpeg, 0, jpeg.size, opts2) ?: return jpeg
        val out = ByteArrayOutputStream()
        bmp.compress(Bitmap.CompressFormat.JPEG, 85, out)
        bmp.recycle()
        return out.toByteArray()
    }

    override fun onDestroy() {
        super.onDestroy()
        tts?.stop()
        tts?.shutdown()
        cameraExecutor.shutdown()
    }

    companion object {
        private const val TAG = "RobotTutor"
    }
}
