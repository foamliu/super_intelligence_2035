#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
robot 线 · 在座检测（presence · 12:05 用户令 §1/§5 + INTERACTION_SPEC.md §8 定稿）

三分类（动作克制，见 INTERACTION_SPEC §8）：
  person   人脸/人体在  -> 轻声「我在，要提示吗？」（<=12 字）
  left     无人        -> 进 idle
  unknown  遮挡/逆光/太暗 -> 什么都不做，不猜不瞎问

硬约束（12:05 令 §1）：
  - 单帧、低分辨率 320x240；
  - 抓帧 -> 检测 -> 立即丢弃（不写盘、不上传、不留存；日志只记 presence=... + 时间戳）；
  - 单次抓帧+检测 <=300ms；
  - speak 态绝不抓帧、检测频率 <=1 次/90s —— 由【调用方】保证，本模块只提供 grab() 不做内部循环。

PC 端事实（16:5x 令「能信/不能信」）：
  - 默认后端 = PC 摄像头（cv2.VideoCapture，Logitech 046D 已实测可开）；
  - 人脸检测 = OpenCV 5 内置 YuNet（cv2.FaceDetectorYN，本地 ONNX 模型，端侧）。
    ⚠️ OpenCV 5.0 已移除 CascadeClassifier/HOGDescriptor，故改用 YuNet（更快更准，
    10~300px 小脸可检）；模型 face_detection_yunet_2023mar.onnx 放 host/models/。
  - 亮度阈值判「unknown」；端侧处理，帧不落盘。
"""
import os
import time

import cv2
import numpy as np

# 低分辨率单帧（12:05 令）
FRAME_W = 320
FRAME_H = 240

# 单次抓帧+检测硬上限（12:05 令 §1）
GRAB_BUDGET_MS = 300

# 亮度下限：低于此值判 unknown（太暗/逆光）
BRIGHTNESS_MIN = 40.0

# YuNet 人脸模型默认搜索路径（OpenCV 5 内置 FaceDetectorYN，端侧）
_YUNET_CANDIDATES = [
    os.environ.get("ROBOT_FACE_MODEL", ""),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "models",
                 "face_detection_yunet_2023mar.onnx"),
]


def _find_yunet() -> str:
    for p in _YUNET_CANDIDATES:
        if p and os.path.isfile(p):
            return p
    return ""


def _silence_cv_stderr():
    """临时把 fd 2 指向 devnull，压掉 OpenCV DNN 一次性 warning（C++ 层直接写 stderr）。"""
    import contextlib

    @contextlib.contextmanager
    def _ctx():
        devnull = os.open(os.devnull, os.O_WRONLY)
        old = os.dup(2)
        os.dup2(devnull, 2)
        os.close(devnull)
        try:
            yield
        finally:
            os.dup2(old, 2)
            os.close(old)
    return _ctx()


class FaceDetector:
    """人脸检测（OpenCV 5 内置 YuNet / FaceDetectorYN，端侧，非云端）。"""

    def __init__(self, model_path: str = None, width: int = FRAME_W,
                 height: int = FRAME_H, score_threshold: float = 0.6):
        self.backend = "yunet"
        self.width = width
        self.height = height
        path = model_path or _find_yunet()
        if not path or not os.path.isfile(path):
            raise RuntimeError(
                "YuNet 人脸模型未找到。下载并放到 host/models/ 或设 ROBOT_FACE_MODEL 指向它：\n"
                "  curl.exe -sL -o models/face_detection_yunet_2023mar.onnx "
                "https://huggingface.co/opencv/face_detection_yunet/resolve/main/"
                "face_detection_yunet_2023mar.onnx\n"
                "（模型权重 *.onnx 按 run/.gitignore 体积红线不入库，需自行拉取）")
        self._net = None
        with _silence_cv_stderr():
            self._net = cv2.FaceDetectorYN.create(
                path, "", (width, height), score_threshold, 0.3, 5000)

    def detect(self, bgr):
        """在已缩放到 (height,width,3) 的 BGR 图上检测。返回 (has_person, detail)。"""
        self._net.setInputSize((bgr.shape[1], bgr.shape[0]))
        _ok, faces = self._net.detect(bgr)
        n = 0 if faces is None else int(faces.shape[0])
        return (n > 0, {"faces": n, "backend": "yunet"})


class FrameSource:
    """帧源抽象：read() -> (ok, bgr_frame)。真机/测试可替换。"""

    def read(self):
        raise NotImplementedError

    def open(self):
        pass

    def close(self):
        pass


class WebcamSource(FrameSource):
    """PC 摄像头后端（cv2.VideoCapture）。"""

    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap = None

    def open(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise RuntimeError("无法打开摄像头 %d" % self.camera_index)
        # 预热丢首帧（自动曝光/对焦）
        self.cap.read()

    def read(self):
        ok, frame = self.cap.read()
        if not ok:
            return (False, None)
        return (True, frame)

    def close(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None


class PresenceDetector:
    """在座检测：单帧抓取 + 三分类 person/left/unknown。"""

    def __init__(self, source: FrameSource = None, camera_index: int = 0,
                 width: int = FRAME_W, height: int = FRAME_H,
                 model_path: str = None, brightness_min: float = BRIGHTNESS_MIN):
        self.source = source if source is not None else WebcamSource(camera_index)
        self.width = width
        self.height = height
        self.brightness_min = brightness_min
        self.detector = FaceDetector(model_path, width=width, height=height)

    def _prepare(self, frame):
        if frame.shape[1] != self.width or frame.shape[0] != self.height:
            frame = cv2.resize(frame, (self.width, self.height))
        return frame

    def classify(self, frame):
        """对单帧（BGR ndarray 或 None）做三分类。返回 (status, info)。"""
        if frame is None:
            return ("unknown", {"reason": "no_frame"})
        try:
            bgr = self._prepare(frame)
        except Exception:  # noqa: BLE001
            return ("unknown", {"reason": "bad_frame"})
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        brightness = float(gray.mean())
        if brightness < self.brightness_min:
            return ("unknown", {"reason": "too_dark",
                                "brightness": round(brightness, 1)})
        has_person, detail = self.detector.detect(bgr)
        if has_person:
            return ("person", detail)
        return ("left", {"brightness": round(brightness, 1)})

    def grab(self) -> dict:
        """抓一帧并检测，返回 dict。帧立即丢弃（栈上释放），不写盘/不上传。"""
        t0 = time.perf_counter()
        ok, frame = self.source.read()
        if not ok:
            return {"status": "unknown", "reason": "read_fail",
                    "latency_ms": round((time.perf_counter() - t0) * 1000, 1)}
        status, info = self.classify(frame)
        latency_ms = round((time.perf_counter() - t0) * 1000, 1)
        return {"status": status, "latency_ms": latency_ms,
                "within_budget_ms": bool(latency_ms <= GRAB_BUDGET_MS),
                **info}

    def open(self):
        self.source.open()

    def close(self):
        self.source.close()


def measure(n: int = 20, camera_index: int = 0, warmup: int = 2) -> dict:
    """连拍 n 次：帧率 + 单次抓帧检测耗时（真实数字，🚫 不估算）。"""
    det = PresenceDetector(camera_index=camera_index)
    det.open()
    results = []
    for _ in range(warmup):
        det.grab()
    t_start = time.perf_counter()
    for _ in range(n):
        results.append(det.grab())
    elapsed = time.perf_counter() - t_start
    det.close()
    lat = [r["latency_ms"] for r in results]
    return {
        "n": n,
        "elapsed_s": round(elapsed, 3),
        "fps": round(n / elapsed, 2) if elapsed > 0 else None,
        "latency_ms": lat,
        "latency_p50_ms": round(float(np.percentile(lat, 50)), 1),
        "latency_p90_ms": round(float(np.percentile(lat, 90)), 1),
        "latency_max_ms": round(float(max(lat)), 1),
        "within_budget_300ms": int(sum(1 for r in results if r["within_budget_ms"])),
        "statuses": [r["status"] for r in results],
        "backend": det.detector.backend,
    }


def main():
    import argparse
    import json
    ap = argparse.ArgumentParser(description="presence 在座检测自测")
    ap.add_argument("--measure", action="store_true", help="连拍 20 次测帧率/耗时")
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--n", type=int, default=20)
    args = ap.parse_args()

    det = PresenceDetector(camera_index=args.camera)
    det.open()
    try:
        r = det.grab()
        print("单帧：", json.dumps(r, ensure_ascii=False))
        if args.measure:
            m = measure(n=args.n, camera_index=args.camera)
            print("连拍：", json.dumps(m, ensure_ascii=False))
    finally:
        det.close()


if __name__ == "__main__":
    main()
