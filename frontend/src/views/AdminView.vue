<template>
  <div class="min-h-screen bg-secondary-50">
    <!-- 添加加载提示 -->
    <div v-if="isLoading" class="fixed top-4 right-4 z-50">
      <div class="bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded relative" role="alert">
        <strong class="font-bold">正在处理... </strong>
        <span class="block sm:inline">{{ loadingMessage }}</span>
      </div>
    </div>
    
    <!-- Header -->
    <div class="bg-white shadow-sm border-b border-secondary-200">
      <div class="max-w-7xl mx-auto px-4 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-secondary-900">管理后台</h1>
            <p class="text-secondary-600 mt-1">文件收集任务管理</p>
          </div>
          <div class="flex items-center space-x-4">
            <button
              @click="logout"
              class="inline-flex items-center px-4 py-2 border border-secondary-300 rounded-lg text-secondary-700 bg-white hover:bg-secondary-50 transition-colors font-medium"
            >
              退出登录
            </button>
            <button
              @click="showSettingsModal = true"
              class="inline-flex items-center px-4 py-2 border border-secondary-300 rounded-lg text-secondary-700 bg-white hover:bg-secondary-50 transition-colors font-medium"
            >
              设置
            </button>
            <button
              @click="showCreateModal = true"
              class="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
              </svg>
              创建任务
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 py-8">
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow-md p-6 border border-secondary-200">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                <svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                </svg>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-secondary-600">总任务数</p>
              <p class="text-2xl font-semibold text-secondary-900">{{ tasks.length }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-md p-6 border border-secondary-200">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-secondary-600">活跃任务</p>
              <p class="text-2xl font-semibold text-secondary-900">{{ activeTasks.length }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-md p-6 border border-secondary-200">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                </svg>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-secondary-600">总上传文件</p>
              <p class="text-2xl font-semibold text-secondary-900">{{ totalFiles }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tasks Table -->
      <div class="bg-white rounded-lg shadow-md border border-secondary-200 overflow-hidden">
        <div class="px-6 py-4 bg-secondary-50 border-b border-secondary-200">
          <h2 class="text-lg font-semibold text-secondary-900">任务列表</h2>
        </div>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-secondary-200">
            <thead class="bg-secondary-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">任务信息</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">状态</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">文件数量</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">创建时间</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-secondary-200">
              <tr v-for="task in tasks" :key="task.id" class="hover:bg-secondary-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div class="text-sm font-medium text-secondary-900">{{ task.name }}</div>
                    <div v-if="task.description" class="text-sm text-secondary-500">{{ task.description }}</div>
                    <div class="text-xs text-secondary-400 mt-1">ID: {{ task.id }}</div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" 
                        :class="getStatusClass(task.status)">
                    {{ getStatusText(task.status) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-secondary-900">
                  {{ task.uploaded_files_count || 0 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-secondary-500">
                  {{ formatDate(task.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                  <button
                    @click="copyUploadLink(task.id)"
                    class="text-primary-600 hover:text-primary-900 transition-colors"
                    title="复制上传链接"
                  >
                    复制链接
                  </button>
                  <button
                    @click="viewFiles(task)"
                    class="text-blue-600 hover:text-blue-900 transition-colors"
                    title="查看文件"
                  >
                    查看文件
                  </button>
                  <button
                    @click="toggleTaskStatus(task)"
                    class="transition-colors"
                    :class="task.status === 'active' ? 'text-orange-600 hover:text-orange-900' : 'text-green-600 hover:text-green-900'"
                  >
                    {{ task.status === 'active' ? '关闭' : '激活' }}
                  </button>
                  <button
                    @click="deleteTask(task)"
                    class="text-red-600 hover:text-red-900 transition-colors"
                    title="删除任务"
                  >
                    删除
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="tasks.length === 0" class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-secondary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
          </svg>
          <h3 class="mt-2 text-sm font-medium text-secondary-900">暂无任务</h3>
          <p class="mt-1 text-sm text-secondary-500">开始创建您的第一个文件收集任务</p>
        </div>
      </div>
    </div>

    <!-- Create Task Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-secondary-600 bg-opacity-50 overflow-y-auto z-50">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center">
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all max-w-lg w-full">
          <div class="bg-white px-6 pt-5 pb-4">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-medium text-secondary-900">创建新任务</h3>
              <button @click="showCreateModal = false" class="text-secondary-400 hover:text-secondary-600">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
            
            <form @submit.prevent="createTask" class="space-y-4">
              <div>
                <label for="taskName" class="block text-sm font-medium text-secondary-700 mb-2">
                  任务名称 <span class="text-red-500">*</span>
                </label>
                <input
                  id="taskName"
                  v-model="newTask.name"
                  type="text"
                  required
                  class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="输入任务名称"
                />
              </div>
              
              <div>
                <label for="taskDescription" class="block text-sm font-medium text-secondary-700 mb-2">
                  任务描述
                </label>
                <textarea
                  id="taskDescription"
                  v-model="newTask.description"
                  rows="3"
                  class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  placeholder="输入任务描述（可选）"
                ></textarea>
              </div>
            </form>
          </div>
          
          <div class="bg-secondary-50 px-6 py-3 flex justify-end space-x-3">
            <button
              @click="showCreateModal = false"
              type="button"
              class="px-4 py-2 border border-secondary-300 text-secondary-700 rounded-md hover:bg-secondary-50 transition-colors"
            >
              取消
            </button>
            <button
              @click="createTask"
              :disabled="!newTask.name || creating"
              class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:bg-secondary-300 disabled:cursor-not-allowed transition-colors"
            >
              {{ creating ? '创建中...' : '创建任务' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Files Modal -->
    <div v-if="showFilesModal" class="fixed inset-0 bg-secondary-600 bg-opacity-50 overflow-y-auto z-50">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center">
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all max-w-4xl w-full">
          <div class="bg-white px-6 pt-5 pb-4">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-medium text-secondary-900">任务文件 - {{ selectedTask?.name }}</h3>
              <button @click="showFilesModal = false" class="text-secondary-400 hover:text-secondary-600">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
            
            <div v-if="taskFiles.length > 0" class="max-h-96 overflow-y-auto">
              <div class="space-y-2">
                <div
                  v-for="file in taskFiles"
                  :key="file.filename + file.uploader_name"
                  class="flex items-center justify-between p-3 bg-secondary-50 rounded-lg border border-secondary-200"
                >
                  <div class="flex items-center space-x-3">
                    <svg class="h-5 w-5 text-secondary-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd" />
                    </svg>
                    <div>
                      <p class="text-sm font-medium text-secondary-900">{{ file.filename }}</p>
                      <p class="text-xs text-secondary-500">上传者: {{ file.uploader_name }} | {{ formatFileSize(file.size) }}</p>
                    </div>
                  </div>
                  <div class="text-xs text-secondary-500">
                    {{ formatDate(file.upload_time) }}
                  </div>
                </div>
              </div>
            </div>
            
            <div v-else class="text-center py-8">
              <p class="text-secondary-500">暂无上传文件</p>
            </div>
          </div>
          
          <div class="bg-secondary-50 px-6 py-3 flex justify-end space-x-3">
            <button
              v-if="taskFiles.length > 0"
              @click="downloadAllFiles"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
            >
              批量下载
            </button>
            <button
              @click="showFilesModal = false"
              class="px-4 py-2 border border-secondary-300 text-secondary-700 rounded-md hover:bg-secondary-50 transition-colors"
            >
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Settings Modal -->
    <div v-if="showSettingsModal" class="fixed inset-0 bg-secondary-600 bg-opacity-50 overflow-y-auto z-50">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center">
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all max-w-lg w-full">
          <div class="bg-white px-6 pt-5 pb-4">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-medium text-secondary-900">系统设置</h3>
              <button @click="showSettingsModal = false" class="text-secondary-400 hover:text-secondary-600">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
            
            <form @submit.prevent="saveSettings" class="space-y-6">
              <div>
                <h4 class="text-md font-medium text-secondary-800 mb-3">管理员密码设置</h4>
                <div class="space-y-3">
                  <div>
                    <label for="currentPassword" class="block text-sm font-medium text-secondary-700 mb-1">
                      当前密码
                    </label>
                    <input
                      id="currentPassword"
                      v-model="settings.currentPassword"
                      type="password"
                      class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      placeholder="请输入当前密码"
                    />
                  </div>
                  
                  <div>
                    <label for="newPassword" class="block text-sm font-medium text-secondary-700 mb-1">
                      新密码
                    </label>
                    <input
                      id="newPassword"
                      v-model="settings.newPassword"
                      type="password"
                      class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      placeholder="请输入新密码"
                    />
                  </div>
                  
                  <div>
                    <label for="confirmPassword" class="block text-sm font-medium text-secondary-700 mb-1">
                      确认新密码
                    </label>
                    <input
                      id="confirmPassword"
                      v-model="settings.confirmPassword"
                      type="password"
                      class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      placeholder="请再次输入新密码"
                    />
                  </div>
                </div>
              </div>
              
              <div>
                <h4 class="text-md font-medium text-secondary-800 mb-3">上传限制设置</h4>
                <div class="space-y-3">
                  <div>
                    <label for="maxFileSize" class="block text-sm font-medium text-secondary-700 mb-1">
                      单文件大小限制 (MB)
                    </label>
                    <input
                      id="maxFileSize"
                      v-model.number="settings.maxFileSize"
                      type="number"
                      min="0"
                      class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      placeholder="例如: 100"
                    />
                    <p class="text-xs text-secondary-500 mt-1">设置为0表示无限制</p>
                  </div>
                  
                  <div>
                    <label for="maxFilesPerUpload" class="block text-sm font-medium text-secondary-700 mb-1">
                      单次上传文件数量限制
                    </label>
                    <input
                      id="maxFilesPerUpload"
                      v-model.number="settings.maxFilesPerUpload"
                      type="number"
                      min="0"
                      class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      placeholder="例如: 10"
                    />
                    <p class="text-xs text-secondary-500 mt-1">设置为0表示无限制</p>
                  </div>
                </div>
              </div>
              
              <div>
                <h4 class="text-md font-medium text-secondary-800 mb-3">错误限制设置</h4>
                <div class="space-y-3">
                  <div>
                    <label for="maxUploadErrors" class="block text-sm font-medium text-secondary-700 mb-1">
                      最大上传错误数
                    </label>
                    <input
                      id="maxUploadErrors"
                      v-model.number="settings.maxUploadErrors"
                      type="number"
                      min="0"
                      class="w-full px-3 py-2 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      placeholder="例如: 5"
                    />
                    <p class="text-xs text-secondary-500 mt-1">设置为0表示无限制</p>
                  </div>
                </div>
              </div>
            </form>
          </div>
          
          <div class="bg-secondary-50 px-6 py-3 flex justify-end space-x-3">
            <button
              @click="showSettingsModal = false"
              type="button"
              class="px-4 py-2 border border-secondary-300 text-secondary-700 rounded-md hover:bg-secondary-50 transition-colors"
            >
              取消
            </button>
            <button
              @click="saveSettings"
              :disabled="savingSettings"
              class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:bg-secondary-300 disabled:cursor-not-allowed transition-colors"
            >
              {{ savingSettings ? '保存中...' : '保存设置' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="successMessage" class="fixed top-4 right-4 bg-green-50 border border-green-200 rounded-lg p-4 shadow-lg z-50">
      <div class="flex items-center">
        <svg class="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <p class="ml-3 text-sm font-medium text-green-800">{{ successMessage }}</p>
      </div>
    </div>

    <div v-if="errorMessage" class="fixed top-4 right-4 bg-red-50 border border-red-200 rounded-lg p-4 shadow-lg z-50">
      <div class="flex items-center">
        <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
        <p class="ml-3 text-sm font-medium text-red-800">{{ errorMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { message } from 'ant-design-vue';

// Router
const router = useRouter()

// Reactive data
const tasks = ref<any[]>([])
const showCreateModal = ref(false)
const showFilesModal = ref(false)
const showSettingsModal = ref(false)
const creating = ref(false)
const savingSettings = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const selectedTask = ref<any>(null)
const taskFiles = ref<any[]>([])

// 添加加载提示相关的状态
const loadingMessage = ref('')
const isLoading = ref(false)

const newTask = ref({
  name: '',
  description: ''
})

const settings = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
  maxFileSize: 0,
  maxFilesPerUpload: 0,
  maxUploadErrors: 0
})

// API base URL
const API_BASE = 'http://localhost:8000/api'

// Computed properties
const activeTasks = computed(() => tasks.value.filter(task => task.status === 'active'))
const totalFiles = computed(() => tasks.value.reduce((total, task) => total + (task.uploaded_files_count || 0), 0))

// Load tasks on mount
onMounted(() => {
  loadTasks()
  loadSettings()
})

// 登出功能
const logout = () => {
  localStorage.removeItem('admin_token')
  router.push('/login')
}

const loadTasks = async () => {
  try {
    const token = localStorage.getItem('admin_token')
    const response = await axios.get(`${API_BASE}/tasks/`, {
      headers: {
        'Authorization': `Basic ${token}`
      }
    })
    tasks.value = response.data
  } catch (error: any) {
    if (error.response?.status === 401) {
      // 未授权，跳转到登录页
      localStorage.removeItem('admin_token')
      router.push('/login')
    } else {
      showError('加载任务列表失败')
    }
  }
}

const loadSettings = async () => {
  try {
    const token = localStorage.getItem('admin_token')
    const response = await axios.get(`${API_BASE}/settings`, {
      headers: {
        'Authorization': `Basic ${token}`
      }
    })
    
    const data = response.data
    settings.value.maxFileSize = data.max_file_size || 0
    settings.value.maxFilesPerUpload = data.max_files_per_upload || 0
    settings.value.maxUploadErrors = data.max_upload_errors || 0
  } catch (error: any) {
    if (error.response?.status === 401) {
      // 未授权，跳转到登录页
      localStorage.removeItem('admin_token')
      router.push('/login')
    } else {
      // 不显示错误，使用默认值
      console.warn('加载设置失败:', error)
    }
  }
}

const createTask = async () => {
  if (!newTask.value.name.trim()) return

  creating.value = true
  try {
    const token = localStorage.getItem('admin_token')
    await axios.post(`${API_BASE}/tasks/`, {
      name: newTask.value.name.trim(),
      description: newTask.value.description.trim() || null
    }, {
      headers: {
        'Authorization': `Basic ${token}`
      }
    })

    showSuccess('任务创建成功')
    showCreateModal.value = false
    newTask.value = { name: '', description: '' }
    await loadTasks()
  } catch (error: any) {
    if (error.response?.status === 401) {
      // 未授权，跳转到登录页
      localStorage.removeItem('admin_token')
      router.push('/login')
    } else {
      showError(error.response?.data?.detail || '创建任务失败')
    }
  } finally {
    creating.value = false
  }
}

const toggleTaskStatus = async (task: any) => {
  const newStatus = task.status === 'active' ? 'inactive' : 'active'
  
  try {
    const token = localStorage.getItem('admin_token')
    await axios.put(`${API_BASE}/tasks/${task.id}/status?status=${newStatus}`, {}, {
      headers: {
        'Authorization': `Basic ${token}`
      }
    })
    showSuccess(`任务已${newStatus === 'active' ? '激活' : '关闭'}`)
    await loadTasks()
  } catch (error: any) {
    if (error.response?.status === 401) {
      // 未授权，跳转到登录页
      localStorage.removeItem('admin_token')
      router.push('/login')
    } else {
      showError('更新任务状态失败')
    }
  }
}

const deleteTask = async (task: any) => {
  if (!confirm(`确定要删除任务"${task.name}"吗？此操作不可撤销。`)) return

  try {
    const token = localStorage.getItem('admin_token')
    await axios.delete(`${API_BASE}/tasks/${task.id}`, {
      headers: {
        'Authorization': `Basic ${token}`
      }
    })
    showSuccess('任务删除成功')
    await loadTasks()
  } catch (error: any) {
    if (error.response?.status === 401) {
      // 未授权，跳转到登录页
      localStorage.removeItem('admin_token')
      router.push('/login')
    } else {
      showError('删除任务失败')
    }
  }
}

const copyUploadLink = async (taskId: string) => {
  const link = `${window.location.origin}/upload/${taskId}`
  
  try {
    await navigator.clipboard.writeText(link)
    showSuccess('上传链接已复制到剪贴板')
  } catch (error) {
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = link
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    showSuccess('上传链接已复制到剪贴板')
  }
}

const viewFiles = async (task: any) => {
  selectedTask.value = task
  showFilesModal.value = true
  
  try {
    const token = localStorage.getItem('admin_token')
    const response = await axios.get(`${API_BASE}/upload/${task.id}/files`, {
      headers: {
        'Authorization': `Basic ${token}`
      }
    })
    taskFiles.value = response.data.files || []
  } catch (error: any) {
    if (error.response?.status === 401) {
      // 未授权，跳转到登录页
      localStorage.removeItem('admin_token')
      router.push('/login')
    } else {
      showError('加载文件列表失败')
      taskFiles.value = []
    }
  }
}

const downloadAllFiles = async () => {
  // 显示确认对话框，询问是否清理已下载的文件
  const shouldDownload = confirm("是否要下载所有文件？\n点击\"确定\"开始下载，点击\"取消\"放弃下载。");
  if (!shouldDownload) return;

  const cleanAfterDownload = confirm("下载完成后是否要清理已下载的文件？\n注意：这将永久删除服务器上的文件，请谨慎操作！\n点击\"确定\"表示清理，点击\"取消\"表示保留文件。");

  try {
    showLoading('正在准备下载...');
    
    const token = localStorage.getItem('admin_token')
    const response = await axios.get(`${API_BASE}/upload/${selectedTask.value.id}/download-all?clean=${cleanAfterDownload}`, {
      headers: {
        'Authorization': `Basic ${token}`
      },
      responseType: 'blob'
    })
    
    hideLoading();
    showLoading('正在下载文件...');

    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `task_${selectedTask.value.id}_files.zip`)
    document.body.appendChild(link)
    link.click()
    
    // 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    hideLoading();
    if (cleanAfterDownload) {
      showSuccess('文件打包下载成功，已清理服务器上的文件')
    } else {
      showSuccess('文件打包下载成功')
    }
  } catch (error: any) {
    hideLoading();
    if (error.response?.status === 401) {
      // 未授权，跳转到登录页
      localStorage.removeItem('admin_token')
      router.push('/login')
    } else {
      showError('批量下载失败: ' + (error.response?.data?.detail || '未知错误'))
    }
  }
}

const saveSettings = async () => {
  // 验证密码设置
  if (settings.value.newPassword && settings.value.newPassword !== settings.value.confirmPassword) {
    showError('新密码和确认密码不匹配')
    return
  }

  savingSettings.value = true
  try {
    const token = localStorage.getItem('admin_token')
    
    // 如果提供了新密码，则更新密码
    if (settings.value.newPassword) {
      await axios.put(`${API_BASE}/settings/password`, {
        current_password: settings.value.currentPassword,
        new_password: settings.value.newPassword
      }, {
        headers: {
          'Authorization': `Basic ${token}`
        }
      })
    }
    
    // 更新其他设置
    const response = await axios.put(`${API_BASE}/settings`, {
      max_file_size: settings.value.maxFileSize,
      max_files_per_upload: settings.value.maxFilesPerUpload,
      max_upload_errors: settings.value.maxUploadErrors
    }, {
      headers: {
        'Authorization': `Basic ${token}`
      }
    })
    
    // 更新本地设置值
    settings.value.maxFileSize = response.data.max_file_size || 0
    settings.value.maxFilesPerUpload = response.data.max_files_per_upload || 0
    settings.value.maxUploadErrors = response.data.max_upload_errors || 0
    
    showSuccess('设置保存成功')
    showSettingsModal.value = false
    
    // 重置密码字段
    settings.value.currentPassword = ''
    settings.value.newPassword = ''
    settings.value.confirmPassword = ''
  } catch (error: any) {
    if (error.response?.status === 401) {
      // 未授权，跳转到登录页
      localStorage.removeItem('admin_token')
      router.push('/login')
    } else if (error.response?.status === 400 && error.response?.data?.detail === "当前密码错误") {
      showError('当前密码错误，请重新输入')
    } else {
      showError(error.response?.data?.detail || '保存设置失败')
    }
  } finally {
    savingSettings.value = false
  }
}

// Utility functions
const getStatusClass = (status: string) => {
  switch (status) {
    case 'active':
      return 'bg-green-100 text-green-800'
    case 'inactive':
      return 'bg-orange-100 text-orange-800'
    case 'completed':
      return 'bg-blue-100 text-blue-800'
    default:
      return 'bg-secondary-100 text-secondary-800'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'active':
      return '开放上传'
    case 'inactive':
      return '已关闭'
    case 'completed':
      return '已完成'
    default:
      return '未知状态'
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 添加加载提示相关的方法
const showLoading = (message: string) => {
  loadingMessage.value = message
  isLoading.value = true
}

const hideLoading = () => {
  isLoading.value = false
  loadingMessage.value = ''
}

const showSuccess = (messageText: string) => {
  message.success(messageText)
}

const showError = (messageText: string) => {
  message.error(messageText)
}

// 在页面中找到notification部分，在其下方添加loading显示
</script>
