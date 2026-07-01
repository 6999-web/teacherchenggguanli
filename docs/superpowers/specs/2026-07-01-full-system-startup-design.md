# Full System Startup Design

## Scope

This change only fixes how the complete local demo system is started and verified. It does not change business pages, navigation labels, data models, API behavior, or existing UI flows.

## Services

The full system consists of six local services:

| Service | URL | Source |
| --- | --- | --- |
| Unified portal | `http://127.0.0.1:5001/` | `portal/` |
| Teacher reward/HR frontend | `http://127.0.0.1:5004/student/login` | `studentsystem-main/frontend/` |
| Reward/HR admin frontend | `http://127.0.0.1:5005/admin/login` | `studentsystem-main/admin/` |
| Reward/HR backend | `http://127.0.0.1:5006/health` | `studentsystem-main/backend/` |
| Evaluation backend | `http://127.0.0.1:5007/api/openapi.json` | `backend/` |
| Evaluation frontend | `http://127.0.0.1:5008/login` | `jys-frontend/` |

## Startup Behavior

Create a single PowerShell launcher that:

1. Checks whether each expected port is already listening.
2. Reuses a listening service instead of killing it.
3. Starts only missing services.
4. Writes one stdout and one stderr log file per service under `logs/`.
5. Verifies every service with an HTTP request after startup.
6. Prints a concise table with service name, URL, status, PID when available, and log paths.

## Implementation Notes

Use existing local assets and runtimes:

- Portal: serve `portal/` as static files on port `5001`.
- Teacher reward/HR frontend: run Vite in `studentsystem-main/frontend` on port `5004`.
- Reward/HR admin frontend: run Vite in `studentsystem-main/admin` on port `5005`.
- Reward/HR backend: run `studentsystem-main/backend/main.py`, which already uses port `5006`.
- Evaluation backend: run `uvicorn app.main:app --host 127.0.0.1 --port 5007` in `backend/`.
- Evaluation frontend: use the existing SPA/static proxy pattern for `jys-frontend/` on port `5008`, proxying `/api` to `5007`.

The script should avoid destructive actions. It may report a conflicting or unhealthy service, but it should not terminate unrelated processes automatically.

## Verification

After startup, verify:

- `GET http://127.0.0.1:5001/` returns `200`.
- `GET http://127.0.0.1:5004/student/login` returns `200`.
- `GET http://127.0.0.1:5005/admin/login` returns `200`.
- `GET http://127.0.0.1:5006/health` returns `200`.
- `GET http://127.0.0.1:5007/api/openapi.json` returns `200`.
- `GET http://127.0.0.1:5008/login` returns `200`.

If a service fails verification, the script should print the relevant log file path so the next debugging step is obvious.

## Out Of Scope

- Reworking portal copy or visual design.
- Changing teacher/admin menus.
- Changing hard-coded frontend API URLs.
- Database migrations or seed data changes.
- Stopping existing services automatically.
