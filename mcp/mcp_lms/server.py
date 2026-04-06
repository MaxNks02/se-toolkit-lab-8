"""Stdio MCP server exposing LMS backend operations as typed tools."""

from __future__ import annotations

import asyncio
import json
import os
import time
from collections.abc import Awaitable, Callable, Sequence
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field

from mcp_lms.client import LMSClient

_base_url: str = ""
_victorialogs_url: str = ""
_victoriatraces_url: str = ""

server = Server("lms")

# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------


class _NoArgs(BaseModel):
    """Empty input model for tools that only need server-side configuration."""


class _LabQuery(BaseModel):
    lab: str = Field(description="Lab identifier, e.g. 'lab-04'.")


class _TopLearnersQuery(_LabQuery):
    limit: int = Field(
        default=5, ge=1, description="Max learners to return (default 5)."
    )


class _LogsSearchQuery(BaseModel):
    query: str = Field(default="*", description="LogsQL query, e.g. 'severity:ERROR' or 'db_query AND severity:ERROR'.")
    limit: int = Field(default=20, ge=1, le=100, description="Max log entries to return (default 20).")


class _LogsErrorCountQuery(BaseModel):
    minutes: int = Field(default=60, ge=1, description="Look-back window in minutes (default 60).")


class _TracesListQuery(BaseModel):
    service: str = Field(default="Learning Management Service", description="Service name to filter traces.")
    limit: int = Field(default=10, ge=1, le=50, description="Max traces to return (default 10).")


class _TraceGetQuery(BaseModel):
    trace_id: str = Field(description="The trace ID to fetch, e.g. '1017b6ed5c60c438bc04fe293e39ec93'.")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_api_key() -> str:
    for name in ("NANOBOT_LMS_API_KEY", "LMS_API_KEY"):
        value = os.environ.get(name, "").strip()
        if value:
            return value
    raise RuntimeError(
        "LMS API key not configured. Set NANOBOT_LMS_API_KEY or LMS_API_KEY."
    )


def _client() -> LMSClient:
    if not _base_url:
        raise RuntimeError(
            "LMS backend URL not configured. Pass it as: python -m mcp_lms <base_url>"
        )
    return LMSClient(_base_url, _resolve_api_key())


def _text(data: BaseModel | Sequence[BaseModel]) -> list[TextContent]:
    """Serialize a pydantic model (or list of models) to a JSON text block."""
    if isinstance(data, BaseModel):
        payload = data.model_dump()
    else:
        payload = [item.model_dump() for item in data]
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))]


# ---------------------------------------------------------------------------
# Tool handlers — LMS
# ---------------------------------------------------------------------------


async def _health(_args: _NoArgs) -> list[TextContent]:
    return _text(await _client().health_check())


async def _labs(_args: _NoArgs) -> list[TextContent]:
    items = await _client().get_items()
    return _text([i for i in items if i.type == "lab"])


async def _learners(_args: _NoArgs) -> list[TextContent]:
    return _text(await _client().get_learners())


async def _pass_rates(args: _LabQuery) -> list[TextContent]:
    return _text(await _client().get_pass_rates(args.lab))


async def _timeline(args: _LabQuery) -> list[TextContent]:
    return _text(await _client().get_timeline(args.lab))


async def _groups(args: _LabQuery) -> list[TextContent]:
    return _text(await _client().get_groups(args.lab))


async def _top_learners(args: _TopLearnersQuery) -> list[TextContent]:
    return _text(await _client().get_top_learners(args.lab, limit=args.limit))


async def _completion_rate(args: _LabQuery) -> list[TextContent]:
    return _text(await _client().get_completion_rate(args.lab))


async def _sync_pipeline(_args: _NoArgs) -> list[TextContent]:
    return _text(await _client().sync_pipeline())


# ---------------------------------------------------------------------------
# Tool handlers — Observability (VictoriaLogs + VictoriaTraces)
# ---------------------------------------------------------------------------


async def _logs_search(args: _LogsSearchQuery) -> list[TextContent]:
    url = f"{_victorialogs_url}/select/logsql/query"
    async with httpx.AsyncClient(timeout=10.0) as c:
        r = await c.get(url, params={"query": args.query, "limit": args.limit})
        r.raise_for_status()
        entries = []
        for line in r.text.strip().split("\n"):
            if line.strip():
                entries.append(json.loads(line))
        return [TextContent(type="text", text=json.dumps(entries, ensure_ascii=False))]


async def _logs_error_count(args: _LogsErrorCountQuery) -> list[TextContent]:
    end_us = int(time.time() * 1e6)
    start_us = end_us - args.minutes * 60 * int(1e6)
    url = f"{_victorialogs_url}/select/logsql/query"
    async with httpx.AsyncClient(timeout=10.0) as c:
        r = await c.get(url, params={"query": "severity:ERROR", "limit": 1000, "start": start_us, "end": end_us})
        r.raise_for_status()
        entries = [json.loads(l) for l in r.text.strip().split("\n") if l.strip()]
        counts: dict[str, int] = {}
        for e in entries:
            svc = e.get("otelServiceName", e.get("service.name", "unknown"))
            counts[svc] = counts.get(svc, 0) + 1
        result = {"window_minutes": args.minutes, "total_errors": len(entries), "by_service": counts}
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]


async def _traces_list(args: _TracesListQuery) -> list[TextContent]:
    url = f"{_victoriatraces_url}/select/jaeger/api/traces"
    async with httpx.AsyncClient(timeout=10.0) as c:
        r = await c.get(url, params={"service": args.service, "limit": args.limit})
        r.raise_for_status()
        data = r.json()
        summaries = []
        for trace in data.get("data", []):
            tid = trace["traceID"]
            spans = trace.get("spans", [])
            has_error = any(
                any(t["key"] == "error" and t["value"] == "true" for t in s.get("tags", []))
                for s in spans
            )
            root = next((s for s in spans if not s.get("references")), spans[0] if spans else None)
            summaries.append({
                "trace_id": tid,
                "operation": root["operationName"] if root else "unknown",
                "duration_ms": round(root["duration"] / 1000, 1) if root else 0,
                "spans": len(spans),
                "has_error": has_error,
            })
        return [TextContent(type="text", text=json.dumps(summaries, ensure_ascii=False))]


async def _traces_get(args: _TraceGetQuery) -> list[TextContent]:
    url = f"{_victoriatraces_url}/select/jaeger/api/traces/{args.trace_id}"
    async with httpx.AsyncClient(timeout=10.0) as c:
        r = await c.get(url)
        r.raise_for_status()
        data = r.json()
        spans = []
        for trace in data.get("data", []):
            for s in trace.get("spans", []):
                tags = {t["key"]: t["value"] for t in s.get("tags", [])}
                spans.append({
                    "span_id": s["spanID"],
                    "operation": s["operationName"],
                    "duration_ms": round(s["duration"] / 1000, 1),
                    "error": tags.get("error") == "true",
                    "status_description": tags.get("otel.status_description", ""),
                    "db_statement": tags.get("db.statement", ""),
                })
        return [TextContent(type="text", text=json.dumps(spans, ensure_ascii=False))]


# ---------------------------------------------------------------------------
# Registry: tool name -> (input model, handler, Tool definition)
# ---------------------------------------------------------------------------

_Registry = tuple[type[BaseModel], Callable[..., Awaitable[list[TextContent]]], Tool]

_TOOLS: dict[str, _Registry] = {}


def _register(
    name: str,
    description: str,
    model: type[BaseModel],
    handler: Callable[..., Awaitable[list[TextContent]]],
) -> None:
    schema = model.model_json_schema()
    # Pydantic puts definitions under $defs; flatten for MCP's JSON Schema expectation.
    schema.pop("$defs", None)
    schema.pop("title", None)
    _TOOLS[name] = (
        model,
        handler,
        Tool(name=name, description=description, inputSchema=schema),
    )


_register(
    "lms_health",
    "Check if the LMS backend is healthy and report the item count.",
    _NoArgs,
    _health,
)
_register("lms_labs", "List all labs available in the LMS.", _NoArgs, _labs)
_register(
    "lms_learners", "List all learners registered in the LMS.", _NoArgs, _learners
)
_register(
    "lms_pass_rates",
    "Get pass rates (avg score and attempt count per task) for a lab.",
    _LabQuery,
    _pass_rates,
)
_register(
    "lms_timeline",
    "Get submission timeline (date + submission count) for a lab.",
    _LabQuery,
    _timeline,
)
_register(
    "lms_groups",
    "Get group performance (avg score + student count per group) for a lab.",
    _LabQuery,
    _groups,
)
_register(
    "lms_top_learners",
    "Get top learners by average score for a lab.",
    _TopLearnersQuery,
    _top_learners,
)
_register(
    "lms_completion_rate",
    "Get completion rate (passed / total) for a lab.",
    _LabQuery,
    _completion_rate,
)
_register(
    "lms_sync_pipeline",
    "Trigger the LMS sync pipeline. May take a moment.",
    _NoArgs,
    _sync_pipeline,
)
_register(
    "logs_search",
    "Search structured logs by LogsQL query. Use 'severity:ERROR' for errors, '*' for all.",
    _LogsSearchQuery,
    _logs_search,
)
_register(
    "logs_error_count",
    "Count error logs per service over a time window (in minutes).",
    _LogsErrorCountQuery,
    _logs_error_count,
)
_register(
    "traces_list",
    "List recent traces for a service with summary (duration, error status, span count).",
    _TracesListQuery,
    _traces_list,
)
_register(
    "traces_get",
    "Fetch full span details for a specific trace by trace ID.",
    _TraceGetQuery,
    _traces_get,
)


# ---------------------------------------------------------------------------
# MCP handlers
# ---------------------------------------------------------------------------


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [entry[2] for entry in _TOOLS.values()]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    entry = _TOOLS.get(name)
    if entry is None:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    model_cls, handler, _ = entry
    try:
        args = model_cls.model_validate(arguments or {})
        return await handler(args)
    except Exception as exc:
        return [TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def main(base_url: str | None = None) -> None:
    global _base_url, _victorialogs_url, _victoriatraces_url
    _base_url = base_url or os.environ.get("NANOBOT_LMS_BACKEND_URL", "")
    _victorialogs_url = os.environ.get("VICTORIALOGS_URL", "http://victorialogs:9428")
    _victoriatraces_url = os.environ.get("VICTORIATRACES_URL", "http://victoriatraces:10428")
    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    asyncio.run(main())
