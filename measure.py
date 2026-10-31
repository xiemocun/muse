"""measure：唯一不靠人评的指标——输出的跨域覆盖。

注意边界：这测的是「工具产出的提示覆盖多少个不相干领域」，
不是「用了它之后模型的点子更好」。后者必须有模型参与才能测。
先测这个，是因为它可机器计算、可复现；如果连这一项都没提升，后面两项不用谈。
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter

import muse2

PROBLEMS = [
    "给本地小商家做工具，怎么不落进代运营的坑",
    "AI 写作助手怎么避免输出千篇一律",
    "开源项目怎么找到第一批真实用户",
    "怎么判断一个技术方向三年后还在",
    "一个人怎么持续产出而不耗尽",
    "怎么让测试真的能抓住 bug 而不是走过场",
    "团队知识怎么在人员流动时不丢",
    "怎么给一个没人为之付费的需求定价",
]


def coverage(problems: list[str]) -> dict:
    domains, attrs = Counter(), Counter()
    for i, p in enumerate(problems):
        r = muse2.build(p, domain_offset=i)  # 轮转，避免哈希把多个问题挤到同一远域
        domains[r["远域"]["领域"]] += 1
        for a in r["属性"]:
            attrs[a] += 1
    total = sum(domains.values())
    probs = [c / total for c in domains.values()]
    entropy = -sum(x * math.log2(x) for x in probs) if probs else 0.0
    return {
        "问题数": len(problems),
        "覆盖远域数": len(domains),
        "远域分布": dict(domains.most_common()),
        "远域熵(bit)": round(entropy, 3),
        "最大熵(bit)": round(math.log2(len(muse2.FAR)), 3),
        "覆盖属性数": len(attrs),
        "属性总数": len(muse2.ATTRS),
    }


def baseline() -> dict:
    """对照组：问题原文本身。人写一个问题，通常只锚在一个领域里。"""
    return {"说明": "直接拿问题去问模型时，提示里只有一个领域（问题所在的那个）",
            "覆盖远域数": 1, "远域熵(bit)": 0.0}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    c = coverage(PROBLEMS)
    out = {"muse": c, "baseline": baseline()}
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return
    print(f"问题数: {c['问题数']}")
    print(f"覆盖远域: {c['覆盖远域数']} 个（共 {len(muse2.FAR)}）")
    print(f"远域熵: {c['远域熵(bit)']} bit / 最大 {c['最大熵(bit)']} bit")
    print(f"覆盖属性: {c['覆盖属性数']} / {c['属性总数']}")
    print(f"对照（直接用问题去问）: 1 个领域，熵 0")
    print("\n远域分布:", c["远域分布"])


if __name__ == "__main__":
    main()