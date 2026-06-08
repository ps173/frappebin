<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  // { name, secret_key, edit_token, visibility }
  snippet: { type: Object, required: true },
})
const emit = defineEmits(['close'])
const router = useRouter()

const origin = window.location.origin
const base = `${origin}/frontend`

// Public snippets need no key; Unlisted/Private require the secret key in the link.
const shareUrl = computed(() => {
  const { name, secret_key, visibility } = props.snippet
  if (visibility === 'Public') return `${base}/${name}`
  return `${base}/${name}?key=${secret_key}`
})

const copied = ref(false)
async function copyLink() {
  await navigator.clipboard.writeText(shareUrl.value)
  copied.value = true
  setTimeout(() => (copied.value = false), 1500)
}

function viewSnippet() {
  const { name, secret_key, visibility } = props.snippet
  const query = visibility === 'Public' ? {} : { key: secret_key }
  router.push({ name: 'View', params: { name }, query })
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" @click.self="emit('close')">
    <div class="w-full max-w-lg rounded-lg bg-white p-6 shadow-xl">
      <h2 class="text-lg font-semibold">Snippet created 🎉</h2>
      <p class="mt-1 text-sm text-gray-600">
        Visibility: <span class="font-medium">{{ snippet.visibility }}</span>
      </p>

      <label class="mt-4 block text-sm font-medium text-gray-700">Share link</label>
      <div class="mt-1 flex gap-2">
        <input
          :value="shareUrl"
          readonly
          class="w-full rounded-md border border-gray-300 px-3 py-2 font-mono text-xs"
        />
        <button
          class="shrink-0 rounded-md bg-gray-900 px-3 py-2 text-sm font-medium text-white hover:bg-gray-800"
          @click="copyLink"
        >
          {{ copied ? 'Copied!' : 'Copy' }}
        </button>
      </div>
      <p v-if="snippet.visibility !== 'Public'" class="mt-2 text-xs text-amber-600">
        This link contains the secret key — anyone with it can view the snippet.
      </p>

      <div class="mt-6 flex justify-end gap-2">
        <button
          class="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100"
          @click="emit('close')"
        >
          Create another
        </button>
        <button
          class="rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
          @click="viewSnippet"
        >
          View snippet
        </button>
      </div>
    </div>
  </div>
</template>
