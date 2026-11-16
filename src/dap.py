#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright: DAP-protocol contributors
"""dap.py — RFC-DAP-0001 Delivery Acceptance Protocol 参考实现
零依赖（仅 Python 标准库），可离线运行。
三命令：init（锁定验收口径） / verify（校验交付回执并判定三态） / selftest（自检）。

核心：把"甲方验收"从主观感觉变成可复跑对账——承诺逐条 vs 交付证据 →
delivered/partial/missing 三态；并对关键功能做"改坏测试"（mutation probe），
证明验收器不是摆设（调用 GMB 协议思想：无检出力的验收器=背答案）。
"""
import argparse, json, math, os, sys, hashlib, datetime

VERSION = "0.1"
VERDICTS = ("delivered", "partial", "missing")
BANNED_CLAIMS = [
    "交付物100%符合", "100%符合", "验收器总体有效", "语义验收已自动化",
    "全部用例独立", "用例相互独立", "无需人工复核",
]


def wilson(k, n, z=1.96):
    """Wilson score 95% 区间。n=0 返回 (0,0) 并由调用方判无效。"""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def cmd_init(args):
    """生成一份"看交付物之前先锁定"的验收口径模板，并打印其 sha256。"""
    tpl = {
        "dap_version": VERSION,
        "project_id": args.project_id,
        "locked_at": datetime.datetime.now().astimezone().isoformat(),
        "acceptance_criteria": [
            {"id": "C1", "proposal_claim": "TODO: 承诺项原文", "evidence_type": "command|artifact|log",
             "pass_condition": "TODO: 可观测、可复跑的通过条件", "semantic": False}
        ],
        "thresholds": {
            "min_delivered_ratio": 0.8,
            "mutation_must_be_caught": True,
            "min_replay_commands": 1,
            "max_replay_commands": 5,
        },
        "mutation_targets": ["TODO: 选 1–2 个关键功能做改坏测试"],
        "honesty_scope": "结构可复跑；语义正确性需人工复核——见 RFC §5",
        "note": "Lock this file (compute sha256) BEFORE inspecting the delivery. Any edit invalidates the acceptance.",
    }
    out = args.out or "acceptance_protocol.json"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(tpl, f, ensure_ascii=False, indent=2)
    print(json.dumps({"status": "INIT", "file": out, "sha256": sha256_file(out)}, ensure_ascii=False))
    return 0


def load_protocol(args):
    if args.protocol and os.path.isfile(args.protocol):
        p = json.load(open(args.protocol, encoding="utf-8"))
        return p.get("thresholds", {}), {
            "protocol": args.protocol, "protocol_sha256": sha256_file(args.protocol), "defaulted": False}
    defaults = {"min_delivered_ratio": 0.8, "mutation_must_be_caught": True,
                "min_replay_commands": 1, "max_replay_commands": 5}
    return defaults, {"protocol": None, "protocol_sha256": None, "defaulted": True}


def _flag_banned_claims(text):
    return [c for c in BANNED_CLAIMS if c in text]


def cmd_verify(args):
    """校验交付回执：三态复算 + Wilson 区间 + 变异抽检 + 诚实边界。"""
    r = json.load(open(args.receipt, encoding="utf-8"))
    th, prov = load_protocol(args)
    issues = []

    # 1) 口径先定后测
    if r.get("criterion_before_evidence") is not True:
        issues.append("RED:criterion_before_evidence≠true（口径未先锁定）")

    # 2) 三态枚举合法性 + 计数复算
    claims = r.get("claims", [])
    if not claims:
        issues.append("INVALID:claims 为空")
    counts = {v: 0 for v in VERDICTS}
    for i, c in enumerate(claims):
        v = c.get("verdict")
        if v not in VERDICTS:
            issues.append(f"INVALID:claims[{i}].verdict={v!r} 非三态")
            continue
        counts[v] += 1
        # 证据类型与复跑命令
        if c.get("evidence_type") not in ("command", "artifact", "log"):
            issues.append(f"INVALID:claims[{i}].evidence_type 非法")
        # 语义项若无人工复核证据却标 delivered → 抓出（这是 DAP 的诚实闸）
        if c.get("semantic") is True and c.get("verdict") == "delivered" and not c.get("human_recheck"):
            issues.append(f"SEMANTIC:claims[{i}] 语义项无 human_recheck 却判 delivered——语义不可自动断言")
    reported_counts = r.get("counts", {})
    for v in VERDICTS:
        if v in reported_counts and reported_counts[v] != counts[v]:
            issues.append(f"MISMATCH:counts.{v} 报告 {reported_counts[v]} 复算 {counts[v]}")

    # 3) delivered 比例 + Wilson 区间复算
    n = len(claims)
    d = counts.get("delivered", 0)
    ratio = round(d / n, 6) if n else 0.0
    lo, hi = wilson(d, n)
    rep = r.get("delivered_ratio_wilson95")
    if not rep or len(rep) != 2:
        issues.append("RED:缺 delivered_ratio_wilson95")
    else:
        if abs(rep[0] - lo) > 0.02 or abs(rep[1] - hi) > 0.02:
            issues.append(f"MISMATCH:Wilson 报告 {rep} 复算 {[round(lo,4),round(hi,4)]}")
    min_ratio = th.get("min_delivered_ratio", 0.8)
    # 阈值未达标 = PARTIAL 的证据，不是红牌（红牌只给"流程违规/数字造假/验收器摆设"）
    below_threshold = ratio < min_ratio

    # 4) 变异抽检（调用 GMB 思想：验收器须能抓到改坏）
    mp = r.get("mutation_probe")
    if not mp:
        issues.append("RED:缺 mutation_probe（未证明验收器有检出力）")
    else:
        if mp.get("mutations", 0) < 1:
            issues.append("INVALID:mutations<1")
        if mp.get("caught", 0) < 1:
            issues.append(f"FAIL:变异抽检 caught={mp.get('caught',0)}——验收器抓不到改坏，是摆设")
        mp_rep = mp.get("catch_ratio_wilson95")
        if not mp_rep or len(mp_rep) != 2:
            issues.append("RED:mutation_probe 缺 Wilson 区间")
        else:
            mk, mn = mp.get("caught", 0), mp.get("mutations", 0)
            mlo, mhi = wilson(mk, mn)
            if abs(mp_rep[0] - mlo) > 0.02 or abs(mp_rep[1] - mhi) > 0.02:
                issues.append(f"MISMATCH:mutation Wilson 报告 {mp_rep} 复算 {[round(mlo,4),round(mhi,4)]}")

    # 5) 四不宣称（全文扫）
    blob = json.dumps(r, ensure_ascii=False)
    flagged = _flag_banned_claims(blob)
    if flagged:
        issues.append(f"RED:禁用宣称 {flagged}")

    # 6) 语义边界声明必须存在且诚实
    if r.get("semantic_scope") not in ("unverified", "manual-recheck-required"):
        issues.append("RED:semantic_scope 必须声明 unverified 或 manual-recheck-required")

    # 判定：红牌（issues 非空）→ FAIL；流程合规但交付未达标/有 missing → PARTIAL；全达标 → PASS
    if issues:
        verdict = "FAIL"
    elif not below_threshold and counts.get("missing", 0) == 0 and mp and mp.get("caught", 0) >= 1:
        verdict = "PASS"
    else:
        verdict = "PARTIAL"

    out = {
        "tool": "dap.py v%s (RFC-DAP-0001 reference implementation)" % VERSION,
        "receipt": os.path.basename(args.receipt),
        "provenance": prov,
        "thresholds": th,
        "recompute": {"counts": counts, "delivered_ratio": ratio, "delivered_ratio_wilson95": [round(lo,4), round(hi,4)]},
        "issues": issues,
        "verdict": verdict,
        "honesty_note": "本报告只对结构可复跑项对账；语义正确性须人工复核，不构成'交付物100%符合'或'验收器总体有效'的宣称。",
    }
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return {"PASS": 0, "PARTIAL": 1, "FAIL": 2}[verdict]


def _check(receipt_obj, expected):
    """把回执写到临时文件再跑 verify，返回实际 verdict。"""
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(receipt_obj, f, ensure_ascii=False)
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    old = sys.argv
    try:
        sys.argv = ["dap.py", "verify", "--receipt", path]
        with redirect_stdout(buf):
            cmd_verify(argparse.Namespace(receipt=path, protocol=None))
    finally:
        sys.argv = old
        os.unlink(path)
    out = json.loads(buf.getvalue())
    return out["verdict"]


def cmd_selftest(args):
    """三例自检：结构达标→PASS；语义虚标→FAIL；变异抓不到→FAIL。"""
    # 区间一律用 wilson() 真值生成，禁止手填（GMB 轮踩过手填上界的坑）
    w_full = [round(x, 4) for x in wilson(2, 2)]     # [0.3424, 1.0]
    w_zero = [round(x, 4) for x in wilson(0, 2)]     # [0.0, 0.6576]
    base = {
        "dap_version": VERSION, "criterion_before_evidence": True,
        "semantic_scope": "manual-recheck-required",
        "claims": [
            {"id": "C1", "evidence_type": "command", "verdict": "delivered", "semantic": False},
            {"id": "C2", "evidence_type": "artifact", "verdict": "delivered", "semantic": False},
        ],
        "counts": {"delivered": 2, "partial": 0, "missing": 0},
        "delivered_ratio_wilson95": w_full,
        "mutation_probe": {"mutations": 2, "caught": 2, "catch_ratio_wilson95": w_full},
    }
    cases = []
    # T1 结构达标 → PASS
    cases.append(("达标回执 → PASS", "PASS", _check(base, "PASS")))
    # T2 语义虚标（语义项无人工复核却 delivered）→ FAIL
    import copy
    t2 = copy.deepcopy(base)
    t2["claims"][0]["semantic"] = True
    cases.append(("语义虚标 → FAIL", "FAIL", _check(t2, "FAIL")))
    # T3 变异抓不到 → FAIL
    t3 = copy.deepcopy(base)
    t3["mutation_probe"]["caught"] = 0
    t3["mutation_probe"]["catch_ratio_wilson95"] = w_zero
    cases.append(("变异零检出 → FAIL", "FAIL", _check(t3, "FAIL")))

    all_ok = True
    for name, exp, got in cases:
        ok = exp == got
        all_ok &= ok
        print(f"{'PASS' if ok else 'FAIL'} {name} (expect {exp}, got {got})")
    print("")
    print("selftest: %d/%d → %s" % (sum(1 for _, e, g in cases if e == g), len(cases), "ALL-PASS" if all_ok else "HAS-FAILURE"))
    return 0 if all_ok else 2


def main():
    ap = argparse.ArgumentParser(description="DAP — Delivery Acceptance Protocol (RFC-DAP-0001)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("init", help="锁定验收口径模板（看交付物之前）")
    p1.add_argument("--project-id", default="demo-project")
    p1.add_argument("--out", default=None)
    p1.set_defaults(func=cmd_init)
    p2 = sub.add_parser("verify", help="校验交付回执并判定三态")
    p2.add_argument("--receipt", required=True)
    p2.add_argument("--protocol", default=None)
    p2.set_defaults(func=cmd_verify)
    p3 = sub.add_parser("selftest", help="自检三例")
    p3.set_defaults(func=cmd_selftest)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
