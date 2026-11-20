#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
presence 在座检测 · 评测（12:05 令 §5 交付物 eval/presence_*.json）

产出两组【真实数字】：
  1. live_measurement —— PC 摄像头连拍 20 次：帧率 + 单次抓帧检测耗时（P50/P90/max、300ms 预算达标率）
  2. accuracy —— 20 张标注样本三分类准确率（person/left/unknown + 混淆）

口径：🚫 不估算；PC 摄像头结论仅作「逻辑/耗时」证据，真人准确率待真机/真人复测
（16:5x 令「能信/不能信」）。
"""
import json
import os
import time

import cv2
import numpy as np

from presence import PresenceDetector, measure

IMGDIR = "D:/Users/Administrator/code/super_intelligence_2035/images"

# 标注集：person = 含人脸（YuNet 检出 >=1）；left = 无人脸且明亮；unknown = 暗帧
PERSON = [
    "01_linwei_dawn.jpg", "10-mirror-hall.jpg", "11-speed-asi.jpg",
    "15-teacher-callin.jpg", "21-american-dream.jpg",
    "25-workgroup-arrival.jpg", "30-open-source-weight.jpg",
    "37-abundance-existentialism.jpg",
]
LEFT = [
    "00_stone_forest_architecture.jpg", "03-seed.png", "17-the-wall.jpg",
    "20-heavens-hand.jpg", "28-ritual-music-law-governance-2.jpg",
    "31-the-dug-tree.jpg", "38-chessboard.jpg", "41-wisdom-of-blankness.jpg",
]


def _dark_frames(n=4):
    return [np.zeros((240, 320, 3), dtype=np.uint8) for _ in range(n)]


def main():
    det = PresenceDetector()
    samples = []
    # person
    for name in PERSON:
        img = cv2.imread(os.path.join(IMGDIR, name))
        status, info = det.classify(img)
        samples.append({"file": name, "expected": "person",
                        "predicted": status, "faces": info.get("faces", 0)})
    # left
    for name in LEFT:
        img = cv2.imread(os.path.join(IMGDIR, name))
        status, info = det.classify(img)
        samples.append({"file": name, "expected": "left",
                        "predicted": status, "brightness": info.get("brightness")})
    # unknown（暗帧）
    for i, f in enumerate(_dark_frames()):
        status, info = det.classify(f)
        samples.append({"file": "synthetic_dark_%d" % i, "expected": "unknown",
                        "predicted": status, "brightness": info.get("brightness")})

    correct = sum(1 for s in samples if s["expected"] == s["predicted"])
    per_class = {}
    for s in samples:
        k = s["expected"]
        per_class.setdefault(k, {"n": 0, "correct": 0})
        per_class[k]["n"] += 1
        if s["predicted"] == k:
            per_class[k]["correct"] += 1

    result = {
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "backend": det.detector.backend,
        "model": "face_detection_yunet_2023mar.onnx",
        "live_measurement": measure(n=20),
        "accuracy": {
            "n_total": len(samples),
            "n_correct": correct,
            "accuracy": round(correct / len(samples), 3),
            "per_class": per_class,
            "samples": samples,
        },
    }
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "eval", "presence_pc_camera.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("WROTE", out)


if __name__ == "__main__":
    main()
