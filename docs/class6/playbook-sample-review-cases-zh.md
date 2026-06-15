# 第 6 课 Playbook 示例审查案例

> 这些课堂案例展示了如何**依据 AI Solo Company 公司法律 playbook**来审查示例法律文本。它们用于教学中的首轮审查示例，不是最终法律意见。

## 案例 1 — 服务协议审查

### 示例条款

```text
Customer may terminate this Agreement at any time for convenience upon written notice. Company will continue providing transition support for 60 days at no extra charge. Company’s liability is unlimited, and Customer may withhold any payment it reasonably disputes. All work product, methods, prompts, templates, automations, and tooling developed or used under this Agreement become Customer property upon payment.
```

### 文档类型
- contract

### 审查摘要包

- **summary:** 该条款在责任上限、付款保护、过渡支持边界、以及背景 IP 所有权方面都与公司 playbook 冲突。
- **overall_risk:** high
- **risk_counts:** low=0, medium=1, high=4
- **human_review_required:** true

### 发现项

1. **无限责任**
   - risk_level: high
   - playbook_position: 责任应限制在前 12 个月已支付费用或协议总已支付费用范围内
   - playbook_alignment: high_risk_deviation
   - why_it_matters: 对 solo AI 服务公司来说，无限责任可能带来无法承受的下行风险
   - suggested_follow_up: redline 为 fees-paid cap，并排除间接/后果性损害

2. **宽泛的付款扣留权**
   - risk_level: high
   - playbook_position: 客户应在 net 7 或 net 14 内支付无争议款项
   - playbook_alignment: high_risk_deviation
   - why_it_matters: 广泛扣留付款会严重影响小公司的现金流，并让对方获得过强杠杆
   - suggested_follow_up: 将扣留限制为具体、可证明的争议，且无争议部分必须支付

3. **背景 IP 被转让**
   - risk_level: high
   - playbook_position: 公司保留 prompts、模板、工作流、可复用代码、系统与 know-how
   - playbook_alignment: high_risk_deviation
   - why_it_matters: 该条款转让的不只是最终交付物，而是公司的可复用经营资产
   - suggested_follow_up: 明确保留背景 IP，只向客户授予最终已付款交付物的权利

4. **免费过渡支持没有边界**
   - risk_level: medium
   - playbook_position: 超范围工作应通过书面确认或变更单处理
   - playbook_alignment: outside_playbook
   - why_it_matters: 额外过渡支持可能无限扩展成无偿实施工作
   - suggested_follow_up: 定义过渡支持的具体范围/小时数，或改为可计费支持

5. **缺少未付款暂停权**
   - risk_level: high
   - playbook_position: 公司需要在逾期付款或 abusive 行为时拥有暂停/终止权
   - playbook_alignment: missing_key_protection
   - why_it_matters: 如果客户停止付款却继续要求服务，公司缺乏运营保护
   - suggested_follow_up: 加入对逾期无争议款项的书面通知后暂停权

### Playbook 偏差汇总

- aligned: 0
- acceptable_with_note: 0
- outside_playbook: 1
- high_risk_deviation: 3
- missing_key_protection: 1

### 建议下一步

- 升级人工法律复核
- 立即 redline 责任上限、付款扣留、背景 IP
- 在接受该条款前先明确过渡支持边界

---

## 案例 2 — 隐私政策审查

### 示例条款

```text
We collect names, emails, browser activity, device data, uploaded documents, and chatbot conversations. We may share personal data with trusted partners, affiliates, analytics providers, model providers, and service providers as needed to improve our services. We retain information for as long as useful to our business. We use commercially reasonable efforts to protect data and cannot guarantee absolute security.
```

### 文档类型
- privacy

### 审查摘要包

- **summary:** 该条款在安全表述上较为现实，但在共享范围、保留周期、以及用途限制方面过于宽泛，缺少清晰的用户权利说明。
- **overall_risk:** medium
- **risk_counts:** low=1, medium=3, high=1
- **human_review_required:** true

### 发现项

1. **共享语言过于宽泛**
   - risk_level: high
   - playbook_position: 应以务实方式说明主要处理方和关键第三方类别
   - playbook_alignment: high_risk_deviation
   - why_it_matters: “trusted partners, affiliates, analytics providers, model providers” 范围太广，容易被认为披露不足
   - suggested_follow_up: 收窄类别并说明每类接收数据的目的

2. **保留期限过于模糊**
   - risk_level: medium
   - playbook_position: 应说明务实的保留逻辑，而不是无限或仅以“业务需要”为理由
   - playbook_alignment: outside_playbook
   - why_it_matters: “as long as useful to our business” 过于开放，不利于合规与信任审查
   - suggested_follow_up: 增加按数据类别划分的保留逻辑或保留判断因素

3. **缺少用途限制细节**
   - risk_level: medium
   - playbook_position: 应说明数据处理的具体用途
   - playbook_alignment: missing_key_protection
   - why_it_matters: 用户和审查者无法区分哪些处理是服务必需，哪些是分析或产品改进
   - suggested_follow_up: 将收集的数据类别与明确用途对应起来

4. **安全表述较为现实**
   - risk_level: low
   - playbook_position: 避免承诺“绝对安全”
   - playbook_alignment: aligned
   - why_it_matters: 该条款正确避免了完美安全保证
   - suggested_follow_up: 保留这一平衡表达，并补充实际安全措施（如果有）

5. **用户权利/联系路径不清晰**
   - risk_level: medium
   - playbook_position: 隐私披露应支持访问、删除、联系路径等务实审查
   - playbook_alignment: missing_key_protection
   - why_it_matters: 用户需要知道如何提出隐私请求或咨询问题
   - suggested_follow_up: 增加请求/联系入口或链接到相应流程

### Playbook 偏差汇总

- aligned: 1
- acceptable_with_note: 0
- outside_playbook: 1
- high_risk_deviation: 1
- missing_key_protection: 2

### 建议下一步

- 修改共享类别和用途映射
- 增加保留逻辑与隐私请求路径
- 如果业务面向受监管行业或多法域用户，升级人工复核

---

## 案例 3 — 服务条款审查

### 示例条款

```text
Subscriptions renew automatically for successive 12-month terms unless canceled at least 72 hours before renewal. Fees are non-refundable. We may change pricing or these Terms at any time by posting an update on the website. We may suspend any account we believe creates legal, reputational, or operational risk.
```

### 文档类型
- terms

### 审查摘要包

- **summary:** 该条款在暂停权上部分符合 playbook，但在续费通知和单方修改公平性方面较弱。
- **overall_risk:** medium
- **risk_counts:** low=1, medium=3, high=1
- **human_review_required:** true

### 发现项

1. **自动续费但没有提前通知承诺**
   - risk_level: high
   - playbook_position: 自动续费只有在周期、通知、取消路径清晰时才可接受
   - playbook_alignment: high_risk_deviation
   - why_it_matters: 虽然有取消窗口，但没有提醒或提前通知义务
   - suggested_follow_up: 增加续费提醒时间和更清晰的取消步骤

2. **不可退款需要限定条件**
   - risk_level: medium
   - playbook_position: 退款/credit 应明确且有限，但也应解释取消或计费错误时如何处理
   - playbook_alignment: acceptable_with_note
   - why_it_matters: 严格不可退款可能可以接受，但前提是计费节奏和服务范围足够清晰
   - suggested_follow_up: 说明例外情形、计费错误处理、以及取消后的服务周期安排

3. **可随时单方修改条款**
   - risk_level: medium
   - playbook_position: 重大商业变更不应在没有合理通知或公平机制下直接生效
   - playbook_alignment: outside_playbook
   - why_it_matters: “posting an update on the website” 对重大价格或合同变更来说可能过弱
   - suggested_follow_up: 对重大变更加上通知期，并明确生效机制

4. **因法律/运营风险暂停账户**
   - risk_level: low
   - playbook_position: 公司应保留对法律、安全、滥用风险的暂停权
   - playbook_alignment: aligned
   - why_it_matters: 这为小公司提供了必要的运营保护
   - suggested_follow_up: 保留，但可补充示例避免过度模糊

5. **该摘录中缺少责任上限**
   - risk_level: medium
   - playbook_position: 责任上限是关键保护
   - playbook_alignment: missing_key_protection
   - why_it_matters: 如果整份 terms 缺少 limitation-of-liability，将留下重要风险缺口
   - suggested_follow_up: 确认完整条款中另有责任限制与损害排除条款

### Playbook 偏差汇总

- aligned: 1
- acceptable_with_note: 1
- outside_playbook: 1
- high_risk_deviation: 1
- missing_key_protection: 1

### 建议下一步

- 增加续费提醒语言
- 明确重大变更通知流程
- 确认完整 terms 中存在责任限制
- 在上线或真实使用前升级人工复核

---

## 教学提示

这些样例适合按以下顺序演示：

1. 服务协议 → 最强的 redline 示例
2. 隐私政策 → 网站/数据处理场景
3. 服务条款 → 订阅/平台场景

学生最终应始终输出：
- 风险标签摘要
- 人工复核队列
- playbook 偏差列表
- redline 或下一步建议
