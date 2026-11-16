<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# REV70 双七发表门禁表 — dap-protocol

> 依据 `标准-REV70双七发表门禁-v1.0.md`。D1–D7 = 工程尺（立仓），F1–F7 = 发表族（push 前）。
> **两把尺各管一段，不做综合分**（REV70 §2 纪律四）。逐维 PASS/FAIL + 证据，禁"综合就绪度 X/10 可以推"。
> 判定日期：2026-11-16。对象：本仓待推送文件集。

## 资产分型（先于双尺，两原则 v1.1 第〇章）

| 三问 | 答 | 结论 |
|---|---|---|
| 抄走得到什么 | 协议文本 + 对账 schema + 零依赖 CLI 骨架；价值需在自己交付场景标定才兑现 | B 型候选 |
| 价值在"知道"还是"被用" | 在被用（先占"可复跑交付验收"生态位、成为甲方验收的默认对账格式） | B 型 |
| 有无 L3 信息增量可藏 | 无——合作解锁的是"按领域标定承诺模板/通过条件/变异算子/语义复核规范"服务，不是文档能写的信息 | B 型 |

**终裁：B 型卡位工具仓。** 利益最大化 = 零摩擦传播 + 抢先占位 + 防御性公开。许可走 F21 双许可。与 GMB 是上下游两件，非重复件（D1 纪律一：独立判据去重已核）。

---

## 一、工程尺 D1–D7

| 尺 | 结果 | 证据 | 阻断 push？ |
|---|---|---|---|
| **D1 约束驱动** | PASS | `spec/RFC-DAP-0001.md` §1（问题/范围外）、§3 七纪律每条对应一个真实失败模式（口径漂移/模糊态/不可复跑证据/摆设验收器/点估计/语义虚标/虚妄宣称）；README §"和看演示打勾的区别"写明"我们不用交付后凭感觉，因为验收器从不被检验"。每条设计可追到约束。 | 否 |
| **D2 失效边界** | PASS | RFC §1.3 范围外（3 条）、§5 诚实边界（语义 TPR=0 自曝、"不自动判语义"）、§10 已知边界（4 条）、§8 可证伪条件 F1–F4（自我作废触发）；README §"诚实边界"同步。**最关键的失效边界（语义全漏）主动写在显眼位**。 | 否 |
| **D3 数据流可见** | PASS | `schema/dap_receipt.schema.json` 定义全部字段；`src/dap.py` 8 函数，核心 `cmd_verify` 分解（口径校验→三态复算→Wilson→变异抽检→禁用宣称→语义闸→判定）；`examples/sample_acceptance.json` 是 schema 实例化。输入→校验→输出一眼可见。 | 否 |
| **D4 零依赖** | PASS | `src/dap.py:13` 仅 `argparse,json,math,os,sys,hashlib,datetime` 全标准库；clean-env 实测 `third_party_imports=0`、`network_calls=0`（`evidence/f5_cleanenv_receipt.json`）。 | 否 |
| **D5 可测试性** | PASS | `python src/dap.py selftest` → 3/3 ALL-PASS exit=0（达标 PASS / 语义虚标 FAIL / 变异零检出 FAIL）；判定逻辑 `verify` 为可独立调用的纯校验；F5 clean-env 复跑一致。 | 否 |
| **D6 错误不静默** | PASS | `grep except` → 无裸 except；CLI 对语义虚标报 `SEMANTIC:claims[i] 语义项无 human_recheck 却判 delivered`、对假 Wilson 报 `MISMATCH`、对红牌报 `RED:` 并 exit=2；退出码三态 0/1/2 明确。 | 否 |
| **D7 演进留痕** | PASS | RFC 标 Draft v0.1 + 日期 + 组织署名；`evidence/e2e_receipt.json` 的 `design_fix_logged` 字段记录了"阈值未达标从 FAIL 修正为 PARTIAL"的语义 bug 修复动机；`evidence/provenance_anchors.json` 记录机会库旧数字被实拉值替换的纠正；版本升级须走 verdict-backfill（RFC §8）。 | 否 |

**工程尺结论：D1–D7 全 PASS，无阻断。**

---

## 二、发表族 F1–F7

| 族 | 结果 | 证据 | 阻断 push？ |
|---|---|---|---|
| **F1 定位/命名权** | PASS | README §"和看演示打勾的区别"精确占位品类词 **verifiable delivery acceptance（可复跑交付验收）**；无"最强/100%检出"标语；与 GMB 的"gate-effectiveness benchmark"构成上下游两品类，各自独立命名。novelty 可证伪条件公开（RFC §8 F1）。 | 否 |
| **F2 竞品对标实证** | PASS | RFC §7 + `evidence/provenance_anchors.json` 三源全带日期版本限定：arXiv:2611.14581v1（2026-11-10，实拉确认 56.2%/11-of-11）、affaan-m/ECC（304,243★ MIT pushed 2026-11-16，实拉 5 条相关合并 PR）、内部 hold-out（已脱敏）。**明确记录并纠正了机会库 M46 旧快照"3 条 PR"的过时数字**。 | 否 |
| **F3 机制差异化** | PASS | 三个差异机制各有可复现测试：①三态对账 → selftest T1（达标 PASS）；②语义诚实闸 → selftest T2（语义虚标 FAIL）；③变异抽检 → selftest T3（零检出 FAIL）。每条承诺有测试背书。 | 否 |
| **F4 数字诚实** | PASS | 所有比率带 Wilson 95%（示例回执 + schema 必填）；RFC §3.5 禁点估计；CLI 用 Wilson 复算，偏差 >0.02 判 MISMATCH；四不宣称写进每次 verify 的 `honesty_note`；**语义 TPR=0.0 的负面实证主动公开在 README 显眼位**，不藏。 | 否 |
| **F5 可复现** | PASS | **干净环境实测**（非原地）：12 公开文件复制到全新临时目录从零跑——selftest 3/3 exit=0、init exit=0、verify PARTIAL exit=1，全符预期；零第三方依赖零网络。证据 `evidence/f5_cleanenv_receipt.json`。README 安装命令已实测等价链路。R8 血案（clone 即跑未实测）已规避。 | 否 |
| **F6 Agent 可消费** | PASS | `AGENTS.md` 第二入口（机器真相源优先级 + 一键复跑 + 诚实边界 + 给 agent 的质疑指令）；`evidence/` 4 份结构化回执；`.github/ISSUE_TEMPLATE/mechanism-challenge.md` 机制质疑模板。对应 D63 共识。 | 否 |
| **F7 发现性杠杆** | PASS | README §"想质疑或复跑"只认真讨论；issue 模板明禁自问自答、无回执不讨论；**全仓无 star/issue 数量预期、无门面件涨星表述**；真讨论（r=+0.633）是唯一写进策略的信号。 | 否 |

**发表族结论：F1–F7 全 PASS，无阻断。**

---

## 三、REV70 四纪律留痕

| 纪律 | 执行 |
|---|---|
| 独立判据去重 | D/F 共 14 行无重复信号；已核 DAP 与 GMB 是上下游两件（验对象/核心问题/指标均不同），非同一判据拆两行充数。 |
| 成功样本反证 | 反证三伪杠杆并降权：堆工程件（无 CI badge 炫示）、抢大数字标语（F1 禁）、社交齐发（无）。 |
| actionable 标记 | 全表只写动作与判据，无 star≥1万 / issue≥100 等结果型判据。 |
| 逐维列证据禁综合分 | 每行 PASS/FAIL + 具体证据 + 阻断位，**无综合分、无就绪度 X/10**。 |

---

## 四、推前验证 + 回读（push 时执行，此处为预案）

1. selftest 全绿 exit=0 — 已达成（本机 + 干净环境双验）。
2. 显式文件列表提交 — 用 `PUSH_MANIFEST.json.files_to_push`，禁 `git add -A`。
3. push 前 `ahead=1 behind=0` 核 — push 时执行。
4. push 后 `gh api` 回读 author.login=committer.login=chenhz01 + README 首屏 — push 时执行。

> 本表只证明"按 REV70 双尺建仓与发表准备合规"，**不构成推送授权**。push 仍须善伦明确说"可以推"（二级授权）。
