"""muse v2：灵感旁路。

四条实测有用的机制，外加一条纪律：
  1. 远域属性重组（不做向量扰动，扰动抽象标签，零依赖）
  2. 四个碰撞算子：类比迁移 / 矛盾缝合 / 降维抽象 / 反转因果
  3. 可验证代理：一个想法能不能写成一个能测的命题——比「模型自评有张力」可靠
  4. 只发散一轮，第二轮强制收窄（收窄比发散难，也更值钱）

确定性：同一个问题永远得到同一组提示，方便复现和 A/B。
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json

# 抽象属性，不是领域名词——正因为抽象，才能跨域搬运
ATTRS = ["克制", "失重", "破碎", "慢张力", "反常识", "冗余", "延迟", "不可逆",
         "共振", "留白", "锚定", "熵增", "回声", "阈限", "折叠"]

FAR = [("免疫系统", "识别自我与非我、记忆、耐受"),
       ("水利工程", "泄洪、淤积、闸门、渠系"),
       ("戏剧结构", "幕、悬念、替身、彩排"),
       ("司法程序", "举证责任、时效、判例"),
       ("农业育种", "杂交优势、回交、表型筛选"),
       ("航海", "压舱、吃水、灯塔、引航"),
       ("音乐对位", "主题变奏、休止、转调"),
       ("建筑承重", "荷载路径、伸缩缝、扩建接口")]

OPERATORS = [
    ("类比迁移", "把 {far} 的结构（{note}）当成解法骨架，问题变成：{attr} 在这个结构里对应什么？"),
    ("矛盾缝合", "同时满足「要 {attr_a}」和「要 {attr_b}」——这两个要求在你现在的方案里是互斥的，怎么让它们共存？"),
    ("降维抽象", "剥掉所有业务细节，只留下「{attr}」这一个属性；从零重建，会得到什么形态？"),
    ("反转因果", "如果 {attr} 不是结果而是原因，谁在制造它？把因果调过来，方案怎么变？"),
]


def h(seed: str, n: int) -> int:
    return int.from_bytes(hashlib.sha256(seed.encode()).digest()[:4], "big") % n


def build(problem: str) -> dict:
    s = problem.strip().lower()
    a = ATTRS[h(s + "a", len(ATTRS))]
    b = ATTRS[h(s + "b", len(ATTRS))]
    if b == a:
        b = ATTRS[(ATTRS.index(a) + 3) % len(ATTRS)]
    far, note = FAR[h(s + "f", len(FAR))]

    cands = []
    for name, tpl in OPERATORS:
        text = tpl.format(far=far, note=note, attr=a, attr_a=a, attr_b=b)
        cands.append({"算子": name, "提示": text})

    # 收窄：只留一条约束，其余全放开
    narrow = [
        f"从上面 {len(cands)} 个候选里挑一个，回答：它最少需要保留哪一条约束？",
        "如果把这条约束去掉，想法立刻崩塌——那条才是真的约束；其余的都可以改。",
    ]

    # 可验证代理：把想法变成能测的命题
    probes = [
        "这个想法能用一句话写成一个可证伪的预测吗？（「如果 X，则 Y 会变多」）",
        "要测它，最少需要什么数据？现在拿得到吗？",
        "什么结果出现，你会承认它不成立？先写下这个结果，再动手。",
    ]

    return {
        "problem": problem,
        "属性": [a, b],
        "远域": {"领域": far, "结构": note},
        "候选": cands,
        "收窄": narrow,
        "可验证": probes,
    }


def render(r: dict) -> str:
    out = [f"问题：{r['problem']}", f"属性标签：{r['属性'][0]} / {r['属性'][1]}",
           f"远域：{r['远域']['领域']}（{r['远域']['结构']}）", "", "一、四个碰撞算子"]
    for c in r["候选"]:
        out.append(f"  [{c['算子']}] {c['提示']}")
    out += ["", "二、收窄（比发散更难）"]
    out += [f"  - {q}" for q in r["收窄"]]
    out += ["", "三、可验证代理（过不了这关的想法不算灵感）"]
    out += [f"  - {q}" for q in r["可验证"]]
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("problem", nargs="+")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    r = build(" ".join(a.problem))
    print(json.dumps(r, ensure_ascii=False, indent=1) if a.json else render(r))


if __name__ == "__main__":
    main()