#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""presence 在座检测 · 单元测试（确定性，不依赖真机摄像头）。

覆盖 12:05 令 §1 的三分类逻辑 + 300ms 预算字段 + 模型缺失报错。
"""
import os

import cv2
import numpy as np
import pytest

from presence import PresenceDetector, FaceDetector, FrameSource

_IMGDIR = "D:/Users/Administrator/code/super_intelligence_2035/images"


class MockSource(FrameSource):
    """把预先准备的帧按序吐出，模拟摄像头。"""

    def __init__(self, frames):
        self.frames = list(frames)
        self.i = 0

    def read(self):
        if self.i >= len(self.frames):
            return (False, None)
        f = self.frames[self.i]
        self.i += 1
        return (True, f)


def _dark():
    return np.zeros((240, 320, 3), dtype=np.uint8)


def _face():
    p = os.path.join(_IMGDIR, "15-teacher-callin.jpg")
    img = cv2.imread(p)
    assert img is not None
    return img


def _scene():
    p = os.path.join(_IMGDIR, "03-seed.png")
    img = cv2.imread(p)
    assert img is not None
    return img


def test_classify_none_is_unknown():
    d = PresenceDetector(source=MockSource([]))
    assert d.classify(None)[0] == "unknown"


def test_classify_dark_is_unknown():
    d = PresenceDetector(source=MockSource([]))
    status, info = d.classify(_dark())
    assert status == "unknown"
    assert info["reason"] == "too_dark"


def test_classify_face_is_person():
    d = PresenceDetector(source=MockSource([]))
    status, info = d.classify(_face())
    assert status == "person"
    assert info["backend"] == "yunet"


def test_classify_empty_scene_is_left():
    d = PresenceDetector(source=MockSource([]))
    assert d.classify(_scene())[0] == "left"


def test_grab_mock_returns_budget_fields():
    d = PresenceDetector(source=MockSource([_face()]))
    r = d.grab()
    assert r["status"] == "person"
    assert "latency_ms" in r
    assert "within_budget_ms" in r


def test_grab_read_fail_is_unknown():
    d = PresenceDetector(source=MockSource([]))
    r = d.grab()
    assert r["status"] == "unknown"
    assert r["reason"] == "read_fail"


def test_missing_model_raises():
    with pytest.raises(RuntimeError):
        FaceDetector(model_path="C:/nonexistent/not_there.onnx")


def test_model_is_found_automatically():
    d = FaceDetector()
    assert d.backend == "yunet"
