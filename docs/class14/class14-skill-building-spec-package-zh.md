# Class 14 技能建设规格包（Option A）

> 面向 Hermes bot 的第 14 课技能建设方案。
> 目标：把“最终集成、演示与 30 天启动计划”做成一套老师可直接调用、学生可直接落地、并且能输出标准化结果包的技能系统。

## 一、Class 14 的课程定位

第 14 课不是新增一个孤立模块，而是把前 13 课已经完成的模块接成一个完整业务闭环：

**内容 / SEO / GEO / 短视频 → 网站 → AI 助手 → 线索表单 → CRM → 客服 Agent → 销售 Agent → 报价/跟进 → 客户成交与复购**

因此，Hermes 在第 14 课的职责不是“再生成一个内容”，而是：

1. 审计学生当前系统到底哪里可用
2. 检查端到端链路是否真的打通
3. 设计一个可信的最终 Demo
4. 给出最小启动修复路径
5. 输出 30 天启动计划
6. 输出每周运营 SOP
7. 输出课后作业与下次验收标准

---

## 二、Class 14 技能建设总目标

构建一套可复用技能体系，让 Hermes 可以在第 14 课中稳定产出以下交付物：

- 当前系统整合结论
- 端到端业务流程检查
- readiness score
- P0 / P1 / P2 阻塞项
- 最终 Demo 脚本与演示证据包
- 30 天启动计划
- 每周运营 SOP
- 课后作业
- 标准化课堂总结报告

---

## 三、现有技能盘点

### 1. 已有核心技能

#### `class14-teacher-workflow-orchestrator`
- **用途**：第 14 课老师总控技能
- **现状**：可用
- **价值**：负责课堂顺序与总体输出结构
- **建议**：保持为最外层总入口

#### `final-integration-launch-orchestrator`
- **用途**：输出完整整合结论、Demo、30 天计划、SOP
- **现状**：可用
- **价值**：作为学生视角/系统视角总总结技能
- **建议**：作为总输出器保留

#### `class14-system-audit-checker`
- **用途**：审计网站、助手、线索、CRM、销售、流量等模块
- **现状**：可用
- **价值**：适合作为 Class 14 Phase 1 审计器
- **建议**：后续和链路验证技能联动

#### `class14-final-demo-builder`
- **用途**：生成最终 Demo 结构与讲解脚本
- **现状**：可用
- **价值**：适合作为 Demo 主技能
- **建议**：补足“证据包”和“fallback 预案”能力

#### `class14-launch-blocker-fixer`
- **用途**：把问题分成 P0 / P1 / P2
- **现状**：可用
- **价值**：可稳定减少学生任务泛滥
- **建议**：后续接收更结构化的 audit / flow-validator 输出

#### `class14-30-day-launch-plan`
- **用途**：输出 4 周启动计划
- **现状**：可用
- **建议**：保留

#### `class14-weekly-operations-sop`
- **用途**：输出每周运营 SOP
- **现状**：可用
- **建议**：保留

#### `class14-launch-readiness-scorecard`
- **用途**：把 readiness 量化评分
- **现状**：可用
- **建议**：作为汇总结论的一部分输出

### 2. 现有体系的主要缺口

现有技能更多是在“模块审计”和“总结生成”层面；第 14 课最关键的 **链路闭环验证、Demo 证据准备、课后执行 handoff** 还不够强。

最需要补的缺口有 3 个：

1. **模块之间是否真的接通**
2. **最终演示有没有准备好备用证据**
3. **学生课后第一周具体该做什么**

---

## 四、建议新增技能规格

以下是建议优先建设的技能规格包。

---

## 4.1 `class14-end-to-end-flow-validator`

### 定位
专门检查第 14 课目标链路是否闭环，不只看模块“存在”，而是看每一段是否真的能从上一步流到下一步。

### 为什么需要
第 14 课的核心是“整合”。
如果只有模块审计，没有链路验证，就可能出现：
- 网站有 CTA，但表单不工作
- 表单存在，但线索没进 CRM
- CRM 有记录，但没人跟进
- 销售话术有了，但没有报价/提案下一步

### 触发场景
- 帮我检查 Class 14 最终链路
- 这个学生系统有没有真正打通
- 哪一段最影响启动
- 做最终集成审查

### 输入
- business_type
- target_customer
- website_status
- assistant_status
- lead_capture_status
- crm_status
- customer_service_status
- sales_followup_status
- quote_or_proposal_status
- content_or_traffic_status
- known_demo_assets
- missing_information

### 输出
- strongest_working_link
- weakest_broken_link
- broken_transitions
- minimum_launchable_loop
- must_fix_before_demo
- must_fix_before_launch
- assumptions

### 必检链路
1. 内容 / SEO / GEO / 短视频 → 网站入口
2. 网站 → CTA / 线索入口
3. CTA / 表单 → 线索提交
4. 线索提交 → CRM / 表格 / 数据库
5. CRM → 客服 / 跟进动作
6. 跟进动作 → 报价 / 提案 / 咨询下一步
7. 报价 / 提案 → 成交推进路径

### 推荐输出结构
```markdown
## 端到端链路总体判断
## 已打通链路
## 断裂链路
## 最影响启动的断点
## 最小可运行闭环
## Demo 前必须补的连接
## Launch 前必须补的连接
## 风险与假设
```

### 提示词结构建议
- 第一步：重述目标业务链
- 第二步：逐段检查每个 transition
- 第三步：明确每段状态：已打通 / 部分打通 / 未打通
- 第四步：提炼 strongest link / weakest link
- 第五步：给出最小闭环建议

### 与现有技能关系
- 上游输入：`class14-system-audit-checker`
- 下游输出给：`class14-launch-blocker-fixer`
- 汇总到：`final-integration-launch-orchestrator`

### 验收标准
- 能明确指出至少一个 strongest link
- 能明确指出至少一个 weakest broken link
- 能区分“模块存在”与“链路接通”
- 能给出最小可运行闭环，而不是泛泛而谈

---

## 4.2 `class14-final-demo-proof-builder`

### 定位
帮助老师/学生为最终演示准备“证据包”，避免 live demo 因单点失败而崩掉。

### 为什么需要
第 14 课 demo 经常出问题：
- 助手现场回答不稳定
- 表单提交失败
- CRM 页面打不开
- 网络慢导致体验差

所以需要一个“可信演示证据包”技能，专门准备：
- 关键页面
- 测试问题
- 样例 lead
- CRM 截图
- 报价样本
- fallback 话术

### 触发场景
- 帮我准备 Class 14 final demo
- 给我最终演示证据包
- 帮我降低现场演示失败风险

### 输入
- business_type
- demo_goal
- available_pages
- assistant_questions
- lead_capture_method
- crm_view_or_record
- quote_or_proposal_asset
- known_weak_modules
- available_screenshots
- available_backup_materials

### 输出
- demo_asset_checklist
- required_live_steps
- prepared_backup_assets
- preloaded_pages
- sample_lead_payload
- sample_crm_record
- quote_or_proposal_proof
- fallback_plan_by_failure_type

### 推荐输出结构
```markdown
## Demo 目标
## 必须现场展示的 live 模块
## 建议提前准备的证据包
## 建议预加载页面
## 建议测试问题
## 建议样例线索
## 建议 CRM / 跟进证明材料
## 建议报价 / 提案证明材料
## 常见失败场景与备用方案
## Demo 前 15 分钟检查清单
```

### 提示词结构建议
- 第一步：识别最终 demo 的收入路径
- 第二步：区分 live 必须项 vs 备份证据项
- 第三步：列出演示所需资产
- 第四步：针对每个高风险模块给 fallback
- 第五步：输出上场前检查清单

### 与现有技能关系
- 配合：`class14-final-demo-builder`
- 汇总到：`final-integration-launch-orchestrator`
- 也可被老师总控技能单独调用

### 验收标准
- 输出必须包含 live 演示项和 backup 项
- 至少包含 3 类 fallback：助手失败、表单失败、CRM/报价失败
- 输出应能直接转成课堂 demo 准备表

---

## 4.3 `class14-student-handoff-assignment-builder`

### 定位
把第 14 课结束后的建议，压缩成一个学生能真正执行的“课后 handoff 包”。

### 为什么需要
很多学生上完第 14 课后知道很多，但不会立刻执行。
这个技能要把“最后建议”收敛成：
- 1 个本周必须完成的作业
- 3 个具体行动项
- 明确截止时间
- 明确验收标准

### 触发场景
- 给这个学生一个课后作业
- 第 14 课结束后该做什么
- 帮我输出 student handoff

### 输入
- student_name
- business_type
- top_blockers
- demo_readiness
- launch_readiness
- available_weekly_capacity
- target_launch_date
- recommended_30_day_plan
- recommended_sop

### 输出
- one_primary_assignment
- three_action_items
- deadline_recommendation
- success_criteria
- review_evidence_required
- fallback_if_blocked

### 推荐输出结构
```markdown
## 课后总目标
## 本周唯一最重要作业
## 3 个具体行动项
## 完成标准
## 截止时间建议
## 下次复盘要提交的证据
## 如果卡住先做什么
```

### 提示词结构建议
- 第一步：确认当前最影响启动/演示的问题
- 第二步：只选一个主作业
- 第三步：拆成 3 个可执行动作
- 第四步：定义证据与完成标准
- 第五步：给出卡住时 fallback

### 与现有技能关系
- 接收：`class14-launch-blocker-fixer`、`class14-30-day-launch-plan`
- 输出给：老师课堂收尾、学生课后执行

### 验收标准
- 输出只能有 1 个主作业
- 动作项必须可执行、可提交证据
- 不能变成笼统路线图

---

## 五、第二批建议技能规格

---

## 5.1 `class14-launch-asset-checker`

### 定位
检查启动前资产是否齐备，避免学生“系统看起来有，但基础资产不完整”。

### 重点检查
- 首页
- 服务页 / 产品页
- FAQ
- 联系页 / CTA
- 助手知识库
- 线索表单字段
- CRM 字段
- 跟进模板
- 报价模板
- 隐私政策 / 服务条款
- SEO / GEO / 短视频的至少一套启动素材

### 输出
- asset_ready
- asset_missing
- demo_can_work_without_it
- launch_cannot_work_without_it
- recommended_minimum_asset_pack

### 价值
让第 14 课从“系统流程”延伸到“启动前资产齐套度”。

---

## 5.2 `class14-demo-script-personalizer`

### 定位
根据学生业务类型，输出更贴身的 Demo 讲解脚本。

### 建议支持路径
- 电商
- 本地服务
- AI 咨询

### 输出
- tailored_demo_opening
- tailored_questions_to_ask_assistant
- tailored_cta_flow
- tailored_close_script

### 价值
同一个 final demo builder 太通用时，这个技能负责“按行业翻译”。

---

## 5.3 `class14-launch-readiness-reporter`

### 定位
把 audit、flow validation、scorecard、blockers、demo、30-day、SOP 汇总成一个统一结果包。

### 输出
```markdown
## 总体判断
## readiness score
## 最强模块
## 最弱模块
## 端到端链路状态
## P0 / P1 / P2
## 最终 Demo 方案
## 30 天计划
## 每周 SOP
## 课后作业
## 风险与假设
```

### 价值
让老师在第 14 课结尾一键输出完整课堂总结。

---

## 六、Class 14 技能调用架构建议

### 老师主入口
`class14-teacher-workflow-orchestrator`

### 推荐调用顺序
1. `class14-system-audit-checker`
2. `class14-launch-readiness-scorecard`
3. `class14-end-to-end-flow-validator`
4. `class14-launch-blocker-fixer`
5. `class14-final-demo-builder`
6. `class14-final-demo-proof-builder`
7. `class14-30-day-launch-plan`
8. `class14-weekly-operations-sop`
9. `class14-student-handoff-assignment-builder`
10. `class14-launch-readiness-reporter`

### 系统总输出入口
`final-integration-launch-orchestrator`

建议它后续支持接收结构化中间结果，而不是只从自然语言总结二次生成。

---

## 七、Class 14 标准输出包规格

建议所有技能围绕同一个统一结果包 schema 工作，哪怕只是 markdown 输出，也尽量保持字段稳定。

### 建议顶层字段
- class_goal
- current_system_summary
- readiness_score
- module_audit
- flow_validation
- blocker_priority
- final_demo_plan
- final_demo_proof_pack
- launch_plan_30d
- weekly_sop
- handoff_assignment
- risks_and_assumptions

### 好处
- 老师课堂输出统一
- 后续能做 dashboard / CRM / 学生档案
- 后续能做 cohort 批量总结

---

## 八、技能提示词设计共性要求

所有 Class 14 技能建议遵守以下规则：

### 1. 不要假设系统真的可用
如果学生没证据，就标记：
- Unknown
- Missing
- Needs verification
- Demo only

### 2. 区分 Demo Ready 与 Launch Ready
这是第 14 课最重要的判断边界之一。

### 3. 优先最小可运行闭环
不要推动学生做更大更复杂的系统，而是帮助他先形成最小可启动路径。

### 4. 输出要偏运营语言，不要过度技术化
课程目标是学生能启动业务，不是做工程评审。

### 5. 每个技能都应给出“下一步”
避免学生拿到一份漂亮总结却不知道先做什么。

---

## 九、建设优先级建议

### 第一批（本周优先）
1. `class14-end-to-end-flow-validator`
2. `class14-final-demo-proof-builder`
3. `class14-student-handoff-assignment-builder`

### 第二批（紧接着做）
4. `class14-launch-asset-checker`
5. `class14-launch-readiness-reporter`
6. `class14-demo-script-personalizer`

### 第三批（课程成熟后）
7. `class14-cohort-review-dashboard`
8. `class14-reuse-and-clone-planner`
9. `class14-case-study-packager`

---

## 十、实施建议

### 先做的不是 UI，而是技能标准化
第 14 课目前最重要的是让老师能稳定出结果，所以应优先：
- 完成技能 prompt 结构
- 完成统一输出结构
- 完成样例输入/输出
- 完成教师课堂调用顺序

### 每个新增技能都建议配套 3 类文件
1. `SKILL.md`
2. 中文模板文件
3. 参考样例文件

### 每个技能至少要有的 linked files
- `templates/*.md`
- `references/*.md`

例如：
- flow validator → `templates/flow-validator-template-zh.md`
- demo proof builder → `references/demo-proof-example-zh.md`
- handoff builder → `templates/handoff-assignment-template-zh.md`

---

## 十一、可执行的下一步开发任务

### Task A
先起草以下 3 个技能：
- `class14-end-to-end-flow-validator`
- `class14-final-demo-proof-builder`
- `class14-student-handoff-assignment-builder`

### Task B
给每个技能补 1 个中文模板和 1 个中文参考样例。

### Task C
更新 `class14-teacher-workflow-orchestrator`，把这 3 个新技能加入推荐调用链。

### Task D
更新 `final-integration-launch-orchestrator`，让它能引用结构化中间结果。

---

## 十二、结论

Class 14 最重要的不是“再造新功能”，而是让 Hermes 成为：

- **整合审计器**
- **链路验证器**
- **Demo 设计器**
- **启动计划生成器**
- **学生课后 handoff 助手**

现有技能已经有了 70% 的框架。
真正要补的，是让第 14 课从“会总结”升级成“会交付、会落地、会推动启动”。

当前最值得先做的 3 个技能是：
- `class14-end-to-end-flow-validator`
- `class14-final-demo-proof-builder`
- `class14-student-handoff-assignment-builder`

这三个补齐后，Class 14 就会从“总结课”更接近“真正的最终整合启动课”。
