# Observability Strategy

You have access to observability tools that query VictoriaLogs (structured logs) and VictoriaTraces (distributed traces).

## Available tools

- `logs_search` — search logs with LogsQL. Examples: `severity:ERROR`, `db_query AND severity:ERROR`, `*` for all.
- `logs_error_count` — count errors per service in a time window. Use this first when asked about recent errors.
- `traces_list` — list recent traces for a service, showing duration and error status.
- `traces_get` — fetch full span details for a trace ID.

## Investigation workflow

When asked **"What went wrong?"** or **"Check system health"**, follow this sequence:

1. **Start with `logs_error_count`** to get a quick summary of errors in the last hour.
2. **If errors exist**, use `logs_search` with `severity:ERROR` to get the actual error details (messages, trace IDs, timestamps).
3. **Extract a trace ID** from the error logs and use `traces_get` to fetch the full trace — this shows the complete request timeline with all spans.
4. **Summarize findings** concisely: which service failed, what the error was, which span in the trace shows the failure, and how long the request took.

## Response guidelines

- Summarize findings concisely — don't dump raw JSON.
- Always chain logs and traces together: find errors in logs, then get the trace for context.
- When reporting errors, include: the service name, error message, timestamp, and trace ID.
- When reporting traces, highlight which span has the error and show the duration breakdown.
- If the HTTP status code looks wrong (e.g., 404 for a database error), mention this discrepancy — it could indicate a bug in error handling.
