import os
import json

config_path = "/app/nanobot/config.json"
resolved_path = "/app/nanobot/config.resolved.json"
workspace = "/app/nanobot/workspace"

with open(config_path, "r") as f:
    config = json.load(f)

# Inject LLM provider credentials
providers = config.setdefault("providers", {})
custom = providers.setdefault("custom", {})
custom["api_key"] = os.environ.get("LLM_API_KEY", custom.get("api_key", ""))
custom["api_base"] = os.environ.get("LLM_API_BASE_URL", custom.get("api_base", ""))

# Set model and provider
agents = config.setdefault("agents", {})
defaults = agents.setdefault("defaults", {})
defaults["model"] = os.environ.get("LLM_API_MODEL", defaults.get("model", "coder-model"))
defaults["provider"] = "custom"

# Inject gateway settings
gateway = config.setdefault("gateway", {})
gateway["host"] = os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS", "0.0.0.0")
gateway["port"] = int(os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT", "18790"))

# Inject webchat channel settings
channels = config.setdefault("channels", {})
webchat = channels.setdefault("webchat", {})
webchat["enabled"] = True
webchat["host"] = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_ADDRESS", "0.0.0.0")
webchat["port"] = int(os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT", "8765"))

# Inject MCP server env vars
tools = config.setdefault("tools", {})
mcp_servers = tools.setdefault("mcp_servers", {})
lms = mcp_servers.setdefault("lms", {})
lms["command"] = "python"
lms["args"] = ["-m", "mcp_lms"]
lms_env = lms.setdefault("env", {})
lms_env["NANOBOT_LMS_BACKEND_URL"] = os.environ.get("NANOBOT_LMS_BACKEND_URL", "")
lms_env["NANOBOT_LMS_API_KEY"] = os.environ.get("NANOBOT_LMS_API_KEY", "")
lms_env["VICTORIALOGS_URL"] = os.environ.get("VICTORIALOGS_URL", "http://victorialogs:9428")
lms_env["VICTORIATRACES_URL"] = os.environ.get("VICTORIATRACES_URL", "http://victoriatraces:10428")

with open(resolved_path, "w") as f:
    json.dump(config, f, indent=2)

os.execvp("nanobot", ["nanobot", "gateway", "--config", resolved_path, "--workspace", workspace])
