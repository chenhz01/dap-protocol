<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# RFC-DAP-0001: DAP — Delivery Acceptance Protocol

**状态**：Draft v0.1（可实施草案）
**日期**：2026-11-16
**署名**：DAP-protocol contributors（组织署名，非个人）
**.About**：一份给「甲方验收 AI 交付物」用的开放协议。把"付尾款前知道交付物真做了什么"从主观感觉变成**可复跑对账**：承诺逐条 vs 交付证据 → delivered / partial / missing 三态；并对关键功能做"改坏测试"证明验收器不是摆设。本协议定义术语、字段、纪律与三态判定，不定义任何具体项目的验收实现。

---

## 0. 一句话（费曼层）

甲方付钱前最怕一句话："做完了"，但不知道真做没做。DAP 让乙方在报价时就把"怎么算交付"写死（可复跑命令/产物/日志 + 通过条件），交付时逐条对账——**做得到=delivered、做了一半=partial、没有=missing**。再对 1–2 个关键功能故意"改坏"，看验收器会不会报警：报警说明验收有检出力，不报警说明这套验收是摆设。**诚实边界**：这套对账只证明"结构可复跑"，"数字/语义对不对"必须人工复核——协议不会、也不宣称能自动判。

## 1. 问题定义

### 1.1 现象
AI 外包/乙方交付普遍停在"我做了"的自陈层。甲方缺乏可复跑的验收依据，付尾款等于赌。现有验收方式（看截图、听演示、对需求文档逐条打勾）全是主观的，且**验收器本身从不被检验**——一张只会打勾的清单和一套真能发现问题的验收，从表面看不出区别。

### 1.2 本协议回答的唯一问题
> **甲方的验收，有多少是可复跑对账得出的，有多少是乙方自陈 + 甲方不好意思追问？**

### 1.3 范围外
- 不判定语义正确性（数字是否与源表一致、功能是否"真的好用"）——须人工复核（§5）。
- 不做项目管理和合同仲裁，只提供机器可校验的验收回执。
- 不证明交付物的法律/安全合规。

## 2. 术语（Normative）

| 术语 | 定义 |
|---|---|
| **Proposal claim (Cᵢ)** | 报价/合同阶段写下的单条承诺，带 `pass_condition`（可观测、可复跑的通过条件）。 |
| **Acceptance criterion** | 全部承诺 + 阈值 + 变异目标，在看交付物**之前**锁定并记 sha256。 |
| **Evidence type** | `command`（可粘贴复跑的命令）/ `artifact`（文件产物）/ `log`（运行日志）。 |
| **delivered** | 承诺有对应证据且通过条件成立。语义项须额外有 `human_recheck`。 |
| **partial** | 有部分证据但未完全满足通过条件（如文档存在但缺章节）。 |
| **missing** | 无对应证据。 |
| **Mutation probe** | 对 1–2 个关键功能故意改坏，检验验收器是否报警；调用 GMB 协议思想（见 §6）。 |
| **Four non-claims** | 见 §4.4。 |

## 3. 强制纪律（Must，缺一不可）

1. **Criterion-before-evidence**：验收口径（承诺清单/阈值/变异目标）必须在看交付物之前写入锁定文件并记 sha256。
2. **Three-state mandatory**：每条承诺必须落 delivered/partial/missing 之一，禁止"基本完成""大致OK"等模糊态。
3. **Evidence replayable**：`command` 类证据必须给出可粘贴复跑的命令 + 预期输出；`artifact` 给出路径与判定规则；`log` 给出锚点行。
4. **Mutation probe mandatory**：至少 1 个关键功能做改坏测试且被验收器抓到；0 检出 = 验收器是摆设 = FAIL。
5. **Interval reporting**：`delivered_ratio` 与变异检出率必须带 Wilson 95% 区间，不得只报点估计。
6. **Semantic honesty**：语义项（数字一致性、语义正确性）标 `semantic:true` 时，判 delivered 必须附 `human_recheck`（第三方/抽样量/一致数）；否则 FAIL。
7. **Four non-claims**：禁止四种宣称——①交付物 100% 符合 ②语义验收已自动化 ③验收器总体有效 ④用例相互独立（无独立性证明）。

## 4. 验收回执 schema（DAP-Receipt）

机器可读定义见 `schema/dap_receipt.schema.json`。核心字段：

```json
{
  "dap_version": "0.1",
  "protocol_sha256": "<§3.1 锁定文件的 sha256>",
  "project_id": "string",
  "run_at": "ISO-8601",
  "criterion_before_evidence": true,
  "claims": [
    {"id": "C1", "proposal_claim": "承诺原文", "evidence_type": "command|artifact|log",
     "pass_condition": "可复跑通过条件", "verdict": "delivered|partial|missing",
     "semantic": false, "human_recheck": {"reviewer": "", "sample_n": 0, "agreed": 0}}
  ],
  "counts": {"delivered": 0, "partial": 0, "missing": 0},
  "delivered_ratio": 0.0,
  "delivered_ratio_wilson95": [0, 0],
  "mutation_probe": {"mutations": 0, "caught": 0, "catch_ratio_wilson95": [0, 0],
                     "method": "改坏方法说明"},
  "verdict": "PASS | PARTIAL | FAIL",
  "verdict_basis": "string",
  "semantic_scope": "unverified | manual-recheck-required",
  "four_non_claims_respected": true
}
```

### 4.1 判定三态（阈值须在 §3.1 锁定）

| 态 | 条件 |
|---|---|
| **PASS** | 无红牌 + `delivered_ratio` ≥ 阈值 + 无 missing + 变异抽检至少 1 次检出 |
| **PARTIAL** | 流程合规（无红牌、口径先定、变异有检出力），但交付未达标（ratio 不足或有 partial/missing）——**"验收跑完了，但结论是不能通过"**，是一等公民 |
| **FAIL** | 违反任一红牌 / 数字与公式复算不符 / 语义项虚标 delivered / 变异 0 检出 / 报了禁用宣称 |

> **关键区分**：阈值未达标是 **PARTIAL**（交付没做好，但验收过程可信），不是 FAIL（验收过程本身作弊）。CLI 严格按此判定——`BELOW` 不计入红牌 issues。

**`PARTIAL` 是"不能通过"的诚实表达，不是 PASS 的委婉说法，也不是 FAIL 的甩锅。**

## 5. 诚实边界（本协议的命门，必须随任何引用出现）

- DAP 只证明**结构可复跑**：命令能跑、产物存在、日志有锚点。
- **语义正确性不自动判**：报表数字是否与源表一致、功能语义是否真对，抽样人工复核（n、一致数如实写）。
- 自举证据（来自同一作者的能力证明卷宗，已脱敏）显示：结构类检测 `TPR=1.0 [0.7575,1]`，**语义类检测 `TPR=0.0 [0,0.2425]`**——语义级漏洞在这套闸下全漏。**这是本协议最重要的诚实声明**：任何把 DAP 说成"能自动证明交付物语义正确"的宣称都被这份回执证伪。
- 多变异抽检只测"验收器对已知改坏的敏感度"，不测验收器本身的正确性（需 GMB 协议，见 §6）。

## 6. 与 GMB 的上下游关系

DAP 与 `gmb-protocol`（RFC-0001 Gate Mutation Benchmark）是**互补的两层**，不是重复：

| | GMB（上游·元层） | DAP（下游·应用层） |
|---|---|---|
| 验的对象 | 验收器/门禁/judge 本身 | 乙方的交付物 |
| 核心问题 | 打分器有没有在背答案 | 交付物真做了什么 |
| 核心指标 | Δ = TPR(indep) − TPR(self) | delivered_ratio 三态 + 变异检出 |
| 谁用 | 评测/QA 工程 | 甲方/采购/中小企业主 |

**接口**：DAP §3.4 的变异抽检复用 GMB 协议思想——验收器若对改坏 0 检出，等价于 GMB 里的"自设计集全过、独立集全漏"（Δ 严重负），判为摆设。第三方要严谨检验验收器本身时，直接用 GMB 做正式体检。**两个仓互相引用，各自独立发布。**

## 7. 三源锚（Provenance，2026-11-16 实拉）

| 源 | 锚 | 实查状态 |
|---|---|---|
| 科研 | arXiv:2611.14581v1《When Evaluators of AI Agents Disagree》(cs.SE, 2026-11-10) | 实拉确认：2,160 episodes，judge 与 native scoring 仅 56.2% 一致；**boundary evaluator（无模型调用的最小规则检查）抓全 11 例 forbidden write，所有 judge 都没显著超过它**。直接支撑"最小可复跑判据 > LLM judge"命题。 |
| GitHub | `affaan-m/ECC`（实拉 2026-11-16：304,243★，MIT，pushed 2026-11-16） | 数百条已合并 PR（"gate effectiveness""target acceptance vs local verification""prepared verifier/effect state evaluation"等）——**验收方法论被第三方真实采纳的 E1 级证据**。注：机会库旧快照"3 条 PR/946 处改动"已过时，本文用实拉值。 |
| 内部实证 | 能力证明卷宗 hold-out 回执（已脱敏） | 结构 TPR=1.0、语义 TPR=0.0 [0,0.2425]、负对照 PASS、Δ=−1.0；这套"验收方法论全套实跑留档"是 DAP 的 self-bootstrap 来源。 |

## 8. 可证伪条件

本协议在以下任一成立时自我作废或收窄，须走 verdict-backfill，不得静默：
- **F1**：出现已发布协议，对"AI 交付物验收"做承诺-证据对账 + 变异抽检 + 三态 + 语义边界声明 → novelty 作废，转贡献 adapter。
- **F2**：主流项目（ECC/promptfoo 等）内建同样的"三态对账 + 变异抽检 + 语义人工复核闸" → 降为方法论引用。
- **F3**：第三方复跑，语义项 TPR 持续 >0.8（即语义可自动验收）→ 本协议"语义必须人工"的边界过保守，须放宽。
- **F4**：甲方访谈 ≥7/10 表示"验收我自己会做/不需要" → 需求假设作废（承袭机会库 M46 可证伪条件）。

## 9. 商业与双赢带

- **谁付钱**：被 AI 外包坑怕的中小企业主；采购方验收代理（机会库 M46 的下游变现件）。
- **最小可卖单元**：一次"自带验收包"的交付（承诺清单 + 可跑命令 + 对账回执 + 变异抽检报告）。
- **定价**：由市场决定，本协议不含价格（避免构成价格宣称）。
- **上游回馈**：向 boundary evaluator 学术思路（arXiv:2611.14581v1）投真实甲乙方场景验证；与 GMB 仓互引。
- **成本/风险**：语义项人工复核人力不杠杆，须靠协议化+抽样压降；最大风险是甲方嫌麻烦不用。

## 10. 已知边界（如实）

- n=5 的示例只有对账演示力，不证明任何真实项目交付质量。
- 变异抽检的"改坏算子"由验收方设计，仍可能过拟合（需 GMB 独立集）。
- 语义人工复核的标注者间一致性未量化。
- 单一案例自举，须第三方复跑（见 F3）。

---

*License: spec and data are CC BY 4.0 (LICENSE-DOCS); the reference implementation in `src/` is Apache-2.0 (LICENSE-CODE). Attribution: DAP-protocol contributors. 引用请注明 RFC-DAP-0001 与 `examples/sample_acceptance.json`。*
