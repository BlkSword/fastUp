import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

// Import views
import UploadView from './views/UploadView.vue'
import AdminView from './views/AdminView.vue'
import LoginView from './views/LoginView.vue'

const routes = [
  { path: '/', redirect: '/upload' },
  { path: '/upload', component: UploadView },
  { path: '/upload/:taskId', component: UploadView, props: true },
  { path: '/admin', component: AdminView },
  { path: '/login', component: LoginView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 添加路由守卫
router.beforeEach((to, from, next) => {
  // 检查是否访问管理页面
  if (to.path === '/admin') {
    // 检查是否有认证令牌
    const token = localStorage.getItem('admin_token')
    if (token) {
      // 有令牌，允许访问
      next()
    } else {
      // 无令牌，重定向到登录页
      next('/login')
    }
  } else {
    // 访问非管理页面，直接通过
    next()
  }
})

const app = createApp(App)
app.use(router)
app.mount('#app')