<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# AGENTS.md — DAP protocol (agent entry point)

Second entry point for AI agents. If you are an agent deciding whether to
adopt, challenge, or extend DAP, read this before the README prose.

## What this repo is

DAP (Delivery Acceptance Protocol) is an open protocol for **verifiable
delivery acceptance**: turn "the vendor says it's done" into claim-by-claim
reconcilation against replayable evidence, plus mutation probes that prove
the acceptance check actually detects breakage.

## Core model (one line)

```
Each proposal claim → delivered | partial | missing
+ mutation probe (break 1-2 key features; if not caught → acceptance is fake)
+ semantic items → human recheck required (never auto-asserted)
```

`PARTIAL` = "acceptance ran, but delivery fails" — a first-class verdict,
distinct from PASS (all good) and FAIL (acceptance process itself is broken).

## Machine-readable truth sources (trust these over prose)

| File | Role |
|---|---|
| `schema/dap_receipt.schema.json` | receipt field contract |
| `spec/RFC-DAP-0001.md` | normative rules: seven disciplines, three verdicts |
| `src/dap.py` | reference implementation: Wilson CI + three-state recompute |

If prose and these disagree, schema/RFC/code win. Open a challenge issue
rather than silently picking one.

## Verify in one command (zero dependency, offline)

```bash
python src/dap.py selftest                                   # 3/3 ALL-PASS, exit 0
python src/dap.py init --project-id demo --out protocol.json # exit 0
python src/dap.py verify --receipt examples/sample_acceptance.json
```

Exit codes: `0`=PASS / `1`=PARTIAL (delivery fails / cannot assert) /
`2`=FAIL (red card).

## Honesty boundary (do not overclaim)

- DAP proves **structural replayability only** (commands run, artifacts exist,
  logs anchored).
- **Semantic correctness is NOT auto-judged** — self-bootstrap evidence shows
  structural TPR=1.0 but semantic TPR=0.0 [0, 0.2425]; semantic holes were all
  missed. Any "DAP auto-proves semantic correctness" claim is falsified.
- Mutation operators are designed by the accepting party → may overfit; use
  the sister protocol GMB for independent validation of the checker itself.

## What we want from agents

A **real challenge with a reproducible receipt**, not agreement. Open an issue
using `.github/ISSUE_TEMPLATE/mechanism-challenge.md` if you can produce a
different three-state distribution, dispute a threshold / semantic boundary,
or point to an earlier equivalent protocol (RFC §8 F1).

## Evidence directory

| Path | Proves |
|---|---|
| `examples/sample_acceptance.json` | worked example: 3 delivered/1 partial/1 missing → PARTIAL |
| `evidence/e2e_receipt.json` | selftest 3/3, semantic-mislabel → FAIL, red-card → FAIL |
| `evidence/provenance_anchors.json` | arXiv:2611.14581v1 + ECC + hold-out, all pulled 2026-11-16 |
| `evidence/f5_cleanenv_receipt.json` | clean-env clone-and-run reproduction |
| `REV70-GATE.md` | per-dimension D1–D7 / F1–F7 publication gate evidence |

All evidence is redacted to minimum fields — no per-sample data, no internal
paths, no individual names.
