<script setup>
import { ref, onMounted } from 'vue'
import { listMySnippets, forgetSnippet } from '@/lib/tokens'

const snippets = ref([])

onMounted(() => {
  snippets.value = listMySnippets()
})

function linkFor(s) {
  return s.visibility === 'Public' ? { name: 'View', params: { name: s.name } }
    : { name: 'View', params: { name: s.name }, query: { key: s.secret_key } }
}

function forget(name) {
  forgetSnippet(name)
  snippets.value = listMySnippets()
}
</script>

<template>
  <div>
    <h1 class="mb-1 text-xl font-semibold">My snippets</h1>
    <p class="mb-4 text-sm text-gray-500">
      Snippets you created on this device. Stored locally in your browser — clearing site data forgets them.
    </p>

    <div v-if="!snippets.length" class="rounded-lg border border-dashed border-gray-300 p-8 text-center">
      <p class="text-sm text-gray-500">No snippets yet.</p>
      <router-link to="/" class="mt-2 inline-block text-sm font-medium text-gray-900 underline">
        Create your first snippet
      </router-link>
    </div>

    <ul v-else class="divide-y divide-gray-200 overflow-hidden rounded-lg border border-gray-200 bg-white">
      <li v-for="s in snippets" :key="s.name" class="flex items-center justify-between px-4 py-3">
        <div class="min-w-0">
          <router-link :to="linkFor(s)" class="block truncate font-medium text-gray-900 hover:underline">
            {{ s.title || 'Untitled' }}
          </router-link>
          <div class="mt-0.5 flex items-center gap-2 text-xs text-gray-500">
            <span class="rounded bg-gray-100 px-1.5 py-0.5">{{ s.visibility }}</span>
            <span class="font-mono">{{ s.name }}</span>
          </div>
        </div>
        <button class="text-xs text-gray-400 hover:text-red-600" @click="forget(s.name)">
          Remove from list
        </button>
      </li>
    </ul>
  </div>
</template>
