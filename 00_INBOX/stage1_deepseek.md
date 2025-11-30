# Stage 1 Notes: DeepSeek

## Stage 5: Implementation Drafting

**Input**: stage4_tasks.json

**Process**:
- Create placeholder implementation notes for each task
- Reference task ID, stage name, step index, step description
- Organize by stage and sequence
- Output markdown file with all tasks listed

**Output**: stage5_implementation_notes.md

## Stage 6: Review & Finalize

**Input**: stage4_tasks.json, stage3_master_plan.json

**Process**:
- Use reviewer agent with zero temperature (0.0) for deterministic output
- Check: all 6 stages present?
- Check: monitor/clean/pack agents documented?
- Check: dash-number tracking consistent?
- Check: artifacts only in 00_INBOX and projects/current_project?
- Check: Mermaid diagrams renderable?
- Check: stage2_handoff.json well-formed?
- Return JSON review with status (ok|warn|fail) and notes

**Output**: stage6_review.json

## Final Packaging

**Input**: All artifacts from stages 2-6 + monitor/clean reports

**Process** (agent_pack):
- Assemble stage2_handoff.json with:
  - All tasks
  - Master plan
  - Monitor summary
  - Paths to all artifacts
  - Version and timestamp
- Save to projects/current_project/stage2_handoff.json

**Output**: stage2_handoff.json (final handoff to downstream systems)
