FROM python:3.14-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY . /app/nanobot/
COPY --from=workspace mcp /app/mcp
COPY --from=workspace nanobot-websocket-channel /app/nanobot-websocket-channel

WORKDIR /app/nanobot
RUN uv sync

FROM python:3.14-slim-bookworm
WORKDIR /app
ENV PATH="/app/nanobot/.venv/bin:$PATH"

COPY --from=builder /app /app

WORKDIR /app/nanobot
CMD ["python", "entrypoint.py"]
