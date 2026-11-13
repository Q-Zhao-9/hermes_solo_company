# mybnb Class 10 Bilingual Student Example

This file turns the mybnb orchestrator demo into a student-facing bilingual example that is easier to reuse in class.

---

## 1) Business Setup / 业务背景

**English**
- Brand: mybnb
- Offer: an Airbnb-like rental marketplace MVP
- Audience: early hosts, property managers, and renters
- Goal: explain the product clearly and generate launch interest

**中文**
- 品牌：mybnb
- 报价 / 产品：一个类似 Airbnb 的租赁平台 MVP
- 受众：早期房东、物业管理者和租客
- 目标：更清楚地解释产品，并为上线初期获取关注

---

## 2) Video Request Classification / 视频请求分类

**English**
- Primary job type: mixed workflow
- Source material state: likely website copy, product notes, and founder messaging
- Grounding sensitivity: medium
- Best route: `website-to-video-funnel -> short-video-content-factory -> google-veo-cinematic-video`

**中文**
- 主要任务类型：混合型工作流
- 源材料状态：大概率已有网站文案、产品说明和创始人表达素材
- 对事实一致性的要求：中等
- 推荐路线：`website-to-video-funnel -> short-video-content-factory -> google-veo-cinematic-video`

---

## 3) Why This Route Fits / 为什么这条路线合适

**English**
1. mybnb probably starts from offer or website copy, not from a final approved video script.
2. The first bottleneck is message extraction: what the marketplace does, for whom, and why it is different.
3. After the message is clear, the strongest topic can be upgraded into a promo concept.

**中文**
1. mybnb 更可能是从产品报价或网站文案开始，而不是从最终定稿的视频脚本开始。
2. 第一个瓶颈不是生成画面，而是先把信息提炼清楚：做什么、给谁做、为什么不一样。
3. 当核心信息清楚以后，再把最强的一个选题升级成宣传视频会更有效。

---

## 4) Recommended Stage Plan / 推荐阶段计划

| Stage | English | 中文 | Best skill |
|---|---|---|---|
| 1 | Extract launch messaging | 提炼上线期核心表达 | `website-to-video-funnel` |
| 2 | Build topic and hook batch | 生成选题和 Hook 批次 | `short-video-content-factory` |
| 3 | Upgrade one winning promo concept | 升级一个最强宣传概念 | `google-veo-cinematic-video` |
| 4 | Prepare production handoff | 准备制作交接包 | `ai-video-from-script` |

---

## 5) Student-Friendly Deliverables / 学员可直接理解的产物

**English**
- 10 short-video topics
- 10 hooks
- 3 scripts
- 1 winning promo direction
- 1 simple first-week batch plan

**中文**
- 10 个短视频选题
- 10 个 Hook
- 3 个脚本版本
- 1 个最值得升级的宣传方向
- 1 个第一周可执行的视频批次计划

---

## 6) Best Next Step / 最佳下一步

**English**
Start with `website-to-video-funnel` and ask Hermes to extract:
- offer summary
- host / renter pain points
- trust or proof gaps
- CTA angles
- 5 strongest short-video directions

**中文**
先从 `website-to-video-funnel` 开始，让 Hermes 提炼：
- 报价摘要
- 房东 / 租客痛点
- 信任或证明缺口
- CTA 角度
- 最强的 5 个短视频方向

---

## 7) Student Prompt Template / 学员可复制提示词

```text
Use video-generation-orchestrator for mybnb.
Business: mybnb
Offer: Airbnb-like rental marketplace MVP
Audience: early hosts, property managers, and renters
Goal: choose the best video workflow, then generate the first useful content batch.
Source state: website copy, product notes, and founder messaging
First return:
- video request classification
- recommended route
- first downstream skill
- best next step
Then generate:
- 10 short-video topics
- 10 hooks
- 1 strong 30-second script
- 1 first-week 5-video batch plan
Keep it review-first and practical.
```

```text
请为 mybnb 使用 video-generation-orchestrator。
业务：mybnb
报价：类似 Airbnb 的租赁平台 MVP
受众：早期房东、物业管理者和租客
目标：先选择最合适的视频工作流，再生成第一批有用内容。
源材料状态：网站文案、产品说明、创始人表达素材
请先返回：
- 视频请求分类
- 推荐路线
- 第一个下游技能
- 最佳下一步
然后再生成：
- 10 个短视频选题
- 10 个 Hook
- 1 个强一点的 30 秒脚本
- 1 个第一周 5 条视频计划
保持 review-first，且要实用。
```

---

## 8) Teaching Note / 教学备注

**English**
The key teaching lesson is: do not jump into cinematic generation too early. First extract the message, then generate the strongest promo idea.

**中文**
这个案例最重要的教学点是：不要太早跳进电影感生成。先把信息提炼清楚，再去做最强的宣传概念。
