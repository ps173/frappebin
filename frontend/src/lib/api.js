import { createResource } from 'frappe-ui'

// Thin imperative wrapper over a frappe whitelisted method. Returns a promise.
// All Frappebin endpoints accept POST, so submit() works uniformly.
export function callMethod(method, params = {}) {
  const resource = createResource({ url: method })
  return resource.submit(params)
}

export const api = {
  createSnippet: (params) => callMethod('frappebin.api.create_snippet', params),
  getSnippet: (name, key) => callMethod('frappebin.api.get_snippet', { name, key }),
  updateSnippet: (params) => callMethod('frappebin.api.update_snippet', params),
  deleteSnippet: (name, edit_token) =>
    callMethod('frappebin.api.delete_snippet', { name, edit_token }),
  getLanguages: () => callMethod('frappebin.api.get_languages', {}),
}

// Build the raw text URL (served as text/plain by the backend).
export function rawUrl(name, key) {
  const q = key ? `?key=${encodeURIComponent(key)}` : ''
  return `/api/method/frappebin.api.get_raw?name=${encodeURIComponent(name)}${q}`
}
