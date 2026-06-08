<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <header class="border-b border-gray-200 bg-white">
      <div class="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <router-link to="/" class="flex items-center gap-2 font-semibold">
          <span class="text-lg">📋 Frappebin</span>
        </router-link>
        <nav class="flex items-center gap-2">
          <router-link
            to="/"
            class="rounded-md px-3 py-1.5 text-sm font-medium text-gray-600 hover:bg-gray-100"
          >
            New
          </router-link>
          <router-link
            to="/mine"
            class="rounded-md px-3 py-1.5 text-sm font-medium text-gray-600 hover:bg-gray-100"
          >
            My Snippets
          </router-link>
        </nav>
      </div>
    </header>

    <main class="mx-auto max-w-5xl px-4 py-6">
      <router-view />
    </main>
  </div>
</template>
