import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/auth',
    component: () => import('layouts/AuthLayout.vue'),
    children: [
      { path: 'login', name: 'login', component: () => import('pages/auth/LoginPage.vue') },
      { path: 'register', name: 'register', component: () => import('pages/auth/RegisterPage.vue') },
    ],
  },
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', redirect: { name: 'discover' } },
      { path: 'discover', name: 'discover', component: () => import('pages/discover/DiscoverPage.vue'), meta: { requiresAuth: true } },
      { path: 'media/:id', name: 'media-detail', component: () => import('pages/media/MediaDetailPage.vue'), meta: { requiresAuth: true } },
      { path: 'list', name: 'my-list', component: () => import('pages/tracking/MyListPage.vue'), meta: { requiresAuth: true } },
      { path: 'airing-calendar', name: 'airing-calendar', component: () => import('pages/tracking/AiringCalendarPage.vue'), meta: { requiresAuth: true } },
      { path: 'import-list', name: 'import-list', component: () => import('pages/tracking/ImportListPage.vue'), meta: { requiresAuth: true } },
      { path: 'feed', name: 'feed', component: () => import('pages/social/FeedPage.vue'), meta: { requiresAuth: true } },
      { path: 'recommendations', name: 'recommendations', component: () => import('pages/social/RecommendationsPage.vue'), meta: { requiresAuth: true } },
      { path: 'discussions', name: 'discussions', component: () => import('pages/social/DiscussionPage.vue'), meta: { requiresAuth: true } },
      { path: 'watchparty', name: 'watchparty', component: () => import('pages/watchparty/WatchPartyPage.vue'), meta: { requiresAuth: true } },
      { path: 'notifications', name: 'notifications', component: () => import('pages/notifications/NotificationsPage.vue'), meta: { requiresAuth: true } },
      { path: 'profile', name: 'profile', component: () => import('pages/profile/ProfilePage.vue'), meta: { requiresAuth: true } },
    ],
  },
  {
    path: '/:catchAll(.*)*',
    name: 'not-found',
    component: () => import('pages/discover/DiscoverPage.vue'),
  },
]

export default routes
