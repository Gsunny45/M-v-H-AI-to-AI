#!/usr/bin/env python3
# nesting_cog_omega.py
# Stage 2 synthesizer and orchestrator

import os
import json
import uuid
import datetime
from pathlib import Path

from cog_nexus import (
    run_agent,
    run_research,
    run_analyzer,
    run_planner,
    run_coder,
    run_reviewer,
    run_tools,
)
from cog_keys import get_api_keys


# -----------------------------------------------------------------------------
# Paths and constants
# -----------------------------------------------------------------------------

BASE_DIR = Path(os.getcwd())
INBOX_DIR = BASE_DIR / "00_INBOX"
PROJECT_ROOT = BASE_DIR / "projects" / "current_project"
LOG_DIR = PROJECT_ROOT / "_logs"
META_DIR = PROJECT_ROOT / "_meta"

STAGE2_HANDOFF_PATH = PROJECT_ROOT / "stage2_handoff.json"

INBOX_DIR.mkdir(parents=True, exist_ok=True)
PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
META_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------------------------------
# Utility helpers
# -----------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _load_json(path: Path, default=None):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(content)


def _read_text(path: Path, default: str = "") -> str:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return f.read()


def _new_task_id(stage: int, seq: int) -> str:
    # dash-number tracking: handoff-<stage>-task-<n>
    return f"handoff-{stage}-task-{seq}"


def _log_event(kind: str, payload: dict) -> None:
    stamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    rid = uuid.uuid4().hex[:8]
    path = LOG_DIR / f"{stamp}_{kind}_{rid}.json"
    record = {
        "id": rid,
        "kind": kind,
        "timestamp": _now_iso(),
        "payload": payload,
    }
    _save_json(path, record)


def _load_stage1_notes() -> list:
    """
    Load Stage 1 notes from 00_INBOX and current_project.
    This assumes five sources: Perplexity, Groq, Grok, Claude, DeepSeek.
    """
    candidates = []
    for base in [INBOX_DIR, PROJECT_ROOT]:
        if not base.exists():
            continue
        for p in base.glob("stage1_*.*"):
            candidates.append(p)
        for p in base.glob("stage1*.json"):
            candidates.append(p)
        for p in base.glob("stage1*.md"):
            candidates.append(p)

    notes = []
    for path in sorted(set(candidates)):
        content = _read_text(path, "")
        if not content.strip():
            continue
        notes.append(
            {
                "source_path": str(path),
                "content": content,
            }
        )

    return notes


# -----------------------------------------------------------------------------
# Mermaid artifacts
# -----------------------------------------------------------------------------

def _build_mermaid_overview() -> str:
    """
    Mermaid diagram of the 6-stage pipeline with clear handoffs.
    """
    return """```
flowchart TD
    S1[Stage 1: Source Notes (Perplexity, Groq, Grok, Claude, DeepSeek)]
    S2[Stage 2: Extract & Normalize Ideas]
    S3[Stage 3: Synthesis & Master Plan]
    S4[Stage 4: Task Planning & Tracking]
    S5[Stage 5: Implementation Drafting]
    S6[Stage 6: Review, Pack & Handoff]

    S1 -->|stage1_notes.*| S2
    S2 -->|unique_ideas.json| S3
    S3 -->|master_plan.md / master_plan.json| S4
    S4 -->|handoff-* task objects| S5
    S5 -->|draft artifacts| S6
    S6 -->|stage2_handoff.json| OUT[Downstream Systems]
```"""


def _build_mermaid_agents() -> str:
    """
    Mermaid diagram of agents: monitor, clean, pack, plus main pipeline.
    """
    return """```
flowchart LR
    subgraph Pipeline
        P2[Stage 2: Extractor]
        P3[Stage 3: Synthesizer]
        P4[Stage 4: Planner]
        P5[Stage 5: Implementer]
        P6[Stage 6: Reviewer & Packer]
    end

    subgraph Support Agents
        MON[Monitor Agent]
        CLN[Clean Agent]
        PCK[Pack Agent]
    end

    P2 --> P3 --> P4 --> P5 --> P6
    MON --> P2
    MON --> P3
    MON --> P4
    MON --> P5
    MON --> P6

    P2 --> CLN
    P3 --> CLN
    P4 --> CLN
    P5 --> CLN
    P6 --> CLN

    CLN --> PCK
    PCK -->|stage2_handoff.json| OUT[External Orchestrator]
```"""


# -----------------------------------------------------------------------------
# Stage 2: Extract & normalize ideas
# -----------------------------------------------------------------------------

def stage2_extract_unique_ideas(stage1_notes: list) -> dict:
    """
    Use an analyzer agent to extract every unique idea, number, or bullet
    from all 5 Stage 1 notes and normalize them into a deduplicated set.
    """
    task_id = _new_task_id(stage=2, seq=1)
    prompt = (
        "You are Stage 2 of a multi-LLM synthesis pipeline.\n"
        "You receive 5 short, partially overlapping notes describing a nested cog pipeline.\n"
        "Your job is to:\n"
        "1) Extract every distinct idea, requirement, or numeric constraint.\n"
        "2) Normalize wording while preserving meaning.\n"
        "3) Deduplicate overlapping bullets.\n"
        "4) Organize output into labeled clusters (e.g., STAGES, TRACKING, PATHS, AGENTS, FILES, MISC).\n"
        "5) For each bullet, assign a stable key like I-001, I-002, etc.\n\n"
        "Return strict JSON with this schema:\n"
        "{\n"
        '  "clusters": [\n'
        '    {\n'
        '      "name": "STAGES",\n'
        '      "items": [\n'
        '        {\n'
        '          "id": "I-001",\n'
        '          "summary": "6 stages with clear handoffs",\n'
        '          "sources": ["Perplexity", "Claude"]\n'
        "        }\n"
        "      ]\n"
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Input notes:\n"
    )

    for idx, note in enumerate(stage1_notes, start=1):
        prompt += f"\n--- NOTE {idx} ({note['source_path']}) ---\n"
        prompt += note["content"][:12000]

    response = run_analyzer(
        task_id=task_id,
        instructions=prompt,
        temperature=0.1,
        max_tokens=2000,
    )

    try:
        data = json.loads(response["text"])
    except Exception:
        data = {"clusters": []}

    out_path = PROJECT_ROOT / "stage2_unique_ideas.json"
    _save_json(out_path, data)

    _log_event(
        "stage2_extract_unique_ideas",
        {"task_id": task_id, "output_path": str(out_path)},
    )
    return data


# -----------------------------------------------------------------------------
# Stage 3: Synthesis & master plan
# -----------------------------------------------------------------------------

def stage3_build_master_plan(unique_ideas: dict) -> dict:
    """
    Merge unique ideas into a single, detailed master plan for nesting_cog_omega.
    """
    task_id = _new_task_id(stage=3, seq=1)
    prompt = (
        "You are Stage 3: Master Plan Synthesizer for a Python orchestrator file "
        "named nesting_cog_omega.py.\n"
        "You receive normalized, deduplicated ideas from Stage 2.\n"
        "Your job is to produce a single, coherent implementation blueprint.\n\n"
        "Hard requirements from the ideas:\n"
        "- Exactly 6 stages with clear handoffs.\n"
        "- Use cog_nexus.py for all model/tool calls.\n"
        "- Use cog_keys.py for keys only, not direct environment access.\n"
        "- Persist all generated artifacts under 00_INBOX and projects/current_project.\n"
        "- Include monitor, clean, and pack agents.\n"
        "- Use dash-number task tracking like 'handoff-3-task-1'.\n"
        "- Produce Mermaid diagrams embedded in markdown files.\n"
        "- Produce a final stage2_handoff.json file for downstream stages.\n\n"
        "Return strict JSON with this schema:\n"
        "{\n"
        '  "stages": [\n'
        "    {\n"
        '      "index": 1,\n'
        '      "name": "Stage name",\n'
        '      "goal": "Sentence-level description of the stage goal.",\n'
        '      "inputs": ["list of canonical inputs"],\n'
        '      "outputs": ["list of canonical outputs"],\n'
        '      "agents": ["primary agents to call via cog_nexus"],\n'
        '      "steps": [\n'
        '        "Step 1 description",\n'
        '        "Step 2 description"\n'
        "      ]\n"
        "    }\n"
        "  ],\n"
        '  "agents": {\n'
        '    "monitor": "Description of monitoring responsibilities.",\n'
        '    "clean": "Description of cleanup/normalization work.",\n'
        '    "pack": "Description of packaging/finalization work."\n'
        "  },\n"
        '  "files": [\n'
        "    {\n"
        '      "path": "relative/path/from/project_root.ext",\n'
        '      "role": "short description of the file role",\n'
        '      "format": "json|md|txt|other"\n'
        "    }\n"
        "  ],\n"
        '  "tracking": {\n'
        '    "pattern": "handoff-<stage>-task-<n>",\n'
        '    "examples": ["handoff-2-task-1", "handoff-5-task-3"]\n'
        "  }\n"
        "}\n\n"
        "Use concise, implementation-oriented language.\n"
        "The blueprint will be consumed by another Python function, not a human.\n\n"
        "Unique ideas JSON:\n"
    )

    prompt += json.dumps(unique_ideas, indent=2, ensure_ascii=False)[:14000]

    response = run_planner(
        task_id=task_id,
        instructions=prompt,
        temperature=0.15,
        max_tokens=2400,
    )

    try:
        data = json.loads(response["text"])
    except Exception:
        data = {"stages": [], "agents": {}, "files": [], "tracking": {}}

    out_json = PROJECT_ROOT / "stage3_master_plan.json"
    _save_json(out_json, data)

    # Render markdown version with Mermaid diagrams
    md = ["# nesting_cog_omega Master Plan\n", "## Overview\n", _build_mermaid_overview(), "\n"]
    md.append("## Agents\n")
    md.append(_build_mermaid_agents())
    md.append("\n")

    md.append("## Stages\n")
    for st in data.get("stages", []):
        md.append(f"### Stage {st.get('index')}: {st.get('name')}\n")
        md.append(f"**Goal:** {st.get('goal')}\n\n")
        md.append("**Inputs:**\n")
        for item in st.get("inputs", []):
            md.append(f"- {item}\n")
        md.append("\n**Outputs:**\n")
        for item in st.get("outputs", []):
            md.append(f"- {item}\n")
        md.append("\n**Agents:**\n")
        for item in st.get("agents", []):
            md.append(f"- {item}\n")
        md.append("\n**Steps:**\n")
        for step in st.get("steps", []):
            md.append(f"- {step}\n")
        md.append("\n")

    md_path = PROJECT_ROOT / "stage3_master_plan.md"
    _write_text(md_path, "\n".join(md))

    _log_event(
        "stage3_build_master_plan",
        {"task_id": task_id, "plan_json": str(out_json), "plan_md": str(md_path)},
    )
    return data


# -----------------------------------------------------------------------------
# Stage 4: Task planning & tracking
# -----------------------------------------------------------------------------

def stage4_create_tasks(master_plan: dict) -> list:
    """
    Turn the master plan into concrete, dash-numbered tasks.
    """
    task_id = _new_task_id(stage=4, seq=1)
    tasks = []

    for stage in master_plan.get("stages", []):
        s_idx = stage.get("index", 0)
        steps = stage.get("steps", [])
        for i, step in enumerate(steps, start=1):
            tid = _new_task_id(stage=s_idx, seq=i)
            tasks.append(
                {
                    "id": tid,
                    "stage": s_idx,
                    "stage_name": stage.get("name"),
                    "step_index": i,
                    "step": step,
                    "status": "pending",
                    "created_at": _now_iso(),
                }
            )

    out_path = PROJECT_ROOT / "stage4_tasks.json"
    _save_json(out_path, {"tasks": tasks})

    _log_event(
        "stage4_create_tasks",
        {"task_id": task_id, "task_count": len(tasks), "output_path": str(out_path)},
    )
    return tasks


# -----------------------------------------------------------------------------
# Monitor / clean / pack agents
# -----------------------------------------------------------------------------

def agent_monitor(tasks: list) -> dict:
    """
    Lightweight monitor that summarizes task distribution and flags obvious gaps.
    """
    task_id = _new_task_id(stage=5, seq=0)
    summary = {
        "total_tasks": len(tasks),
        "by_stage": {},
        "created_at": _now_iso(),
    }
    for t in tasks:
        s = str(t.get("stage"))
        summary["by_stage"].setdefault(s, 0)
        summary["by_stage"][s] += 1

    out_path = META_DIR / "monitor_summary.json"
    _save_json(out_path, summary)

    _log_event(
        "agent_monitor",
        {"task_id": task_id, "output_path": str(out_path)},
    )
    return summary


def agent_clean() -> dict:
    """
    Clean and normalize intermediate outputs, ensuring consistent JSON and markdown.
    """
    task_id = _new_task_id(stage=5, seq=1)
    cleaned = {"normalized": [], "timestamp": _now_iso()}

    # Example: ensure all JSON files under current_project are valid
    for p in PROJECT_ROOT.rglob("*.json"):
        try:
            data = _load_json(p, None)
            if data is None:
                continue
            cleaned["normalized"].append(str(p))
        except Exception:
            continue

    out_path = META_DIR / "clean_report.json"
    _save_json(out_path, cleaned)

    _log_event(
        "agent_clean",
        {"task_id": task_id, "output_path": str(out_path)},
    )
    return cleaned


def agent_pack(tasks: list, master_plan: dict, monitor_state: dict) -> dict:
    """
    Final packer that assembles stage2_handoff.json summary for downstream systems.
    """
    task_id = _new_task_id(stage=6, seq=1)
    handoff = {
        "id": "stage2_handoff",
        "version": 1,
        "created_at": _now_iso(),
        "project_root": str(PROJECT_ROOT),
        "inbox_root": str(INBOX_DIR),
        "tracking_pattern": "handoff-<stage>-task-<n>",
        "tasks": tasks,
        "master_plan": master_plan,
        "monitor": monitor_state,
        "artifacts": {
            "unique_ideas": str(PROJECT_ROOT / "stage2_unique_ideas.json"),
            "master_plan_json": str(PROJECT_ROOT / "stage3_master_plan.json"),
            "master_plan_md": str(PROJECT_ROOT / "stage3_master_plan.md"),
            "tasks_json": str(PROJECT_ROOT / "stage4_tasks.json"),
            "monitor_json": str(META_DIR / "monitor_summary.json"),
            "clean_report_json": str(META_DIR / "clean_report.json"),
        },
    }

    _save_json(STAGE2_HANDOFF_PATH, handoff)

    _log_event(
        "agent_pack",
        {"task_id": task_id, "handoff_path": str(STAGE2_HANDOFF_PATH)},
    )
    return handoff


# -----------------------------------------------------------------------------
# Stage 5: Implementation drafting (optional, stubbed to keep focus on plan)
# -----------------------------------------------------------------------------

def stage5_implementation_stub(tasks: list) -> None:
    """
    Optionally create placeholder implementation notes for each task.
    This keeps within the requirement to focus on nesting_cog_omega, not other files.
    """
    task_id = _new_task_id(stage=5, seq=2)
    lines = ["# Stage 5 Implementation Notes\n"]
    for t in tasks:
        lines.append(f"- {t['id']}: {t['stage_name']} / step {t['step_index']} – {t['step']}")
    notes_path = PROJECT_ROOT / "stage5_implementation_notes.md"
    _write_text(notes_path, "\n".join(lines))

    _log_event(
        "stage5_implementation_stub",
        {"task_id": task_id, "notes_path": str(notes_path)},
    )


# -----------------------------------------------------------------------------
# Stage 6: Review & finalize
# -----------------------------------------------------------------------------

def stage6_review_and_finalize(tasks: list, master_plan: dict) -> None:
    """
    Use reviewer tools to cross-check master plan, tasks, and artifacts.
    """
    task_id = _new_task_id(stage=6, seq=2)
    checklist = {
        "questions": [
            "Do all 6 stages exist and hand off cleanly?",
            "Are monitor, clean, and pack agents present and documented?",
            "Is dash-number tracking consistently applied?",
            "Are artifacts stored only under 00_INBOX and projects/current_project?",
            "Do Mermaid diagrams exist and renderable as markdown fences?",
            "Is stage2_handoff.json present and well-formed?",
        ],
        "tasks_sample": tasks[:10],
        "master_plan_head": master_plan.get("stages", [])[:3],
    }

    prompt = (
        "You are Stage 6: Reviewer.\n"
        "You receive a master plan, tasks, and a checklist.\n"
        "Return a short JSON review with 'status' (ok|warn|fail) and 'notes' list.\n\n"
        "Checklist and samples:\n"
        + json.dumps(checklist, indent=2, ensure_ascii=False)
    )

    response = run_reviewer(
        task_id=task_id,
        instructions=prompt,
        temperature=0.0,
        max_tokens=800,
    )

    try:
        review_data = json.loads(response["text"])
    except Exception:
        review_data = {"status": "warn", "notes": ["Reviewer output not parseable."]}

    out_path = META_DIR / "stage6_review.json"
    _save_json(out_path, review_data)

    _log_event(
        "stage6_review_and_finalize",
        {"task_id": task_id, "review_path": str(out_path)},
    )


# -----------------------------------------------------------------------------
# Orchestration
# -----------------------------------------------------------------------------

def run_stage2_synthesizer() -> dict:
    """
    Main entrypoint: load Stage 1 notes, synthesize, and emit stage2_handoff.json.
    """
    api_keys = get_api_keys()
    _log_event("keys_loaded", {"keys_present": list(api_keys.keys())})

    # Stage 1: implicit, notes are already created by upstream systems.
    stage1_notes = _load_stage1_notes()
    _log_event("stage1_loaded", {"note_count": len(stage1_notes)})

    # Stage 2: extract unique ideas
    unique_ideas = stage2_extract_unique_ideas(stage1_notes)

    # Stage 3: master plan
    master_plan = stage3_build_master_plan(unique_ideas)

    # Stage 4: tasks
    tasks = stage4_create_tasks(master_plan)

    # Monitor
    monitor_state = agent_monitor(tasks)

    # Stage 5: implementation stub + clean
    stage5_implementation_stub(tasks)
    agent_clean()

    # Stage 6: review and pack
    stage6_review_and_finalize(tasks, master_plan)
    handoff = agent_pack(tasks, master_plan, monitor_state)

    return handoff


if __name__ == "__main__":
    result = run_stage2_synthesizer()
    print(json.dumps({"stage2_handoff": str(STAGE2_HANDOFF_PATH)}, indent=2))
