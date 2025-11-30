# Stage 1 Notes: Claude

## Stage 2: Extract & Normalize Ideas

**Input**: 5 stage1_*.* files (notes from Perplexity, Groq, Grok, Claude, DeepSeek)

**Process**:
- Load all notes from 00_INBOX and projects/current_project
- Use analyzer agent with low temperature (0.1) for precision
- Extract each unique idea and assign stable ID (I-001, I-002, etc.)
- Organize into clusters: STAGES, TRACKING, PATHS, AGENTS, FILES, MISC
- Return strict JSON with clustered items

**Output**: stage2_unique_ideas.json

## Stage 3: Synthesis & Master Plan

**Input**: stage2_unique_ideas.json

**Process**:
- Use planner agent to synthesize coherent blueprint
- Ensure all 6 stages are present with clear goals, inputs, outputs
- Include monitor, clean, pack agents
- Generate markdown with embedded Mermaid diagrams
- Return JSON schema with stages, agents, files, tracking

**Output**: 
- stage3_master_plan.json
- stage3_master_plan.md (with Mermaid diagrams)

## Stage 4: Task Planning & Tracking

**Input**: stage3_master_plan.json

**Process**:
- Iterate through stages and steps
- Create dash-numbered task ID for each step
- Set status to "pending"
- Collect all tasks in array

**Output**: stage4_tasks.json
