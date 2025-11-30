# Stage 1 Notes: Groq

## Orchestrator Requirements

The nesting_cog_omega.py file must:

1. Import from cog_nexus.py (agent runners)
2. Import from cog_keys.py (credential management)
3. Use Path from pathlib for file operations
4. Create directories: 00_INBOX, projects/current_project, _logs, _meta

## Task Tracking

Every task must have a unique ID in the format: `handoff-<stage>-<task_sequence>`

Examples:
- `handoff-2-task-1` (Stage 2, Task 1)
- `handoff-3-task-2` (Stage 3, Task 2)
- `handoff-6-task-3` (Stage 6, Task 3)

## Logging

All events must be logged to JSON files with:
- Timestamp (ISO 8601 format with Z suffix)
- Event kind (e.g., "stage2_extract_unique_ideas")
- UUID for tracking
- Payload with relevant data

## JSON Output

All intermediate outputs must be valid JSON:
- stage2_unique_ideas.json: Clustered ideas with IDs
- stage3_master_plan.json: Full plan with stages, agents, files
- stage4_tasks.json: List of task objects
- stage2_handoff.json: Final packaging of all artifacts
