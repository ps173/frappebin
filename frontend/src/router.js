import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'New',
    component: () => import('@/pages/Editor.vue'),
  },
  {
    path: '/mine',
    name: 'Mine',
    component: () => import('@/pages/Mine.vue'),
  },
  {
    path: '/:name/edit',
    name: 'Edit',
    component: () => import('@/pages/Editor.vue'),
    props: true,
  },
  {
    path: '/:name',
    name: 'View',
    component: () => import('@/pages/View.vue'),
    props: true,
  },
]

let router = createRouter({
  history: createWebHistory('/frappebin'),
  routes,
})

export default router
