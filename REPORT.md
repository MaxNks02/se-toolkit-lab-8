## Task 1A — Bare agent:
🐈 nanobot
I do not have access to the LMS database or tools to check which labs are available. You would need to check the LMS da>

## Task 1B — Agent with LMS tools:
🐈 nanobot
Here are the 8 available labs in the LMS:

 • Lab 01 – Products, Architecture & Roles
 • Lab 02 — Run, Fix, and Deploy a Backend Service
 • Lab 03 — Backend API: Explore, Debug, Implement, Deploy
 • Lab 04 — Testing, Front-end, and AI Agents
 • Lab 05 — Data Pipeline and Analytics Dashboard
 • Lab 06 — Build Your Own Agent
 • Lab 07 — Build a Client with an AI Coding Agent
 • lab-08

Let me know if you'd like stats, pass rates, or completion info for any specific lab!

## Task 1C — Skill prompt:
📊 Lab 01 – Products, Architecture & Roles

 Task                                        Avg Score  Attempts
 ───────────────────────────────────────────────────────────────
 Lab setup                                   97.2%      119
 Task 0: Practice the Git workflow           65.2%      214
 Task 1: Product & architecture description  59.4%      90
 Task 2: Roles and skills mapping            53.9%      42
 Optional: Resolve a merge conflict          41.7%      6
 Optional: Create a release                  50.0%      2
 Optional: Add a CI check                    25.0%      4
 Optional: Plan skill development            0.0%       1

Completion rate: 93.9% (108 passed / 115 total)

Labs 02–08
All other labs show 0 submissions — no learners have attempted them yet.

It looks like only Lab 01 has active data so far. Would you like a deeper dive into any specific lab's stats (timeline,
group performance, top learners)?

## Task 2A — Deployed agent

Nanobot gateway started successfully as a Docker service:

```
Using config: /app/nanobot/config.resolved.json
🐈 Starting nanobot gateway version 0.1.4.post5 on port 18790...
2026-04-06 14:12:50.054 | INFO  | WebChat channel enabled
✓ Channels enabled: webchat
✓ Heartbeat: every 1800s
2026-04-06 14:12:50.081 | INFO  | Cron service started with 0 jobs
2026-04-06 14:12:50.081 | INFO  | Heartbeat started (every 1800s)
2026-04-06 14:12:52.249 | INFO  | Starting webchat channel...
2026-04-06 14:12:53.216 | INFO  | MCP server 'lms': connected, 9 tools registered
2026-04-06 14:12:53.216 | INFO  | Agent loop started
```

## Task 2B — Web client

WebSocket test:

```
$ echo '{"content":"What labs are available?"}' | websocat "ws://localhost:42002/ws/chat?access_key=..."

Response: Here are the available labs:
1. Lab 01 – Products, Architecture & Roles
2. Lab 02 — Run, Fix, and Deploy a Backend Service
3. Lab 03 — Backend API: Explore, Debug, Implement, Deploy
4. Lab 04 — Testing, Front-end, and AI Agents
5. Lab 05 — Data Pipeline and Analytics Dashboard
6. Lab 06 — Build Your Own Agent
7. Lab 07 — Build a Client with an AI Coding Agent
8. Lab 08 — lab-08
```

Flutter web client conversation at http://<vm-ip>:42002/flutter:

User: What can you do in this system?
Agent: I'm nanobot, your personal AI assistant. I can:
- Read, write, and edit files
- Search the web
- Create scheduling/reminders via cron
- LMS: list labs, check pass rates, completion rates, timelines, top learners, trigger sync
- Store and recall facts (memory)
- Manage skills and spawn subagents

User: What labs are available?
Agent: There are 8 labs:
1. Lab 01 – Products, Architecture & Roles
2. Lab 02 — Run, Fix, and Deploy a Backend Service
3. Lab 03 — Backend API: Explore, Debug, Implement, Deploy
4. Lab 04 — Testing, Front-end, and AI Agents
5. Lab 05 — Data Pipeline and Analytics Dashboard
6. Lab 06 — Build Your Own Agent
7. Lab 07 — Build a Client with an AI Coding Agent
8. Lab 08 — lab-08
