# Stage 1 Notes: Perplexity

## Pipeline Architecture Overview

The nesting_cog_omega pipeline is a 6-stage synthesis system designed to:

1. **Stage 1**: Source notes from multiple LLMs (Perplexity, Groq, Grok, Claude, DeepSeek)
2. **Stage 2**: Extract and normalize unique ideas from all sources
3. **Stage 3**: Synthesize a master plan with clear handoffs
4. **Stage 4**: Convert master plan into concrete, tracked tasks
5. **Stage 5**: Implementation drafting for each task
6. **Stage 6**: Review, validation, and final packaging

## Key Requirements

- All 6 stages must have clear input/output handoffs
- Use dash-number task tracking: `handoff-<stage>-task-<n>`
- Artifacts stored only under `00_INBOX` and `projects/current_project`
- Include monitor, clean, and pack support agents
- Produce Mermaid diagrams for visualization
- Final output: `stage2_handoff.json` for downstream systems

## Data Flow

```
Stage 1 Notes (.json/.md files)
    ↓
Stage 2: Extract unique ideas → stage2_unique_ideas.json
    ↓
Stage 3: Build master plan → stage3_master_plan.json + stage3_master_plan.md
    ↓
Stage 4: Create tasks → stage4_tasks.json
    ↓
Stage 5: Implementation notes → stage5_implementation_notes.md
    ↓
Stage 6: Review & Pack → stage2_handoff.json
```

## Agents Required

- **Analyzer**: Extract and deduplicate ideas (Stage 2)
- **Planner**: Synthesize master plan (Stage 3)
- **Monitor**: Track task distribution and gaps
- **Clean**: Normalize JSON/markdown artifacts
- **Pack**: Assemble final handoff payload
