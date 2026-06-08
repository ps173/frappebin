<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import { api, rawUrl } from '@/lib/api'
import { getEditToken } from '@/lib/tokens'

const props = defineProps({ name: { type: String, required: true } })
const route = useRoute()
const router = useRouter()

const snippet = ref(null)
const loading = ref(true)
const error = ref('')
const burned = ref(false)
const copied = ref(false)

// key comes from the share link query (?key=...)
const key = computed(() => route.query.key || null)
const editToken = computed(() => getEditToken(props.name))
const canEdit = computed(() => snippet.value && (snippet.value.is_owner || !!editToken.value))

// highlight.js escapes the input, so the output is XSS-safe to render with v-html.
const highlighted = computed(() => {
  if (!snippet.value) return ''
  const alias = snippet.value.highlight_alias
  const content = snippet.value.content || ''
  if (alias && alias !== 'plaintext' && hljs.getLanguage(alias)) {
    return hljs.highlight(content, { language: alias }).value
  }
  // Escape manually for plaintext.
  const div = document.createElement('div')
  div.textContent = content
  return div.innerHTML
})

onMounted(load)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await api.getSnippet(props.name, key.value)
    snippet.value = data
    burned.value = !!data.burned
  } catch (e) {
    error.value = 'Snippet not found, expired, or you do not have access.'
  } finally {
    loading.value = false
  }
}

async function copyContent() {
  await navigator.clipboard.writeText(snippet.value.content)
  copied.value = true
  setTimeout(() => (copied.value = false), 1500)
}

function openRaw() {
  window.open(rawUrl(props.name, key.value), '_blank')
}

async function remove() {
  if (!confirm('Delete this snippet permanently?')) return
  try {
    await api.deleteSnippet(props.name, editToken.value)
    router.push({ name: 'Mine' })
  } catch (e) {
    error.value = 'Could not delete this snippet.'
  }
}
</script>

<template>
  <div>
    <div v-if="loading" class="text-sm text-gray-500">Loading…</div>

    <div v-else-if="error" class="rounded-lg border border-red-200 bg-red-50 p-6 text-center">
      <p class="text-sm text-red-700">{{ error }}</p>
      <router-link to="/" class="mt-3 inline-block text-sm font-medium text-gray-900 underline">
        Create a new snippet
      </router-link>
    </div>

    <div v-else-if="snippet">
      <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div>
          <h1 class="text-xl font-semibold">{{ snippet.title || 'Untitled' }}</h1>
          <div class="mt-1 flex items-center gap-2 text-xs text-gray-500">
            <span class="rounded bg-gray-100 px-2 py-0.5 font-medium">{{ snippet.language }}</span>
            <span class="rounded bg-gray-100 px-2 py-0.5 font-medium">{{ snippet.visibility }}</span>
            <span>{{ snippet.view_count }} views</span>
          </div>
        </div>

        <div class="flex flex-wrap gap-2">
          <button class="btn-secondary" @click="copyContent">{{ copied ? 'Copied!' : 'Copy' }}</button>
          <button class="btn-secondary" @click="openRaw">Raw</button>
          <template v-if="canEdit">
            <router-link :to="{ name: 'Edit', params: { name } }" class="btn-secondary">Edit</router-link>
            <button class="btn-danger" @click="remove">Delete</button>
          </template>
        </div>
      </div>

      <p v-if="burned" class="mb-3 rounded-md bg-amber-50 px-3 py-2 text-xs text-amber-700">
        🔥 This was a burn-after-read snippet — it has now been deleted and this link will no longer work.
      </p>

      <pre class="overflow-x-auto rounded-lg border border-gray-200 bg-white p-4 text-sm leading-relaxed"><code class="hljs" v-html="highlighted"></code></pre>
    </div>
  </div>
</template>

<style scoped>
.btn-secondary {
  @apply rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100;
}
.btn-danger {
  @apply rounded-md border border-red-300 px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-50;
}
</style>
