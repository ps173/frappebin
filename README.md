# Frappebin

A Pastebin clone built on the [Frappe](https://github.com/frappe/frappe) framework.
Share snippets — code, logs, or notes — via link, with no account required to create
or view.

## Features

- **Anonymous create & view** — no login needed. Anonymous creators get an
  `edit_token` (stored in their browser) that lets them edit or delete later.
- **Three visibility levels:**
  - **Public** — anyone with the link can view.
  - **Unlisted** — only reachable with the secret-key share link.
  - **Private** — same secret-key gate; not surfaced anywhere public.
- **Expiry** — optional auto-deletion (10 min → 1 week). An hourly scheduled job
  (`tasks.delete_expired_snippets`) sweeps expired snippets; reads also clean them up
  opportunistically.
- **Burn after read** — snippet is deleted the first time a non-owner views it.
- **Syntax highlighting** — rendered client-side with highlight.js. Content is stored
  as raw text and always rendered escaped (no stored XSS).
- **Raw view** — `…/api/method/frappebin.api.get_raw` serves the body as `text/plain`
  for `curl`/`wget`.

## Architecture

| Layer | Location | Notes |
|-------|----------|-------|
| DocType | `frappebin/frappebin/doctype/snippet/` | `Snippet` (hash autoname = URL slug), `secret_key` + `edit_token` generated server-side. `Snippet Language` is seeded via fixtures. |
| API | `frappebin/api.py` | All endpoints `@frappe.whitelist(allow_guest=True)` + `@rate_limit`. Access control lives here, not in DocType perms (which stay System-Manager-locked). |
| Frontend | `frontend/` | Vite + Vue 3 + frappe-ui SPA, served at `/frontend`. |
| Serving | `frappebin/www/frontend.py` + `website_route_rules` | Serves the built SPA shell and routes deep links to it. |

### Security model

- Access control is centralized in `api.py`; methods read/write with
  `ignore_permissions` **after** running their own checks.
- Unlisted/Private misses return **404, not 403**, so existence is never leaked.
- The secret key is compared in constant time (`hmac.compare_digest`).
- `secret_key` / `edit_token` are generated server-side and never returned in
  view payloads or accepted as authoritative write input.

## Installation

Install with the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch main
bench install-app frappebin
```

## Frontend development

See [`frontend/README.md`](frontend/README.md) for the dev server and build flow.

## Contributing

This app uses `pre-commit` for code formatting and linting. Please
[install pre-commit](https://pre-commit.com/#installation) and enable it for this
repository:

```bash
cd apps/frappebin
pre-commit install
```

Pre-commit is configured to use the following tools:

- ruff
- eslint
- prettier
- pyupgrade

## License

mit
