# 第 6 课公司 Playbook 演示包

> 这个演示包可用于 Discord 聊天展示、学生/老师网页界面演示，或现场教学 walkthrough。它是教学脚本，不是最终法律意见。

## 1. 演示目标

向学生展示 **AI 法律与合规 Agent** 如何：

- 结构化审查法律文本
- 将条款与**公司法律 playbook**进行比较
- 标记偏差和缺少的关键保护
- 生成**人工复核队列**，而不是假装替代律师

## 2. 推荐演示流程

### Slide / 消息 1 — 为什么重要

**标题：** 小公司经常在没有准备好的情况下签高风险文件。

**讲解：**
- 创始人经常在没有固定方法的情况下审查服务协议、隐私政策、服务条款。
- AI 可以帮助整理审查、分类风险、并指出哪些内容必须交给人工法律复核。
- 安全承诺是**首轮审查支持**，而不是最终法律意见。

### Slide / 消息 2 — 第 6 课工作流

**标题：** 文档 → playbook → 风险标签 → 人工复核包

**讲解：**
1. 识别文档类型。
2. 将条款与公司 playbook 对比。
3. 给问题打 low / medium / high 风险标签。
4. 用商业语言解释为什么重要。
5. 将高风险或不清晰问题升级到人工复核。

### Slide / 消息 3 — 公司法律 playbook

**标题：** Playbook 定义了我们的 fallback positions。

**展示：**
- 付款时间
- 退款 / credit
- 自动续费
- 范围控制
- 责任上限
- indemnity
- 背景 IP
- 隐私 / 数据承诺
- 终止 / 暂停权

**关键句：**
> 没有公司 playbook，AI 只能发现通用风险。拥有 playbook 后，AI 才能把文档与公司的真实偏好条款进行比较。

### Slide / 消息 4 — 示例案例 1

**标题：** 含无限责任和 IP 转让的服务协议

**讲解：**
- 无限责任 = 高风险偏离
- 宽泛扣款权 = 高风险偏离
- 转让 prompts、模板、工具 = 高风险偏离
- 缺少未付款暂停权 = 缺少关键保护

**教学重点：** 学生应学会让 AI 建议 redline 和升级，而不是直接批准。

### Slide / 消息 5 — 示例案例 2

**标题：** 保留和共享表述模糊的隐私政策

**讲解：**
- 第三方共享语言过于宽泛
- 保留期限不够明确
- 用途限制较弱
- 安全表述较为现实，接近 aligned

**教学重点：** 有些条款是“部分合理、部分有风险”，模型应拆开分析。

### Slide / 消息 6 — 示例案例 3

**标题：** 含自动续费和单方修改的服务条款

**讲解：**
- 无提前通知的自动续费 = 高风险偏离
- 不可退款可能是 acceptable with note
- 单方变更需要通知和公平机制
- 暂停权可与 playbook 对齐

**教学重点：** AI 应能处理“混合质量条款”，而不是简单说整份文档好或不好。

### Slide / 消息 7 — 人工复核边界

**标题：** 哪些内容必须交给律师或合格审查人？

**应升级的情况：**
- 无限责任
- 宽泛单向赔偿
- 不清晰的数据/隐私义务
- 背景 IP 转让
- 缺少终止权或付款保护
- 在真实客户合同中出现的重要歧义

### Slide / 消息 8 — 学生交付物

**标题：** 学生最终要产出什么

学生应输出：
- document type
- short summary
- risk counts
- flagged findings
- playbook deviations
- human review queue
- next-step recommendation

## 3. 可直接发到 Discord 的中文短版

```md
## 第 6 课 — AI 法律与合规 Agent

**目标：** 教学生用 AI 做首轮法律审查，而不是替代律师。

### 工作流
文档 -> 公司 playbook -> 风险标签 -> 人工复核队列

### 为什么需要 playbook
有了公司 playbook，AI 才能根据公司的真实底线来判断：
- 付款条款
- 退款 / credit
- 自动续费
- 责任上限
- indemnity
- 背景 IP
- 隐私 / 数据处理
- 终止 / 暂停权

### 示例案例 1 — 服务协议
- 无限责任 -> 高风险偏离
- 宽泛付款扣留 -> 高风险偏离
- 转让 prompts/templates/tools -> 高风险偏离
- 缺少未付款暂停权 -> 缺少关键保护

### 示例案例 2 — 隐私政策
- 宽泛第三方共享 -> 高风险偏离
- 保留期限模糊 -> outside playbook
- 缺少用途限制 / 请求路径 -> 缺少关键保护
- 现实的安全表述 -> aligned

### 示例案例 3 — 服务条款
- 无通知自动续费 -> 高风险偏离
- 仅通过网站公告修改条款 -> outside playbook
- 不可退款 -> acceptable with note
- 因法律/运营风险暂停账户 -> aligned

### 核心规则
高风险或模糊问题必须升级人工复核。
```

## 4. 网页界面演示时建议打开的材料

在第 6 课网页资料区打开：

- `docs/class6/ai-solo-company-legal-playbook-zh.md`
- `docs/class6/playbook-sample-review-cases-zh.md`
- `docs/class6/class6-company-playbook-presentation-zh.md`
- `docs/class6/demo-inputs-zh.md`
- `docs/class6/human-review-checklist-zh.md`

## 5. 网页界面现场演示顺序

1. 打开 **Legal & Compliance Agent** 面板。
2. 先展示公司 playbook 链接。
3. 载入服务协议 demo，解释最强红旗条款。
4. 载入隐私政策 demo，比较共享/保留语言。
5. 载入服务条款 demo，解释续费与变更控制问题。
6. 最后复制人工复核包，并提醒学生：这**不是最终法律意见**。
