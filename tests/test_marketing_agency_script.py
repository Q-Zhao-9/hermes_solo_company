import json
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "marketing_agency.py"


def run_script(*args: str, check: bool = True) -> dict:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        check=check,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def test_create_strategy_writes_markdown_and_state(tmp_path):
    result = run_script(
        "create-strategy",
        "--brand",
        "Acme LiDAR",
        "--business",
        "LiDAR truck volume measurement systems for industrial logistics.",
        "--audience",
        "mining companies and aggregate producers",
        "--goal",
        "Generate qualified demo requests",
        "--offer",
        "automated truck volume measurement",
        "--tone",
        "technical and executive",
        "--output-dir",
        str(tmp_path),
    )

    project_dir = Path(result["projectDir"])
    strategy = Path(result["strategyPath"]).read_text(encoding="utf-8")
    state = json.loads((project_dir / "docs" / "hermes-marketing-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert "Marketing Strategy: Acme LiDAR" in strategy
    assert "Operational ROI" in strategy
    assert "LinkedIn" in result["strategy"]["channels"]
    assert "YouTube demos" in result["strategy"]["channels"]
    assert state["workflowState"] == "strategy_ready"
    assert state["lastStrategy"]["brand"] == "Acme LiDAR"


def test_create_campaign_uses_strategy_defaults_and_records_history(tmp_path):
    strategy = run_script(
        "create-strategy",
        "--brand",
        "Acme LiDAR",
        "--business",
        "LiDAR truck volume measurement systems for industrial logistics.",
        "--audience",
        "mining companies and aggregate producers",
        "--goal",
        "Generate qualified demo requests",
        "--offer",
        "automated truck volume measurement",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(strategy["projectDir"])

    result = run_script(
        "create-campaign",
        "--project-dir",
        str(project_dir),
        "--name",
        "Reduce Loading Loss",
        "--objective",
        "reduce loading losses by 5%",
        "--duration",
        "6 weeks",
        "--cta",
        "Book a measurement demo",
    )

    campaign = Path(result["campaignPath"]).read_text(encoding="utf-8")
    state = json.loads((project_dir / "docs" / "hermes-marketing-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert "Campaign: Reduce Loading Loss" in campaign
    assert "Operational ROI" in campaign
    assert result["campaign"]["channels"][0] == "LinkedIn"
    assert result["campaign"]["approvalRequired"] is True
    assert state["workflowState"] == "campaign_ready"
    assert state["lastCampaign"]["slug"] == "reduce-loading-loss"


def test_summary_returns_discord_friendly_marketing_status(tmp_path):
    strategy = run_script(
        "create-strategy",
        "--brand",
        "Acme AI",
        "--business",
        "AI workflow automation software for operations teams.",
        "--audience",
        "operations leaders",
        "--goal",
        "Book demos",
        "--offer",
        "workflow automation platform",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(strategy["projectDir"])
    run_script(
        "create-campaign",
        "--project-dir",
        str(project_dir),
        "--name",
        "Ops Automation Launch",
        "--objective",
        "increase demo requests",
    )

    result = run_script("summary", "--project-dir", str(project_dir))

    assert result["ok"] is True
    assert "**Marketing Status: Acme AI**" in result["summary"]
    assert "Latest campaign: `Ops Automation Launch`" in result["summary"]


def test_generate_content_plan_creates_calendar_and_state(tmp_path):
    strategy = run_script(
        "create-strategy",
        "--brand",
        "Acme LiDAR",
        "--business",
        "LiDAR truck volume measurement systems for industrial logistics.",
        "--audience",
        "mining companies and aggregate producers",
        "--goal",
        "Generate qualified demo requests",
        "--offer",
        "automated truck volume measurement",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(strategy["projectDir"])
    run_script(
        "create-campaign",
        "--project-dir",
        str(project_dir),
        "--name",
        "Reduce Loading Loss",
        "--objective",
        "reduce loading losses by 5%",
    )

    result = run_script(
        "generate-content-plan",
        "--project-dir",
        str(project_dir),
        "--weeks",
        "2",
        "--cadence",
        "2",
        "--channels",
        "LinkedIn,YouTube demos",
    )

    calendar = Path(result["planPath"]).read_text(encoding="utf-8")
    state = json.loads((project_dir / "docs" / "hermes-marketing-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert len(result["plan"]["items"]) == 4
    assert result["plan"]["items"][0]["channel"] == "LinkedIn"
    assert result["plan"]["items"][0]["approvalStatus"] == "draft"
    assert "Content Calendar: Reduce Loading Loss" in calendar
    assert state["workflowState"] == "content_plan_ready"
    assert state["lastContentPlan"]["campaignSlug"] == "reduce-loading-loss"


def test_generate_posts_creates_platform_drafts_and_summary_tracks_them(tmp_path):
    strategy = run_script(
        "create-strategy",
        "--brand",
        "Acme LiDAR",
        "--business",
        "LiDAR truck volume measurement systems for industrial logistics.",
        "--audience",
        "mining companies and aggregate producers",
        "--goal",
        "Generate qualified demo requests",
        "--offer",
        "automated truck volume measurement",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(strategy["projectDir"])
    run_script(
        "create-campaign",
        "--project-dir",
        str(project_dir),
        "--name",
        "Reduce Loading Loss",
        "--objective",
        "reduce loading losses by 5%",
        "--cta",
        "Book a measurement demo",
    )

    result = run_script(
        "generate-posts",
        "--project-dir",
        str(project_dir),
        "--channels",
        "LinkedIn,X,SEO blog,Email",
        "--count",
        "1",
        "--stage",
        "consideration",
    )
    summary = run_script("summary", "--project-dir", str(project_dir))

    drafts_md = Path(result["draftPath"]).read_text(encoding="utf-8")
    state = json.loads((project_dir / "docs" / "hermes-marketing-state.json").read_text(encoding="utf-8"))
    channels = [draft["channel"] for draft in result["drafts"]["drafts"]]
    assert result["ok"] is True
    assert channels == ["LinkedIn", "X", "SEO blog", "Email"]
    assert "CTA: Book a measurement demo" in drafts_md
    assert "SEO Title:" in drafts_md
    assert state["workflowState"] == "content_drafts_ready"
    assert state["lastContentDrafts"]["approvalRequired"] is True
    assert "Content drafts: `4` ready for review" in summary["summary"]


def test_generate_seo_plan_creates_keyword_page_and_schema_plan(tmp_path):
    strategy = run_script(
        "create-strategy",
        "--brand",
        "Acme LiDAR",
        "--business",
        "LiDAR truck volume measurement systems for industrial logistics.",
        "--audience",
        "mining companies and aggregate producers",
        "--goal",
        "Generate qualified demo requests",
        "--offer",
        "automated truck volume measurement",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(strategy["projectDir"])
    run_script(
        "create-campaign",
        "--project-dir",
        str(project_dir),
        "--name",
        "Reduce Loading Loss",
        "--objective",
        "reduce loading losses by 5%",
    )

    result = run_script(
        "generate-seo-plan",
        "--project-dir",
        str(project_dir),
        "--focus",
        "truck volume measurement",
        "--pages",
        "4",
        "--region",
        "North America",
    )

    markdown = Path(result["seoPlanPath"]).read_text(encoding="utf-8")
    state = json.loads((project_dir / "docs" / "hermes-marketing-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert len(result["seoPlan"]["keywordClusters"]) >= 4
    assert len(result["seoPlan"]["pagePlan"]) == 4
    assert "FAQPage" in result["seoPlan"]["schemaRecommendations"]
    assert "AI Answer Engine Recommendations" in markdown
    assert state["workflowState"] == "seo_plan_ready"
    assert state["lastSeoPlan"]["region"] == "North America"


def test_generate_blog_briefs_uses_seo_plan_and_summary_tracks_them(tmp_path):
    strategy = run_script(
        "create-strategy",
        "--brand",
        "Acme AI",
        "--business",
        "AI workflow automation software for operations teams.",
        "--audience",
        "operations leaders",
        "--goal",
        "Book demos",
        "--offer",
        "workflow automation platform",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(strategy["projectDir"])
    run_script("generate-seo-plan", "--project-dir", str(project_dir), "--pages", "3")

    result = run_script(
        "generate-blog-briefs",
        "--project-dir",
        str(project_dir),
        "--count",
        "3",
        "--intent",
        "comparison",
    )
    summary = run_script("summary", "--project-dir", str(project_dir))

    markdown = Path(result["blogBriefsPath"]).read_text(encoding="utf-8")
    state = json.loads((project_dir / "docs" / "hermes-marketing-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert len(result["blogBriefs"]["briefs"]) == 3
    assert result["blogBriefs"]["briefs"][0]["intent"] == "comparison"
    assert "How to Compare" in result["blogBriefs"]["briefs"][0]["title"]
    assert "AI Answer Summary" in markdown
    assert state["workflowState"] == "blog_briefs_ready"
    assert state["lastBlogBriefs"]["approvalRequired"] is True
    assert "SEO/GEO plan: `" in summary["summary"]
    assert "Blog briefs: `3` ready for review" in summary["summary"]


def test_define_lead_signals_creates_signal_files_and_state(tmp_path):
    strategy = run_script(
        "create-strategy",
        "--brand",
        "Acme LiDAR",
        "--business",
        "LiDAR truck volume measurement systems for industrial logistics.",
        "--audience",
        "mining companies and aggregate producers",
        "--goal",
        "Generate qualified demo requests",
        "--offer",
        "automated truck volume measurement",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(strategy["projectDir"])

    result = run_script(
        "define-lead-signals",
        "--project-dir",
        str(project_dir),
        "--channels",
        "LinkedIn,Reddit,Industry forums",
        "--signals",
        "asking for truck scale alternatives,looking for volume measurement",
        "--negative-signals",
        "student research,free only",
    )

    markdown = Path(result["leadSignalsPath"]).read_text(encoding="utf-8")
    state = json.loads((project_dir / "docs" / "hermes-marketing-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert "Lead Signals: Acme LiDAR" in markdown
    assert "looking for volume measurement" in result["leadSignals"]["positiveSignals"]
    assert result["leadSignals"]["channels"] == ["LinkedIn", "Reddit", "Industry forums"]
    assert Path(result["leadSignalsJsonPath"]).exists()
    assert state["workflowState"] == "lead_signals_ready"
    assert state["lastLeadSignals"]["approvalRequired"] is True


def test_score_lead_creates_scorecard_and_summary_tracks_it(tmp_path):
    strategy = run_script(
        "create-strategy",
        "--brand",
        "Acme LiDAR",
        "--business",
        "LiDAR truck volume measurement systems for industrial logistics.",
        "--audience",
        "mining companies and aggregate producers",
        "--goal",
        "Generate qualified demo requests",
        "--offer",
        "automated truck volume measurement",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(strategy["projectDir"])
    run_script("define-lead-signals", "--project-dir", str(project_dir))

    result = run_script(
        "score-lead",
        "--project-dir",
        str(project_dir),
        "--name",
        "Jordan",
        "--company",
        "North Ridge Aggregates",
        "--role",
        "Operations Manager",
        "--source",
        "LinkedIn",
        "--channel",
        "LinkedIn",
        "--text",
        "We are looking for truck volume measurement to reduce loading losses at our aggregate sites.",
    )
    summary = run_script("summary", "--project-dir", str(project_dir))

    markdown = Path(result["scorecardsPath"]).read_text(encoding="utf-8")
    state = json.loads((project_dir / "docs" / "hermes-marketing-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert result["scorecard"]["score"] > 0
    assert result["scorecard"]["grade"] in {"hot", "warm"}
    assert "North Ridge Aggregates" in markdown
    assert "reduce loading losses" in markdown
    assert state["workflowState"] == "lead_scored"
    assert state["lastLeadScorecard"]["company"] == "North Ridge Aggregates"
    assert "Latest lead: `" in summary["summary"]


def test_draft_outreach_and_crm_export_create_review_ready_assets(tmp_path):
    strategy = run_script(
        "create-strategy",
        "--brand",
        "Acme LiDAR",
        "--business",
        "LiDAR truck volume measurement systems for industrial logistics.",
        "--audience",
        "mining companies and aggregate producers",
        "--goal",
        "Generate qualified demo requests",
        "--offer",
        "automated truck volume measurement",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(strategy["projectDir"])
    run_script(
        "create-campaign",
        "--project-dir",
        str(project_dir),
        "--name",
        "Reduce Loading Loss",
        "--objective",
        "reduce loading losses by 5%",
        "--cta",
        "Book a measurement demo",
    )
    run_script("define-lead-signals", "--project-dir", str(project_dir))
    score = run_script(
        "score-lead",
        "--project-dir",
        str(project_dir),
        "--name",
        "Jordan",
        "--company",
        "North Ridge Aggregates",
        "--source",
        "LinkedIn",
        "--text",
        "We need a solution to replace manual measurement and improve truck loading accuracy.",
    )

    outreach = run_script(
        "draft-outreach",
        "--project-dir",
        str(project_dir),
        "--lead-id",
        score["scorecard"]["id"],
        "--channel",
        "email",
    )
    crm = run_script("crm-export", "--project-dir", str(project_dir), "--format", "csv", "--owner", "sales")

    outreach_md = Path(outreach["outreachDraftsPath"]).read_text(encoding="utf-8")
    crm_csv = Path(crm["crmExportPath"]).read_text(encoding="utf-8")
    state = json.loads((project_dir / "docs" / "hermes-marketing-state.json").read_text(encoding="utf-8"))
    assert outreach["ok"] is True
    assert outreach["outreachDraft"]["approvalRequired"] is True
    assert "Approval: required before sending" in outreach_md
    assert "Book a measurement demo" in outreach_md
    assert crm["ok"] is True
    assert "lead_id,name,company" in crm_csv
    assert "North Ridge Aggregates" in crm_csv
    assert state["workflowState"] == "crm_export_ready"
    assert state["lastCrmExport"]["leadCount"] == 1


def test_record_performance_creates_snapshot_and_summary_tracks_it(tmp_path):
    strategy = run_script(
        "create-strategy",
        "--brand",
        "Acme LiDAR",
        "--business",
        "LiDAR truck volume measurement systems for industrial logistics.",
        "--audience",
        "mining companies and aggregate producers",
        "--goal",
        "Generate qualified demo requests",
        "--offer",
        "automated truck volume measurement",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(strategy["projectDir"])
    run_script(
        "create-campaign",
        "--project-dir",
        str(project_dir),
        "--name",
        "Reduce Loading Loss",
        "--objective",
        "reduce loading losses by 5%",
    )

    result = run_script(
        "record-performance",
        "--project-dir",
        str(project_dir),
        "--channel",
        "LinkedIn",
        "--period",
        "2026-W20",
        "--metrics",
        "impressions=1000,engagements=80,clicks=35,leads=4,conversions=1,spend=120,revenue=600",
        "--notes",
        "ROI post outperformed technical post.",
    )
    summary = run_script("summary", "--project-dir", str(project_dir))

    markdown = Path(result["performanceSnapshotsPath"]).read_text(encoding="utf-8")
    state = json.loads((project_dir / "docs" / "hermes-marketing-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert result["performanceSnapshot"]["derivedMetrics"]["ctr"] == 0.035
    assert result["performanceSnapshot"]["derivedMetrics"]["leadRate"] == 0.1143
    assert "Performance Snapshots" in markdown
    assert "ROI post outperformed technical post." in markdown
    assert state["workflowState"] == "performance_snapshot_ready"
    assert "Latest performance: CTR `3.5%`" in summary["summary"]


def test_generate_review_dashboard_aggregates_assets_leads_and_performance(tmp_path):
    strategy = run_script(
        "create-strategy",
        "--brand",
        "Acme LiDAR",
        "--business",
        "LiDAR truck volume measurement systems for industrial logistics.",
        "--audience",
        "mining companies and aggregate producers",
        "--goal",
        "Generate qualified demo requests",
        "--offer",
        "automated truck volume measurement",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(strategy["projectDir"])
    run_script(
        "create-campaign",
        "--project-dir",
        str(project_dir),
        "--name",
        "Reduce Loading Loss",
        "--objective",
        "reduce loading losses by 5%",
        "--cta",
        "Book a measurement demo",
    )
    run_script("generate-posts", "--project-dir", str(project_dir), "--channels", "LinkedIn,Email")
    run_script("generate-blog-briefs", "--project-dir", str(project_dir), "--count", "2")
    run_script("define-lead-signals", "--project-dir", str(project_dir))
    run_script(
        "score-lead",
        "--project-dir",
        str(project_dir),
        "--name",
        "Jordan",
        "--company",
        "North Ridge Aggregates",
        "--text",
        "We are looking for truck volume measurement to reduce loading losses.",
    )
    run_script(
        "record-performance",
        "--project-dir",
        str(project_dir),
        "--channel",
        "LinkedIn",
        "--metrics",
        "impressions=2000,engagements=120,clicks=50,leads=5,conversions=1,spend=200,revenue=1000",
    )

    result = run_script(
        "generate-review-dashboard",
        "--project-dir",
        str(project_dir),
        "--focus",
        "weekly executive review",
        "--period",
        "2026-W20",
    )

    markdown = Path(result["reviewDashboardPath"]).read_text(encoding="utf-8")
    state = json.loads((project_dir / "docs" / "hermes-marketing-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert result["reviewDashboard"]["artifactCounts"]["contentDrafts"] == 2
    assert result["reviewDashboard"]["artifactCounts"]["blogBriefs"] == 2
    assert result["reviewDashboard"]["leadFunnel"]["total"] == 1
    assert result["reviewDashboard"]["performanceTotals"]["totals"]["clicks"] == 50
    assert "Manager Review Dashboard: Acme LiDAR" in markdown
    assert "Optimization Recommendations" in markdown
    assert state["workflowState"] == "review_dashboard_ready"


def test_add_competitor_creates_profile_files_and_state(tmp_path):
    strategy = run_script(
        "create-strategy",
        "--brand",
        "Acme LiDAR",
        "--business",
        "LiDAR truck volume measurement systems for industrial logistics.",
        "--audience",
        "mining companies and aggregate producers",
        "--goal",
        "Generate qualified demo requests",
        "--offer",
        "automated truck volume measurement",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(strategy["projectDir"])

    result = run_script(
        "add-competitor",
        "--project-dir",
        str(project_dir),
        "--name",
        "MeasureMax",
        "--url",
        "https://example.com",
        "--positioning",
        "Fast truck scale analytics for aggregate operators",
        "--strengths",
        "strong demo videos,known in aggregates",
        "--weaknesses",
        "unclear ROI proof,limited AI answer content",
        "--channels",
        "LinkedIn,SEO blog,YouTube",
    )

    markdown = Path(result["competitorProfilesPath"]).read_text(encoding="utf-8")
    state = json.loads((project_dir / "docs" / "hermes-marketing-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert result["competitor"]["id"] == "measuremax"
    assert "Competitor Profiles" in markdown
    assert "Fast truck scale analytics" in markdown
    assert Path(result["competitorProfilesJsonPath"]).exists()
    assert state["workflowState"] == "competitor_profile_ready"
    assert state["lastCompetitor"]["name"] == "MeasureMax"


def test_track_competitor_creates_observation_and_report_tracks_summary(tmp_path):
    strategy = run_script(
        "create-strategy",
        "--brand",
        "Acme LiDAR",
        "--business",
        "LiDAR truck volume measurement systems for industrial logistics.",
        "--audience",
        "mining companies and aggregate producers",
        "--goal",
        "Generate qualified demo requests",
        "--offer",
        "automated truck volume measurement",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(strategy["projectDir"])
    run_script(
        "add-competitor",
        "--project-dir",
        str(project_dir),
        "--name",
        "MeasureMax",
        "--positioning",
        "Truck measurement dashboards for aggregates",
        "--strengths",
        "customer proof,YouTube demos",
        "--weaknesses",
        "limited workflow ROI content",
    )

    observation = run_script(
        "track-competitor",
        "--project-dir",
        str(project_dir),
        "--competitor",
        "measuremax",
        "--event-type",
        "case study",
        "--channel",
        "LinkedIn",
        "--summary",
        "Published a new quarry case study emphasizing loading accuracy.",
        "--impact",
        "high",
        "--tags",
        "case study,accuracy,aggregates",
    )
    report = run_script(
        "competitor-report",
        "--project-dir",
        str(project_dir),
        "--focus",
        "weekly competitor watch",
        "--period",
        "2026-W20",
    )
    summary = run_script("summary", "--project-dir", str(project_dir))

    observations_md = Path(observation["competitorObservationsPath"]).read_text(encoding="utf-8")
    report_md = Path(report["competitorReportPath"]).read_text(encoding="utf-8")
    state = json.loads((project_dir / "docs" / "hermes-marketing-state.json").read_text(encoding="utf-8"))
    assert observation["ok"] is True
    assert "Published a new quarry case study" in observations_md
    assert "Prepare a proof-led response asset" in observations_md
    assert report["ok"] is True
    assert report["competitorReport"]["competitorCount"] == 1
    assert report["competitorReport"]["observationCount"] == 1
    assert report["competitorReport"]["marketTrends"][0]["topic"] == "accuracy"
    assert "Competitor Intelligence Report: Acme LiDAR" in report_md
    assert "Competitive Proof Response" in report_md
    assert state["workflowState"] == "competitor_report_ready"
    assert "Competitor report: `1` competitors, `1` observations" in summary["summary"]
