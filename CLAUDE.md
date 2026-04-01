# PointMeistro — Claude Development Guide

Enterprise point cloud segmentation for steel fabrication. Processes BLK360 scans to
extract concrete geometry for import into Tekla Structures, Revit, and SDS/2.
Built by Mark Hubrich (Meistro) at Adams Steel Service.

**Status: Active development — app is not feature-complete.**

## Stack
| Layer | Tech |
|---|---|
| Web/API | Laravel 13 (PHP 8.4, PHP-FPM) |
| Frontend | Blade + Vite + Tailwind CSS |
| Queue | Laravel Horizon (Redis-backed) |
| WebSockets | Laravel Reverb (port 8080) |
| Auth | Laravel Sanctum |
| Segmentation | Python 3.10 + FastAPI + Open3D (GPU, port 8001) |
| Database | PostgreSQL 16 (port 5432) |
| Cache/Queue | Redis 7 (port 6379) |
| Proxy | Nginx (port 80) |

## Starting the Dev Environment
```bash
./dev.sh          # live-reload stack (PHP + Python + Vite HMR)
./dev.sh -d       # same but detached
```
This runs `docker-compose.yml` + `docker-compose.dev.yml` together.

## Key URLs (once running)
- http://localhost — Laravel app
- http://localhost:5173 — Vite HMR server (assets, auto-injected)
- http://localhost:8001 — Python segmentation API
- http://localhost:8080 — Reverb WebSockets

## Live Reload Behaviour
| Change type | Result |
|---|---|
| PHP / Blade | Instant — volume-mounted, F5 to see |
| JS / CSS | Vite HMR — browser updates automatically |
| Python (segment.py) | uvicorn --reload watches /app |
| Config / .env | Run `clear_cache` tool or `./dev.sh` restart |
| Horizon workers | Use `restart_service horizon` tool |

## MCP Setup
The MCP server (`mcp-server/server.py`) is registered in `.mcp.json` (project-level)
and in `~/.claude.json` (local scope, already active for this project).

To verify it's running: `claude mcp list` — should show `pointmeistro: ✓ Connected`

If you're on a new machine or it shows disconnected:
```bash
pip3 install mcp --break-system-packages
claude mcp add --scope local pointmeistro python3 -- /home/mark/PointMeistro/mcp-server/server.py
```

Claude has direct access to the running stack via these tools:

| Tool | What it does |
|---|---|
| `artisan <cmd>` | Run any artisan command in the app container |
| `logs <service>` | Tail logs from any container |
| `containers` | Show health of all containers |
| `clear_cache` | php artisan optimize:clear |
| `run_tests [filter]` | Run PHPUnit |
| `db_query <sql>` | Read-only SELECT against Postgres |
| `segmenter_health` | Python service health + logs |
| `restart_service <svc>` | Restart horizon / reverb / nginx |
| `composer <cmd>` | Run composer in app container |

## Project Layout
```
PointMeistro/
├── laravel-app/        # Laravel 13 application
│   ├── app/            # Models, Controllers, Jobs, etc. (to be built)
│   ├── resources/      # Blade views, JS, CSS
│   ├── routes/         # web.php, api.php
│   └── database/       # Migrations, factories, seeders
├── python-segmenter/   # FastAPI GPU segmentation service
│   └── segment.py      # Main segmentation logic
├── nginx/              # Nginx config
├── models/             # ML model weights (.pth files)
├── storage/            # Uploaded scans, processed output
├── mcp-server/         # This MCP server
├── docker-compose.yml
└── docker-compose.dev.yml
```

## Database
- PostgreSQL 16, db: `pointmeistro`, user: `meistro`
- Migrations live in `laravel-app/database/migrations/`
- Always use migrations — never edit the DB directly

## Coding Conventions
- Laravel: follow standard Laravel conventions (resource controllers, form requests, jobs for heavy work)
- Segmentation jobs are queued via Horizon — never run synchronously in a request
- Point cloud uploads go to `storage/` (shared volume between Laravel and Python)
- Python service communicates with Laravel via HTTP (internal Docker network)
