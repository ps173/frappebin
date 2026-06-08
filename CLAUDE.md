# Frappebin — project notes

Pastebin clone on the Frappe framework. Snippets (code / logs / notes) shared via
link with three visibility levels: Public, Unlisted (secret-key link), Private.
Anonymous users can both create and view; no login required to view a public link.

## Frontend (frappe-ui SPA)

The SPA lives in `frontend/` (Vite + Vue 3 + frappe-ui) and is served at `/frappebin`.

### Dev

```bash
cd frontend
yarn dev
```

Then open **`http://frappebin.localhost:8080/frappebin`** — use the **site hostname**,
not `localhost`. The dev proxy (`getProxyOptions`) routes `/api`, `/app`, `/login`,
`/assets`, `/files` to the backend **by `Host` header**, so `localhost:8080` would
proxy to a non-existent site named `localhost`. The backend must be running
(`bench start` / the webserver on the configured port).

### Build

```bash
cd frontend
yarn build
```

Build flow (mirrors apps/crm and apps/helpdesk — do NOT deviate):
- `vite build --base=/assets/frappebin/frontend/` → emits assets to
  `frappebin/public/frontend/` with the correct asset base.
- `copy-html-entry` then `cp`s the built `index.html` to `frappebin/www/frappebin.html`.

**Important:** `base` is set ONLY via the `--base` build flag (see `package.json`),
never in `vite.config.js`. Putting `base` in the config breaks `yarn dev` (blank page).

### How serving works
- `frappebin/www/frappebin.html` is the built SPA shell (gitignored; regenerated each build).
- `frappebin/www/frappebin.py` `get_context` supplies `{{ csrf_token }}` to the shell
  (same role as `crm.py`'s boot data).
- `website_route_rules` in `hooks.py` maps `/frappebin/<path:app_path>` → `frappebin` so
  client-side deep links (e.g. `/frappebin/<snippet>`) resolve to the SPA.
- Router uses `createWebHistory('/frappebin')`, so the base must stay `/frappebin`.

## Backend

- DocTypes: `Snippet` (hash autoname = URL slug; raw `Code` content; `secret_key` +
  `edit_token` generated server-side), `Snippet Language` (seeded via `fixtures`).
- API: `frappebin/api.py` — all endpoints `@frappe.whitelist(allow_guest=True)` +
  `@rate_limit` (`from frappe.rate_limiter import rate_limit`, NOT `frappe.rate_limit`).
  Access control lives here, not in DocType perms (which stay System-Manager-locked);
  methods read/write with `ignore_permissions` after their own checks.
- Visibility gate returns **404, not 403**, on unlisted/private misses (don't leak
  existence). Tokens are never returned in `get_snippet` payloads.
- `tasks.py::delete_expired_snippets` runs hourly (`scheduler_events` in `hooks.py`).
- Content is stored as **raw text** and rendered escaped (highlight.js) on view —
  never render user content as HTML (stored-XSS).
