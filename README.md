<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# DAP — Delivery Acceptance Protocol

> **可复跑交付验收协议（verifiable delivery acceptance）。** 甲方付尾款前，把"做完了"变成承诺-证据逐条对账 + 改坏测试。不是又一个项目打勾清单，而是一套**验收口径先定、结果可复跑、语义不装懂**的开放协议。

[RFC-DAP-0001](spec/RFC-DAP-0001.md) · [JSON Schema](schema/dap_receipt.schema.json) · 零依赖参考实现 · 双许可（见文末） · 姊妹协议 [GMB](https://github.com/chenhz01/gmb-protocol)

## 一句话（费曼层）

乙方说"做完了"，甲方怎么知道真做了？DAP 让双方**在报价时就把"怎么算交付"写死**：每条承诺配一个可粘贴复跑的命令/产物/日志 + 通过条件。交付时逐条对账：**做得到=delivered、做了一半=partial、没有=missing**。再对 1–2 个关键功能故意改坏——验收器报警才算有检出力，不报警就是摆设。

**诚实边界**：这套对账只证明"结构可复跑"。数字对不对、功能语义对不对，**必须人工复核**——本协议不装懂，也不宣称能自动判（见下）。

## 它和"看演示打勾"的区别（F1 品类命名权）

| | 传统验收（看截图/演示/打勾） | DAP |
|---|---|---|
| 口径何时定 | 交付后凭感觉 | **看交付物之前锁定 + sha256** |
| 结论形态 | "基本完成 / 大致OK" | delivered / partial / missing 三态 |
| 验收器本身 | 从不被检验 | **改坏测试，0 检出=FAIL** |
| 语义正确性 | 假装一并判了 | **明确切出，人工复核** |

我们把这叫 **verifiable delivery acceptance（可复跑交付验收）**。若你见过更早对"AI 交付物"做承诺-证据对账 + 变异抽检 + 三态 + 语义边界声明的公开协议，请开 issue 告诉我们——这是 novelty 可证伪条件（RFC §8 F1），我们据此降级或转贡献。

## 一次验收三步

```bash
# 1) 看交付物之前先锁定验收口径（承诺清单/阈值/变异目标），记 sha256
python src/dap.py init --project-id my-project --out acceptance_protocol.json

# 2) 按 schema/dap_receipt.schema.json 填交付回执
#    claims 逐条 + counts + delivered_ratio(Wilson) + mutation_probe

# 3) 校验回执 → PASS / PARTIAL / FAIL
python src/dap.py verify --receipt examples/sample_acceptance.json
python src/dap.py selftest   # 应 3/3 ALL-PASS
```

退出码 `0=PASS / 1=PARTIAL（不能通过/不可断言） / 2=FAIL（红牌）`，可直接进 CI。仅 Python 标准库，零依赖，可离线。

## 三态的态度（关键区分）

- **PASS**：无红牌 + delivered 达标 + 无 missing + 变异抽检有检出。
- **PARTIAL**：验收流程可信（口径先定、变异有检出力），但**交付没达标**——"验收跑完了，结论是不能通过"。这是"不能通过"的诚实表达，不是 PASS 的委婉说法，也不是 FAIL 的甩锅。
- **FAIL**：红牌——口径没先锁 / 数字与公式复算不符 / 语义项无人工复核却标 delivered / 变异 0 检出 / 报了禁用宣称。

CLI 用 Wilson 公式复算区间、用 counts 复算三态、用 `semantic:true & delivered & 无 human_recheck` 抓语义虚标。手填假数字会被抓出。

## 七条纪律（违反任一，报告不得标为 DAP-conformant）

1. 验收口径（承诺/阈值/变异目标）在看交付物**之前**锁定
2. 每条承诺必须落 delivered/partial/missing，禁"基本完成"模糊态
3. 证据必须可复跑（命令+预期输出 / 产物路径 / 日志锚点）
4. 变异抽检强制：≥1 关键功能改坏且被抓到，0 检出=验收器是摆设
5. 比率必带 Wilson 95% 区间，不得只报点估计
6. 语义诚实：语义项判 delivered 必须附人工复核（谁/抽多少/一致多少）
7. 四不宣称：不喊 100%符合 / 语义已自动化 / 验收器总体有效 / 用例独立

## 与 GMB 的关系（互补两层，不是重复）

| | GMB（上游·元层） | DAP（下游·应用层） |
|---|---|---|
| 验什么 | 验收器/门禁本身 | 乙方交付物 |
| 问什么 | 打分器有没有在背答案 | 交付物真做了什么 |
| 指标 | Δ = TPR(indep) − TPR(self) | delivered_ratio 三态 + 变异检出 |

DAP 的变异抽检复用 GMB 思想：验收器对改坏 0 检出 ≈ GMB 里 Δ 严重负 = 摆设。要严谨体检验收器本身，直接用 GMB。两仓互引、各自独立发布。

## 诚实边界（本工具不做什么）

- **只证明结构可复跑**：命令能跑、产物存在、日志有锚点。
- **语义正确性不自动判**：数字是否与源表一致、语义是否真对，抽样人工复核（n/一致数如实写）。
- 自举证据显示：结构类检测 TPR=1.0 [0.7575,1]，**语义类检测 TPR=0.0 [0,0.2425]** —— 语义级漏洞在这套闸下全漏。任何"DAP 能自动证明语义正确"的说法都被证伪。
- 变异算子由验收方设计，仍可能过拟合（需 GMB 独立集验证）。
- 这是**协议**，不是"给你的交付打 90 分"的产品。它常常给出的答案是 PARTIAL（不能通过）。

## 三源锚（2026-11-16 实拉）

- **科研**：arXiv:2611.14581v1《When Evaluators of AI Agents Disagree》(cs.SE, 2026-11-10)——2,160 episodes，LLM judge 与 native scoring 仅 56.2% 一致，**无模型调用的 boundary evaluator 抓全 11 例 forbidden write，所有 judge 都没显著超过它**。
- **GitHub**：`affaan-m/ECC`（304,243★，MIT，pushed 2026-11-16）数百条合并 PR 含 gate effectiveness / target acceptance vs local verification / prepared verifier 等——验收方法论被真实采纳的 E1 证据。
- **内部实证**：能力证明卷宗 hold-out 回执（已脱敏）结构 TPR=1.0、语义 TPR=0.0、负对照 PASS、Δ=−1.0。

## 可证伪条件

出现已发布同类协议 → novelty 作废转贡献；主流工具内建同样三态+变异+语义闸 → 降为方法论；第三方复跑语义 TPR>0.8 → 放宽"语义须人工"边界；甲方访谈 ≥7/10 说"不需要" → 需求假设作废。详见 RFC §8。

## 想质疑或复跑？

本协议最想要的不是 star，而是**有人真的拿它验收自己的交付、然后来 challenge**。如果你复跑出不同的三态分布，或对语义边界/阈值有异议，请开 issue 附你的回执——真讨论是这个协议唯一的发现性杠杆。自问自答的 issue 不会被回复。

## 合作 / Collaboration

- **合作形式**：把 DAP 接入你现有的交付流程（报价阶段锁定验收口径、交付阶段自动对账）；或对你的一次 AI 交付做"自带验收包"体检并出机器可校验回执。
- **合作解锁内容**：按你的领域标定承诺清单模板与通过条件、适配你的证据格式（command/artifact/log）、定制变异算子与语义人工复核规范（这些是需要一起做的服务，不在文档里）。
- **联系方式**：见仓库 GitHub Issues（公开技术讨论）；商务合作走仓库主页所列对外邮箱。

## 安装

```bash
git clone https://github.com/chenhz01/dap-protocol.git
cd dap-protocol
python src/dap.py selftest     # 应 3/3 ALL-PASS
```

## License（双许可，constitution F21）

- `src/` 源码：**Apache-2.0**（含专利授权）— 见 [LICENSE-CODE](LICENSE-CODE)
- `spec/` `schema/` `examples/` `evidence/` 文档与数据：**CC BY 4.0** — 见 [LICENSE-DOCS](LICENSE-DOCS)
- 索引见 [LICENSE](LICENSE)。署名统一为 DAP-protocol contributors（组织署名，非个人）。
