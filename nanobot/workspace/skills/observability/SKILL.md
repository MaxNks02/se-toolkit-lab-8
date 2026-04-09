# Observability Strategy

You have access to observability tools that query VictoriaLogs (structured logs) and VictoriaTraces (distributed traces).

## Available tools

- `logs_search` — search logs with LogsQL. Examples: `severity:ERROR`, `db_query AND severity:ERROR`, `*` for all.
- `logs_error_count` — count errors per service in a time window. Use this first when asked about recent errors.
- `traces_list` — list recent traces for a service, showing duration and error status.
- `traces_get` — fetch full span details for a trace ID.

## When to use

- **"Any errors?"** or **"Check system health"** — start with `logs_error_count` for a quick summary. If errors exist, use `logs_search` with `severity:ERROR` for details.
- **"What went wrong?"** — search error logs first, extract a trace ID from the results, then fetch the full trace with `traces_get` for the timeline.
- **Investigating slow requests** — use `traces_list` to find traces, then `traces_get` to inspect spans and durations.

## Response guidelines

- Summarize findings concisely — don't dump raw JSON.
- If you find a trace ID in log entries, mention it and offer to fetch the full trace.
- When reporting errors, include: the service name, error message, and timestamp.
- When reporting traces, show the span hierarchy with durations and highlight where errors occurred.
