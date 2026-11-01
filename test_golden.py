"""黄金用例：把「输入 → 输出」的映射钉死。

为什么需要：变异测试（mutcheck）发现，把 build 里的比较符或边界数字改错，
原有的测试一个都不响。因为那些测试只检查「两个属性不一样」这类弱性质，
逻辑怎么改都能满足。

黄金用例钉的是具体值：任何一处逻辑变动，映射就变，这里立刻红。
"""

import muse2

GOLDEN = [
    # (问题, 属性, 远域)
    ("我想找个能赚钱的副业", ("克制", "留白"), "司法程序"),
    ("AI 工具总是太具体，怎么让它产生新奇的用途", ("延迟", "克制"), "音乐对位"),
    ("副业怎么定价", ("冗余", "破碎"), "免疫系统"),
]


def test_golden_mapping_is_pinned():
    for problem, attrs, domain in GOLDEN:
        r = muse2.build(problem)
        assert tuple(r["属性"]) == attrs, (problem, r["属性"])
        assert r["远域"]["领域"] == domain, (problem, r["远域"]["领域"])


def test_attributes_are_never_equal():
    """b == a 的那条分支必须真的存在，并且真的被走到过。"""
    for p in ("副业怎么定价", "我想找个能赚钱的副业", "测试" * 40):
        r = muse2.build(p)
        assert r["属性"][0] != r["属性"][1]


def test_domain_index_moves_with_offset():
    """domain_offset 必须真的改变远域，否则成批轮转是假的。"""
    base = muse2.build("副业怎么定价")
    shifted = muse2.build("副业怎么定价", domain_offset=1)
    assert base["远域"]["领域"] != shifted["远域"]["领域"]


def test_offset_wraps_around_the_pool():
    """偏移量等于远域总数时应当回到原处（取模边界）。"""
    n = len(muse2.FAR)
    a = muse2.build("副业怎么定价")
    b = muse2.build("副业怎么定价", domain_offset=n)
    assert a["远域"]["领域"] == b["远域"]["领域"]