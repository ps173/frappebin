<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/lib/api'
import { rememberSnippet, getEditToken, getStoredSecret } from '@/lib/tokens'
import ShareDialog from '@/components/ShareDialog.vue'

const route = useRoute()
const router = useRouter()

// Edit mode when the route carries a :name param.
const editName = computed(() => route.params.name || null)
const isEdit = computed(() => !!editName.value)

const form = reactive({
  title: '',
  content: '',
  language: 'plaintext',
  visibility: 'Unlisted',
  expiry: 'never',
  burn_after_read: false,
})

const languages = ref([])
const loading = ref(false)
const error = ref('')
const created = ref(null) // { name, secret_key, edit_token, visibility }

const EXPIRY_PRESETS = [
  { value: 'never', label: 'Never' },
  { value: '10m', label: '10 minutes', ms: 10 * 60 * 1000 },
  { value: '1h', label: '1 hour', ms: 60 * 60 * 1000 },
  { value: '1d', label: '1 day', ms: 24 * 60 * 60 * 1000 },
  { value: '1w', label: '1 week', ms: 7 * 24 * 60 * 60 * 1000 },
]

function expiryToDatetime(preset) {
  const found = EXPIRY_PRESETS.find((p) => p.value === preset)
  if (!found || !found.ms) return null
  const d = new Date(Date.now() + found.ms)
  // Frappe datetime format: YYYY-MM-DD HH:MM:SS
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

onMounted(async () => {
  try {
    languages.value = await api.getLanguages()
  } catch (e) {
    languages.value = [{ value: 'plaintext', label: 'plaintext' }]
  }

  if (isEdit.value) {
    await loadForEdit()
  }
})

async function loadForEdit() {
  loading.value = true
  try {
    const key = getStoredSecret(editName.value)
    const snippet = await api.getSnippet(editName.value, key)
    form.title = snippet.title
    form.content = snippet.content
    form.language = snippet.language || 'plaintext'
    form.visibility = snippet.visibility
    form.burn_after_read = !!snippet.burn_after_read
  } catch (e) {
    error.value = 'Could not load this snippet for editing.'
  } finally {
    loading.value = false
  }
}

async function save() {
  error.value = ''
  if (!form.content.trim()) {
    error.value = 'Content cannot be empty.'
    return
  }
  loading.value = true
  try {
    if (isEdit.value) {
      await api.updateSnippet({
        name: editName.value,
        edit_token: getEditToken(editName.value),
        title: form.title,
        content: form.content,
        language: form.language,
        visibility: form.visibility,
        burn_after_read: form.burn_after_read ? 1 : 0,
      })
      router.push({ name: 'View', params: { name: editName.value } })
    } else {
      const res = await api.createSnippet({
        title: form.title,
        content: form.content,
        language: form.language,
        visibility: form.visibility,
        expires_on: expiryToDatetime(form.expiry),
        burn_after_read: form.burn_after_read ? 1 : 0,
      })
      rememberSnippet(res.name, {
        edit_token: res.edit_token,
        secret_key: res.secret_key,
        title: form.title,
        visibility: res.visibility,
      })
      created.value = res
    }
  } catch (e) {
    error.value = e?.messages?.join(', ') || e?.message || 'Something went wrong.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <h1 class="mb-4 text-xl font-semibold">
      {{ isEdit ? 'Edit snippet' : 'New snippet' }}
    </h1>

    <div class="space-y-4 rounded-lg border border-gray-200 bg-white p-4">
      <div>
        <label class="mb-1 block text-sm font-medium text-gray-700">Title</label>
        <input
          v-model="form.title"
          type="text"
          placeholder="Untitled"
          class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-900 focus:outline-none"
        />
      </div>

      <div>
        <label class="mb-1 block text-sm font-medium text-gray-700">Content</label>
        <textarea
          v-model="form.content"
          rows="16"
          spellcheck="false"
          placeholder="Paste code, logs, or notes here…"
          class="w-full rounded-md border border-gray-300 px-3 py-2 font-mono text-sm leading-relaxed focus:border-gray-900 focus:outline-none"
        ></textarea>
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div>
          <label class="mb-1 block text-sm font-medium text-gray-700">Language</label>
          <select
            v-model="form.language"
            class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-900 focus:outline-none"
          >
            <option v-for="l in languages" :key="l.value" :value="l.value">{{ l.label }}</option>
          </select>
        </div>

        <div>
          <label class="mb-1 block text-sm font-medium text-gray-700">Visibility</label>
          <select
            v-model="form.visibility"
            class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-900 focus:outline-none"
          >
            <option value="Public">Public — anyone with the link</option>
            <option value="Unlisted">Unlisted — secret link required</option>
            <option value="Private">Private — only you</option>
          </select>
        </div>

        <div v-if="!isEdit">
          <label class="mb-1 block text-sm font-medium text-gray-700">Expires</label>
          <select
            v-model="form.expiry"
            class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-900 focus:outline-none"
          >
            <option v-for="p in EXPIRY_PRESETS" :key="p.value" :value="p.value">{{ p.label }}</option>
          </select>
        </div>
      </div>

      <label class="flex items-center gap-2 text-sm text-gray-700">
        <input v-model="form.burn_after_read" type="checkbox" class="rounded border-gray-300" />
        Burn after reading (delete once viewed)
      </label>

      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

      <div class="flex gap-2">
        <button
          :disabled="loading"
          class="rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50"
          @click="save"
        >
          {{ loading ? 'Saving…' : isEdit ? 'Save changes' : 'Create snippet' }}
        </button>
        <router-link
          v-if="isEdit"
          :to="{ name: 'View', params: { name: editName } }"
          class="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100"
        >
          Cancel
        </router-link>
      </div>
    </div>

    <ShareDialog v-if="created" :snippet="created" @close="created = null" />
  </div>
</template>
