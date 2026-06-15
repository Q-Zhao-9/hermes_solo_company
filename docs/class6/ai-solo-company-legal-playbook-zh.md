# AI Solo Company 公司法律 Playbook 示例

> 用途：这是一个面向小型 AI Solo Company 的课堂示例法律 playbook，适用于网站搭建、聊天机器人部署、AI 工作流自动化、培训与支持等业务。它用于**首轮审查支持**，不是最终法律意见。

## 1. 公司画像

- **业务模式：** 创始人主导的小型 AI 服务 + 软件化实施公司
- **典型服务：** 网站/聊天机器人搭建、AI 工作流集成、培训、支持订阅、轻量软件模块
- **风险立场：** 避免承担超过个人或小团队承受能力的企业级法律责任
- **教学目标：** 让学生理解公司如何把收到的法律文本与自己的“优先条款/底线条款”进行对比

## 2. 不可突破的审查边界

- AI 审查只能作为**首轮审查支持**。
- 任何**高风险偏离**、缺少关键保护、或表述模糊的内容，都必须升级为**人工法律复核**。
- 即使条款与 playbook 一致，如果交易金额大、跨境、涉及监管行业，或具有战略重要性，仍然应交给人工复核。

## 3. 商业条款偏好

### 付款条款
- 项目制工作优先争取 **30%–50% 预付款**。
- 标准发票账期优先为 **net 7** 或 **net 14**。
- 除非价格已经充分覆盖现金流风险，否则应避免超过 **net 30** 的账期。
- 客户不能因为轻微延迟或非重大问题，普遍性扣留无争议款项。

### 退款与信用额度
- 一旦定制化实施已经开始，预付款应默认不可退。
- 订阅型/服务型 credit 应该有明确、有限的规则。
- 避免出现“任何时候任何不满意都可全额退款”这类开放式承诺。

### 范围变更控制
- 超出原始范围的请求必须经过书面确认、重新报价、或变更单。
- 避免无限次修改、无限支持、或无边界战略咨询义务。

### 期限与续费
- 自动续费只有在**续费周期、通知方式、取消方式**都清晰时才可接受。
- 避免无提醒、无清晰退出路径的静默自动续费。
- 对持续支持服务，双方应在通知后具有明确终止路径。

## 4. 知识产权与交付物立场

### 背景 IP
- 公司保留对既有 prompts、模板、工作流、可复用代码、know-how、内部 agent 系统、培训材料的所有权。
- 客户仅获得协议中明确授予的最终交付物权利。

### 客户定制交付物
- 已付费的定制交付物，可按协议约定转让或许可给客户。
- 公司仍应保留对通用思路、know-how、非机密模式、背景系统的复用权。

### 第三方工具
- 协议应允许合理使用第三方 API、AI 模型、开源工具、插件、托管服务，并受其各自条款约束。
- 公司不应保证所有第三方服务始终可用或绝对无错误。

## 5. 数据与隐私立场

- 不要承诺“绝对安全”或“零风险安全”。
- 如果处理个人数据，协议或隐私政策应以务实方式说明用途、主要处理方、以及保留逻辑。
- 如果实际运营中会使用分包商或第三方服务，就不要承诺“绝不使用第三方”。
- 不要对客户提供内容、数据质量、或客户违法指令承担全部责任。

## 6. 责任条款立场

### 责任上限
- 强偏好：总责任上限为**前 12 个月已支付费用**或**协议项下已支付总费用**。
- **无限责任**属于高风险偏离。

### 排除损害
- 优先排除间接、附带、后果性、特殊损害以及利润损失。

### 赔偿责任（Indemnity）
- 避免对对方作出宽泛、单向赔偿承诺。
- 如果存在赔偿责任，应尽量收窄到特定违约、IP 侵权、或由赔偿方自身行为导致的问题。
- 不应为对方的误用、对方的数据、或对方的指令承担无限延伸赔偿。

## 7. 运营保护立场

- 对于**未付款**、**安全风险**、**滥用行为**、或**法律/合规风险**，公司应保留暂停服务的权利。
- 合同终止后，客户仍应支付终止前已完成工作的费用。
- 任何 SLA 或 uptime 承诺必须符合公司真实支持能力。
- 避免暗示 AI 输出一定准确、一定合规、或适合所有用途。

## 8. 争议解决与适用法律

- 优先选择务实、成本可控的争议解决条款。
- 避免对 solo company 来说过于昂贵或不现实的远程管辖地。
- 适用法律最好与公司所在地一致，或至少选择中立、现实可执行的司法地。

## 9. 关键保护清单

在相关文档中，如果以下内容缺失，应标记为 **missing key protection**：

- liability cap（责任上限）
- payment timing（付款时间）
- termination / suspension rights（终止 / 暂停权）
- background IP reservation（背景 IP 保留）
- third-party tools permission（第三方工具许可）
- confidentiality baseline（基础保密义务）
- change-control or scope boundary language（范围控制/边界）
- basic data/privacy purpose language（涉及数据处理时的数据用途说明）

## 10. Playbook 对齐标签

审查时使用这些标签：

- **aligned**
- **acceptable_with_note**
- **outside_playbook**
- **high_risk_deviation**
- **missing_key_protection**

## 11. 高风险升级触发条件

出现以下内容时应升级人工复核：

- 无限责任
- 宽泛、单向赔偿责任
- 转让所有公司工具、prompts、代码、工作流 IP
- 客户广泛扣留付款的权利
- 公司对未付款或 abusive 行为没有退出/暂停权
- 超出实际运营能力的隐私或安全承诺
- 为第三方 AI / 模型 / 平台行为承担全部责任
- 无明确通知/取消路径的静默自动续费
- 对修改次数或范围增长没有任何限制

## 12. 推荐 fallback redline

### 责任上限 fallback
> Company’s aggregate liability will not exceed the fees paid under this Agreement in the 12 months before the claim.

### 背景 IP fallback
> Company retains ownership of all pre-existing materials, prompts, templates, know-how, reusable code, systems, and tools used to provide the Services.

### 付款 fallback
> Customer will pay undisputed invoices within 14 days. Company may suspend work for overdue undisputed amounts after written notice.

### 赔偿 fallback
> Each party will indemnify the other only for third-party claims arising from its own gross negligence, willful misconduct, or infringement caused by materials it supplied.

### 范围控制 fallback
> Requests outside the agreed scope require written approval, timeline review, and any applicable fee adjustment before work begins.

### 续费 fallback
> Any renewal must state the renewal term, pricing, notice window, and cancellation method.

## 13. 学生如何使用这个 playbook

1. 先识别文档类型：合同、隐私政策、还是服务条款。
2. 把条款映射到对应的 playbook 主题。
3. 引用风险条款原文。
4. 标记它是 aligned、acceptable with note、outside playbook、high-risk deviation，还是 missing key protection。
5. 用商业语言解释为什么重要。
6. 给出 redline 或下一步建议。
7. 对高风险或不确定内容升级人工复核。
