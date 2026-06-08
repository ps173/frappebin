# Frappebin frontend

The Frappebin SPA — Vite + Vue 3 + [frappe-ui](https://github.com/frappe/frappe-ui),
served at `/frontend` in production.

## Dev

```bash
cd frontend
yarn        # install deps (first time)
yarn dev
```

Then open **`http://frappebin.localhost:8080/frontend`** — use the **site hostname**,
not `localhost`. The dev proxy (`getProxyOptions` in `vite.config.js`) routes `/api`,
`/app`, `/login`, `/assets`, `/files` to the backend **by `Host` header**, so
`localhost:8080` would proxy to a non-existent site named `localhost`.

The backend must be running (`bench start`, or the webserver on the configured port).

In development, add the following to your site's `site_config.json` to avoid
`CSRFToken` errors from the Vite dev server:

```json
"ignore_csrf": 1
```

In production the `csrf_token` is injected into the SPA shell server-side
(see `frappebin/www/frontend.py`), so this is a dev-only setting.

## Build

```bash
cd frontend
yarn build
```

Build flow (mirrors apps/crm and apps/helpdesk — **do not deviate**):

1. `vite build --base=/assets/frappebin/frontend/` emits assets to
   `frappebin/public/frontend/` with the correct asset base.
2. `copy-html-entry` then copies the built `index.html` to
   `frappebin/www/frontend.html`.

> **Important:** `base` is set **only** via the `--base` build flag (see
> `package.json`), never in `vite.config.js`. Putting `base` in the config breaks
> `yarn dev` (blank page).

The build outputs (`frappebin/public/frontend/` and `frappebin/www/frontend.html`)
are generated artifacts and are **gitignored** — regenerate them with `yarn build`.

## How serving works

- `frappebin/www/frontend.html` is the built SPA shell (regenerated each build).
- `frappebin/www/frontend.py`'s `get_context` supplies `{{ csrf_token }}` to the shell.
- `website_route_rules` in `hooks.py` maps `/frontend/<path:app_path>` → `frontend`
  so client-side deep links (e.g. `/frontend/<snippet>`) resolve to the SPA.
- The router uses `createWebHistory('/frontend')`, so the base must stay `/frontend`.

## Project layout

```
src/
  pages/        Editor.vue, View.vue, Mine.vue
  components/   ShareDialog.vue
  lib/          api.js (whitelisted-method wrapper), tokens.js (localStorage edit tokens)
  router.js     createWebHistory('/frontend')
  main.js       app entry
index.html      Vite entry template (required for dev and build)
```

## Resources

- [Vue 3](https://vuejs.org/guide/introduction.html)
- [Vue Router](https://router.vuejs.org/)
- [Frappe UI](https://github.com/frappe/frappe-ui)
- [TailwindCSS](https://tailwindcss.com/docs/utility-first)
- [Vite](https://vitejs.dev/guide/)
