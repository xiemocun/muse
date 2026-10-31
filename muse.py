"""muse：给 AI 用的灵感引擎。

原理不是玄学，是三条被验证过的机制：
  1. 远域类比 —— 把不相干领域的结构强行搬过来
  2. 极端约束 —— 把问题推到墙角，逼出新解
  3. 异常探测 —— 从「不对劲」的地方入手

它不生成答案，它生成「逼你想别的」的问题。同一道题永远得到同一组提示（可复现），
因为灵感如果不可复现，就没法被检验。
"""
from __future__ import annotations

import argparse
import hashlib
import json

# 远域：和软件/产品离得足够远，结构才可能真的不同
DOMAINS = [
    ("军事", "后勤、佯动、预备队、补给线"),
    ("生物学", "免疫记忆、共生、蜕皮、趋同演化"),
    ("建筑", "承重、采光、动线、扩建缝"),
    ("音乐", "主题变奏、休止、转调、对位"),
    ("法律", "举证责任、判例、时效、合同漏洞"),
    ("农业", "轮作、嫁接、育种、休耕"),
    ("航海", "压舱、吃水、灯塔、引航"),
    ("医学", "分诊、免疫耐受、康复、副作用"),
    ("戏剧", "幕结构、悬念、替身、彩排"),
    ("水利", "泄洪、闸门、渠道、淤积"),
]

CONSTRAINTS = [
    "预算只有现在的 1%",
    "只能做一次，做完就不能改",
    "必须在一小时内完成",
    "使用者完全不识字",
    "没有网络",
    "有 100 倍的用户量，但机器不变",
    "必须能被十岁小孩解释清楚",
    "失败一次就永久失去资格",
    "所有数据每隔一周全部丢失",
    "必须同时服务完全相反的两种需求",
]

ANOMALY_PROBES = [
    "你手上这个方案，哪一部分从来没人质疑过？为什么没人质疑？",
    "如果这个方法真的有效，为什么不是所有人都已经在用？",
    "最近一次让你觉得「奇怪但说不出哪里怪」的地方是什么？",
    "哪个指标一直在变好，但用户的抱怨一直没减少？",
    "如果这个项目明天消失了，谁最难受？那个人为什么没出现？",
]


def pick(seed: str, pool: list, n: int) -> list:
    """按种子确定性抽取：同一个问题永远得到同一组提示。"""
    out, used, i = [], set(), 0
    while len(out) < n and i < len(pool) * 4:
        h = hashlib.sha256(f"{seed}:{i}".encode()).digest()
        idx = int.from_bytes(h[:4], "big") % len(pool)
        if idx not in used:
            used.add(idx)
            out.append(pool[idx])
        i += 1
    return out


def build(problem: str, n: int = 3) -> dict:
    seed = problem.strip().lower()
    return {
        "problem": problem,
        "远域类比": [
            {"领域": d, "它的结构": s,
             "问题": f"如果把「{problem[:30]}」当成{d}问题来处理，{d}里最重要的东西（{s}）在这对应的是什么？"}
            for d, s in pick(seed + "d", DOMAINS, n)
        ],
        "极端约束": [
            {"约束": c,
             "问题": f"如果「{c}」，你会放弃现在的哪个假设？放弃它之后剩下的最小可行方案是什么？"}
            for c in pick(seed + "c", CONSTRAINTS, n)
        ],
        "异常探测": pick(seed + "a", ANOMALY_PROBES, 2),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("problem", nargs="+")
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    problem = " ".join(a.problem)
    r = build(problem, a.n)

    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return
    print(f"问题：{problem}\n")
    print("一、远域类比（把别的领域的结构搬过来）")
    for x in r["远域类比"]:
        print(f"  [{x['领域']}] {x['它的结构']}")
        print(f"    {x['问题']}\n")
    print("二、极端约束（推到墙角，看哪条假设先碎）")
    for x in r["极端约束"]:
        print(f"  {x['约束']}")
        print(f"    {x['问题']}\n")
    print("三、异常探测（灵感常在没人看的地方）")
    for q in r["异常探测"]:
        print(f"  - {q}")


if __name__ == "__main__":
    main()