<template>
  <div class="min-h-screen bg-gradient-to-br from-secondary-50 to-primary-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden">
      <div class="bg-gradient-to-r from-primary-500 to-primary-600 p-6 text-center">
        <h1 class="text-2xl font-bold text-white">文件收集系统</h1>
        <p class="text-primary-100 mt-1">管理员登录</p>
      </div>

      <div class="p-8">
        <form @submit.prevent="login" class="space-y-6">
          <div>
            <label for="username" class="block text-sm font-medium text-secondary-700 mb-2">
              用户名 <span class="text-red-500">*</span>
            </label>
            <input id="username" v-model="credentials.username" type="text" required :disabled="loggingIn"
              class="w-full px-4 py-3 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors disabled:bg-secondary-100"
              placeholder="请输入用户名" />
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-secondary-700 mb-2">
              密码 <span class="text-red-500">*</span>
            </label>
            <input id="password" v-model="credentials.password" type="password" required :disabled="loggingIn"
              class="w-full px-4 py-3 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors disabled:bg-secondary-100"
              placeholder="请输入密码" />
          </div>

          <div v-if="errorMessage" class="rounded-lg bg-red-50 border border-red-200 p-3">
            <p class="text-sm text-red-800">{{ errorMessage }}</p>
          </div>

          <button type="submit" :disabled="!credentials.username || !credentials.password || loggingIn"
            class="w-full px-4 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-secondary-300 disabled:cursor-not-allowed transition-colors font-medium flex items-center justify-center">
            <svg v-if="loggingIn" class="animate-spin h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
              </path>
            </svg>
            <span>{{ loggingIn ? '登录中...' : '登录' }}</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// 状态管理
const loggingIn = ref(false)
const errorMessage = ref('')

// 登录凭据
const credentials = reactive({
  username: '',
  password: ''
})

// 登录函数
const login = async () => {
  if (!credentials.username || !credentials.password) {
    return
  }

  loggingIn.value = true
  errorMessage.value = ''

  try {
    // 将凭据存储到localStorage中用于API请求
    const token = btoa(`${credentials.username}:${credentials.password}`)
    localStorage.setItem('admin_token', token)

    // 验证凭据
    await axios.get('http://localhost:8000/api/auth/check', {
      headers: {
        'Authorization': `Basic ${token}`
      }
    })

    // 登录成功，跳转到管理页面
    router.push('/admin')
  } catch (error: any) {
    // 登录失败
    localStorage.removeItem('admin_token')
    errorMessage.value = error.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loggingIn.value = false
  }
}
</script>