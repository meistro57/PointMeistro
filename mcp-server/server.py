#!/usr/bin/env python3
"""PointMeistro MCP Server — gives Claude tools to interact with the running stack."""

import asyncio
import shlex
import subprocess
from pathlib import Path

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp import types

PROJECT_DIR = Path(__file__).parent.parent
COMPOSE_FILES = ["-f", str(PROJECT_DIR / "docker-compose.yml")]

CONTAINERS = {
    "app":       "pointmeistro-app",
    "horizon":   "pointmeistro-horizon",
    "reverb":    "pointmeistro-reverb",
    "segmenter": "pointmeistro-segmenter",
    "db":        "pointmeistro-db",
    "redis":     "pointmeistro-redis",
    "nginx":     "pointmeistro-nginx",
    "vite":      "pointmeistro-vite",
}

server = Server("pointmeistro")


def run(cmd: list[str], timeout: int = 30) -> str:
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            cwd=str(PROJECT_DIR)
        )
        return (result.stdout + result.stderr).strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return f"Timed out after {timeout}s"
    except Exception as e:
        return f"Error: {e}"


def artisan(cmd: str, timeout: int = 60) -> str:
    parts = shlex.split(cmd)
    return run(["docker", "exec", CONTAINERS["app"], "php", "artisan"] + parts, timeout)


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="artisan",
            description="Run a Laravel artisan command in the app container. Examples: 'migrate', 'route:list', 'make:model Job -m'",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {"type": "string"}
                },
                "required": ["command"]
            }
        ),
        types.Tool(
            name="logs",
            description="Get recent logs from a container",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "enum": list(CONTAINERS.keys())
                    },
                    "lines": {"type": "integer", "default": 50}
                },
                "required": ["service"]
            }
        ),
        types.Tool(
            name="containers",
            description="Show status of all PointMeistro containers",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="clear_cache",
            description="Clear all Laravel caches (config, route, view, compiled). Run after config changes.",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="run_tests",
            description="Run PHPUnit tests in the app container",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter": {"type": "string", "description": "Optional test name filter"}
                }
            }
        ),
        types.Tool(
            name="db_query",
            description="Run a read-only SELECT query against PostgreSQL",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {"type": "string"}
                },
                "required": ["sql"]
            }
        ),
        types.Tool(
            name="segmenter_health",
            description="Check the Python segmentation service health and recent logs",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="restart_service",
            description="Restart a single container without rebuilding (useful after code changes that need a restart, e.g. horizon)",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "enum": ["horizon", "reverb", "nginx"]
                    }
                },
                "required": ["service"]
            }
        ),
        types.Tool(
            name="composer",
            description="Run a composer command in the app container. Example: 'require laravel/telescope'",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {"type": "string"}
                },
                "required": ["command"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "artisan":
        output = artisan(arguments["command"])

    elif name == "logs":
        service = arguments["service"]
        lines = arguments.get("lines", 50)
        output = run(["docker", "logs", "--tail", str(lines), CONTAINERS[service]])

    elif name == "containers":
        output = run(["docker", "compose"] + COMPOSE_FILES + ["ps"])

    elif name == "clear_cache":
        output = artisan("optimize:clear", timeout=30)

    elif name == "run_tests":
        cmd = "test"
        if f := arguments.get("filter"):
            cmd += f" --filter {shlex.quote(f)}"
        output = artisan(cmd, timeout=120)

    elif name == "db_query":
        sql = arguments["sql"].strip()
        if not sql.upper().lstrip().startswith("SELECT"):
            return [types.TextContent(type="text", text="Error: only SELECT queries are permitted")]
        output = run([
            "docker", "exec", CONTAINERS["db"],
            "psql", "-U", "meistro", "-d", "pointmeistro", "-c", sql
        ], timeout=15)

    elif name == "segmenter_health":
        health = run(["docker", "exec", CONTAINERS["segmenter"],
                      "curl", "-sf", "http://localhost:8001/health"], timeout=10)
        logs = run(["docker", "logs", "--tail", "30", CONTAINERS["segmenter"]])
        output = f"=== Health ===\n{health}\n\n=== Recent Logs ===\n{logs}"

    elif name == "restart_service":
        service = arguments["service"]
        output = run(["docker", "compose"] + COMPOSE_FILES + ["restart", service], timeout=30)

    elif name == "composer":
        parts = shlex.split(arguments["command"])
        output = run(["docker", "exec", CONTAINERS["app"], "composer"] + parts, timeout=120)

    else:
        output = f"Unknown tool: {name}"

    return [types.TextContent(type="text", text=output)]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="pointmeistro",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
