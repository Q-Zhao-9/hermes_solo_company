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
