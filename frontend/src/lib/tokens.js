// Anonymous creators have no login, so we remember the edit_token (and secret_key)
// for snippets they made in localStorage. This is what lets them edit/delete later
// and see "your snippets" without an account.

const STORE_KEY = 'frappebin_snippets'

function readStore() {
  try {
    return JSON.parse(localStorage.getItem(STORE_KEY) || '{}')
  } catch {
    return {}
  }
}

function writeStore(data) {
  localStorage.setItem(STORE_KEY, JSON.stringify(data))
}

export function rememberSnippet(name, { edit_token, secret_key, title, visibility }) {
  const store = readStore()
  store[name] = {
    edit_token,
    secret_key,
    title: title || 'Untitled',
    visibility,
    created: Date.now(),
  }
  writeStore(store)
}

export function getEditToken(name) {
  return readStore()[name]?.edit_token || null
}

export function getStoredSecret(name) {
  return readStore()[name]?.secret_key || null
}

export function forgetSnippet(name) {
  const store = readStore()
  delete store[name]
  writeStore(store)
}

export function listMySnippets() {
  const store = readStore()
  return Object.entries(store)
    .map(([name, meta]) => ({ name, ...meta }))
    .sort((a, b) => b.created - a.created)
}
