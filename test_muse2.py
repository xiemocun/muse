"""muse v2 的测试：确定性、四个算子齐全、收窄与可验证关卡不缺。"""
import json
import subprocess
import sys
from pathlib import Path

import muse2

HERE = Path(__file__).parent


def test_same_problem_gives_same_output():
    a = muse2.build("给 AI 做灵感工具")
    b = muse2.build("给 AI 做灵感工具")
    assert a == b, "同题不同结果，灵感就不可复现"


def test_different_problems_differ():
    assert muse2.build("做灵感工具") != muse2.build("做数据处理工具")


def test_four_operators_present():
    r = muse2.build("随便一个问题")
    names = [c["算子"] for c in r["候选"]]
    assert names == ["类比迁移", "矛盾缝合", "降维抽象", "反转因果"], names


def test_two_distinct_attributes():
    r = muse2.build("随便一个问题")
    assert r["属性"][0] != r["属性"][1]


def test_narrowing_and_verifiable_are_not_empty():
    r = muse2.build("随便一个问题")
    assert len(r["收窄"]) >= 2
    assert len(r["可验证"]) >= 3
    assert any("可证伪" in q for q in r["可验证"])


def test_cli_json_roundtrip():
    out = subprocess.run(
        [sys.executable, str(HERE / "muse2.py"), "测试问题", "--json"],
        capture_output=True, text=True, timeout=60)
    data = json.loads(out.stdout)
    assert data["problem"] == "测试问题"
    assert len(data["候选"]) == 4