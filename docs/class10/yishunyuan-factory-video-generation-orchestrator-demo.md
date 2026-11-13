# Yishunyuan Factory Video Generation Orchestrator Demo / 双语示例

This is a bilingual Class 10 example for a factory / industrial website that needs clearer short-video marketing and product explanation content.

这是一个双语的第 10 课示例，适用于需要更清楚的短视频营销与产品讲解内容的工厂 / 工业网站。

---

## 1) Source Material Snapshot / 源材料快照

**English**
- Brand: Yishunyuan Factory
- Business type: industrial / factory website and product sales
- Audience: overseas buyers, sourcing managers, distributors, and B2B prospects
- Goal: explain the factory's capabilities, product strengths, and trust signals more clearly
- Source state: website copy, product pages, factory photos, and company positioning already exist
- Constraint: keep the workflow practical, trust-oriented, and review-first

**中文**
- 品牌：Yishunyuan Factory
- 业务类型：工业 / 工厂网站与产品销售
- 受众：海外采购商、采购经理、经销商和 B2B 潜在客户
- 目标：更清楚地解释工厂能力、产品优势和信任信号
- 源材料状态：已经有网站文案、产品页面、工厂照片和公司定位素材
- 约束：保持流程实用、以信任为导向，并采用 review-first

---

## 2) Video Request Classification / 视频请求分类

**English**
- Primary job type: website/page-to-video repurposing with optional cinematic upgrade
- Source material state: existing website copy plus likely product/factory visuals
- Grounding sensitivity: high because manufacturing claims, certifications, production capacity, and product specifications must stay accurate
- Visual ambition: medium for the first batch, medium to high for a later factory-brand promo
- Likely best route: `website-to-video-funnel -> short-video-content-factory -> ai-video-from-script`
- Optional upgrade path: `website-to-video-funnel -> google-veo-cinematic-video`

**中文**
- 主要任务类型：网站 / 页面内容转视频，并可选择后续升级成更电影感的版本
- 源材料状态：已有网站文案，并且大概率已有产品 / 工厂视觉素材
- 对事实一致性的要求：高，因为制造能力、认证、产能和产品规格必须准确
- 画面野心：第一批以中等为主，后续工厂品牌宣传片可升级到中高
- 最可能的最佳路线：`website-to-video-funnel -> short-video-content-factory -> ai-video-from-script`
- 可选升级路线：`website-to-video-funnel -> google-veo-cinematic-video`

---

## 3) Recommended Route / 推荐路线

### Best default route for the first B2B batch / 第一批 B2B 内容的默认最佳路线
1. `video-generation-orchestrator`
2. `website-to-video-funnel`
3. `short-video-content-factory`
4. `ai-video-from-script`

### Why this route fits / 为什么这条路线合适

**English**
- The most likely starting asset is website or product-page copy, not an approved spoken script.
- The main challenge is extracting trustworthy B2B messaging: what the factory makes, who it serves, and why a buyer should trust it.
- `website-to-video-funnel` is the right first downstream skill because it can pull product angles, buyer questions, proof points, and CTA directions from site content.
- `short-video-content-factory` can then turn those extracted angles into a practical first batch of hooks, topics, and scripts.
- `ai-video-from-script` helps package the strongest concept into narration, subtitle, pacing, and editing instructions for simple production.
- Cinematic generation is useful later for a stronger brand or factory-floor promo, but not before the claims and positioning are clear.

**中文**
- 最有可能的起点是网站或产品页文案，而不是已经定稿的口播脚本。
- 最大难点在于提炼可信的 B2B 表达：工厂做什么、服务谁、以及为什么买家应该信任它。
- `website-to-video-funnel` 很适合作为第一个下游技能，因为它能从站点内容中提炼产品角度、买家问题、证明点和 CTA 方向。
- 然后 `short-video-content-factory` 可以把这些提炼结果转成第一批可执行的 Hook、选题和脚本。
- `ai-video-from-script` 可以把最强概念继续整理成旁白、字幕、节奏和剪辑说明，适合简单实操制作。
- 电影感生成更适合后续升级成品牌片或工厂宣传片，而不是在卖点与证明点还没清楚时就提前进入。

---

## 4) Stage Plan / 阶段计划

| Stage | English goal | 中文目标 | Deliverable / 产物 | Best skill |
|---|---|---|---|---|
| 1 | Classify and route the request | 先做分类并决定路线 | workflow recommendation / 工作流建议 | `video-generation-orchestrator` |
| 2 | Extract manufacturing messaging from the site | 从网站提炼制造与买家表达 | offer summary, buyer pain points, proof points, CTA map | `website-to-video-funnel` |
| 3 | Turn factory messaging into testable video concepts | 把工厂表达转成可测试的视频概念 | 10 topics, 10 hooks, 3 scripts, captions, batch plan | `short-video-content-factory` |
| 4 | Prepare the strongest concept for real production | 把最强概念整理成真实可制作版本 | voiceover/edit plan, scene order, subtitle notes | `ai-video-from-script` |

---

## 5) Deliverables by Stage / 分阶段产物

### Stage 1 / 阶段 1
**English**
- request classification
- recommended route
- recommended first downstream skill
- best next step

**中文**
- 请求分类
- 推荐路线
- 推荐的第一个下游技能
- 最佳下一步

### Stage 2 / 阶段 2
**English**
- offer summary from actual website copy
- buyer pain points by audience type
- proof signals such as quality, experience, export, factory scale, or process control
- CTA map for inquiry, quote request, or distributor contact

**中文**
- 从真实网站文案提炼出的报价摘要
- 按受众拆分的买家痛点
- 质量、经验、出口、工厂规模、流程控制等证明信号
- 针对询盘、报价申请或经销联系的 CTA 路径图

### Stage 3 / 阶段 3
**English**
- 10 short-video topics
- 10 hooks
- 15s / 30s / 60s scripts
- platform caption pack
- first 5-video batch recommendation

**中文**
- 10 个短视频选题
- 10 个 Hook
- 15 秒 / 30 秒 / 60 秒脚本
- 平台发布文案包
- 第一批 5 条视频建议

### Stage 4 / 阶段 4
**English**
- narration or subtitle draft
- scene order using available factory/product visuals
- editing notes for CapCut / Canva / simple editor
- publishing-ready structure

**中文**
- 旁白或字幕草稿
- 基于现有工厂 / 产品素材的场景顺序
- 面向 CapCut / Canva / 简单剪辑工具的编辑说明
- 可直接发布的结构整理

---

## 6) Decision Gates / 决策检查点

**English**
- Gate 1: approve extracted claims and proof points before script generation
- Gate 2: approve the strongest topic before deeper production prep
- Gate 3: approve the main 30-second script before recording voiceover or editing
- Gate 4: only move to cinematic generation after claim accuracy and trust positioning are locked

**中文**
- 检查点 1：先确认提炼出的卖点与证明点，再进入脚本生成
- 检查点 2：先确认最强选题，再进入更深的制作准备
- 检查点 3：先确认核心 30 秒脚本，再进入配音录制或剪辑
- 检查点 4：只有在卖点准确、信任定位清楚之后，才进入电影感生成

---

## 7) Risks and Constraints / 风险与约束

**English**
- Claim risk: do not overstate capacity, certification, product performance, or export experience
- Generic-message risk: weak extraction can produce bland factory marketing language with no real buyer value
- Visual risk: cinematic factory footage can look impressive while still saying nothing specific
- Production risk: first batch should use existing website and product assets before creating heavier promo material

**中文**
- 表述风险：不要夸大产能、认证、产品性能或出口经验
- 信息空泛风险：如果提炼不够好，很容易生成没有真实买家价值的工厂宣传空话
- 画面风险：工厂画面即使很酷，也可能依然没有说清楚具体卖点
- 制作风险：第一批内容应该优先使用现有网站和产品素材，再考虑更重的宣传片制作

---

## 8) Best Next Step / 最佳下一步

**English**
Run Stage 2 first.

Recommended Stage 2 prompt:

```text
Use website-to-video-funnel for the Yishunyuan factory website.
Business: Yishunyuan Factory
Offer: industrial factory products and manufacturing capability
Audience: overseas buyers, sourcing managers, distributors, and B2B prospects
Goal: extract the clearest buyer-facing messaging from the website and convert it into short-video source angles.
Output: offer summary, buyer pain points, proof points, CTA map, and the 5 strongest short-video directions to test first.
Keep it review-first, trust-oriented, and practical.
```

**中文**
先执行阶段 2。

推荐阶段 2 提示词：

```text
请对 Yishunyuan 工厂网站使用 website-to-video-funnel。
业务：Yishunyuan Factory
报价：工业产品与制造能力
受众：海外采购商、采购经理、经销商和 B2B 潜在客户
目标：从网站中提炼最清晰、最面向买家的表达，并把它转成短视频源材料角度。
输出：报价摘要、买家痛点、证明点、CTA 地图，以及最值得优先测试的 5 个短视频方向。
保持 review-first、信任导向，并且实用。
```

---

## 9) Optional Upgrade Path / 可选升级路径

**English**
If the team later wants:
- a stronger evidence-backed explainer from product docs and spec sheets -> use `notebooklm-to-video`
- a higher-production factory promo after messaging is approved -> use `google-veo-cinematic-video`
- a repeatable export-marketing content system -> branch into `short-video-campaign-orchestrator`

**中文**
如果后续团队希望：
- 基于产品文档和规格表做更有依据的讲解视频 -> 使用 `notebooklm-to-video`
- 在表达确认后升级成更高制作级别的工厂宣传片 -> 使用 `google-veo-cinematic-video`
- 建立可重复运行的外贸短视频内容系统 -> 进入 `short-video-campaign-orchestrator`
