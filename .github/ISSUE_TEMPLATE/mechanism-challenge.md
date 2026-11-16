<!-- SPDX-License-Identifier: CC-BY-4.0 -->
---
name: 机制质疑 / Mechanism challenge
about: 用你的交付验收回执挑战 DAP 的三态判定/语义边界/阈值，或指出更早的同类协议
title: "[CHALLENGE] "
labels: mechanism-challenge, needs-receipt
assignees: ''
---

<!--
F7 真讨论钩子：只认真讨论，不收自问自答，不收无回执的空谈。
DAP 的全部主张都必须能被复算，所以质疑也必须能被复算。
-->

## 你挑战的是哪一条？（必选其一）

- [ ] **三态复现差异**：你拿自己的交付验收，得到的 delivered/partial/missing 三态与本协议判定不同
- [ ] **语义边界异议**：你认为语义项可以自动判，不需要 human_recheck（RFC §3.6）
- [ ] **阈值异议**：min_delivered_ratio=0.8 / 变异必须检出 不合理
- [ ] **PARTIAL 定义异议**："验收可信但交付未达标判 PARTIAL"这个区分有问题
- [ ] **novelty 反例**：存在更早对 AI 交付物做承诺-证据对账 + 变异抽检 + 三态 + 语义边界声明的公开协议（RFC §8 F1）

## 你的回执（必填——没有回执的质疑不成立）

```json
{
  "dap_version": "0.1",
  "project_id": "...",
  "claims": [{"id": "C1", "verdict": "delivered|partial|missing", "semantic": false}],
  "counts": {"delivered": 0, "partial": 0, "missing": 0},
  "delivered_ratio": 0.0,
  "delivered_ratio_wilson95": [0, 0],
  "mutation_probe": {"mutations": 0, "caught": 0},
  "verdict": "..."
}
```

## 复现命令（必填）

```bash
python src/dap.py verify --receipt your_receipt.json
```

## 你预期看到什么，实际看到什么？

写清楚数字与三态，不要只写形容词。

## 如果成立，你想让协议怎么改？

具体到 RFC 某一节 / schema 某字段 / `src/dap.py` 某函数。

---
注：自问自答（自己开自己回）不会被回应。我们只回应带可复跑回执的质疑。
