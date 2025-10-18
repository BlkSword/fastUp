<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6">
    <div class="max-w-3xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-10">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-indigo-100 mb-4">
          <svg class="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
          </svg>
        </div>
        <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ taskInfo?.task_name || '文件上传' }}</h1>
        <p class="text-gray-600">{{ taskInfo?.description || '请上传您的文件' }}</p>
        <div v-if="taskInfo" class="mt-4 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
          :class="getStatusClass(taskInfo.status)">
          {{ getStatusText(taskInfo.status) }}
        </div>
      </div>

      <!-- Upload Card -->
      <div class="bg-white rounded-2xl shadow-xl overflow-hidden">
        <div class="px-6 py-5 border-b border-gray-200">
          <h2 class="text-lg font-semibold text-gray-900">上传文件</h2>
        </div>

        <div class="p-6">
          <form @submit.prevent="uploadFiles" v-if="taskInfo?.status === 'active'">
            <!-- Name Input -->
            <div class="mb-6">
              <label for="uploaderName" class="block text-sm font-medium text-gray-700 mb-2">
                您的姓名 <span class="text-red-500">*</span>
              </label>
              <input id="uploaderName" v-model="uploaderName" type="text" required :disabled="uploading"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors disabled:bg-gray-100"
                placeholder="请输入您的姓名" />
            </div>

            <!-- File Drop Zone -->
            <div class="mb-6">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                选择文件 <span class="text-red-500">*</span>
              </label>
              <div @dragover.prevent @dragenter.prevent @drop="handleDrop"
                class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer transition-colors hover:border-indigo-400 hover:bg-indigo-50"
                :class="{ 'bg-gray-50': uploading }">
                <input ref="fileInput" type="file" multiple @change="handleFileSelect" class="hidden"
                  :disabled="uploading" />
                <div @click="fileInput?.click()" class="space-y-2">
                  <div class="flex justify-center">
                    <svg class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12">
                      </path>
                    </svg>
                  </div>
                  <p class="text-gray-600">
                    <span class="font-medium text-indigo-600">点击选择文件</span> 或拖拽文件到此处
                  </p>
                  <p class="text-sm text-gray-500">支持多个文件同时上传</p>
                </div>
              </div>
            </div>

            <!-- Selected Files -->
            <div v-if="selectedFiles.length > 0" class="mb-6">
              <h3 class="text-sm font-medium text-gray-700 mb-3">已选择 {{ selectedFiles.length }} 个文件:</h3>
              <div class="space-y-2 max-h-60 overflow-y-auto">
                <div v-for="(file, index) in selectedFiles" :key="index"
                  class="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <div class="flex items-center space-x-3">
                    <svg class="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd"
                        d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"
                        clip-rule="evenodd" />
                    </svg>
                    <div>
                      <p class="text-sm font-medium text-gray-900 truncate max-w-xs">{{ file.name }}</p>
                      <p class="text-xs text-gray-500">{{ formatFileSize(file.size) }}</p>
                    </div>
                  </div>
                  <button type="button" @click="removeFile(index)" :disabled="uploading"
                    class="text-gray-400 hover:text-red-500 transition-colors disabled:opacity-50">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12">
                      </path>
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- Upload Button -->
            <div class="flex justify-end">
              <button
                type="submit"
                :disabled="!uploaderName.trim() || selectedFiles.length === 0 || uploading"
                class="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium flex items-center"
              >
                <svg v-if="uploading" class="animate-spin h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>{{ uploading ? '上传中...' : '上传文件' }}</span>
              </button>
            </div>

            <!-- Progress Bar -->
            <div v-if="uploading" class="mt-6">
              <a-progress 
                :percent="uploadProgress" 
                :status="uploadProgress < 100 ? 'active' : 'success'"
                :show-info="true"
              />
              <div class="mt-2 text-sm text-gray-600">
                <span v-if="uploadSpeed">速度: {{ formatSpeed(uploadSpeed) }}</span>
                <span v-if="uploadSpeed && timeRemaining"> | </span>
                <span v-if="timeRemaining">剩余时间: {{ formatTime(timeRemaining) }}</span>
              </div>
            </div>
          </form>

          <!-- Task Inactive Message -->
          <div v-else-if="taskInfo?.status === 'inactive'" class="text-center py-10">
            <a-alert message="任务已关闭" description="该文件收集任务已关闭，暂时无法上传文件。" type="warning" show-icon />
          </div>

          <!-- Task Not Found Message -->
          <div v-else-if="taskNotFound" class="text-center py-10">
            <a-alert message="任务不存在" description="找不到指定的文件收集任务。" type="error" show-icon />
          </div>

          <!-- Loading State -->
          <div v-else class="text-center py-10">
            <svg class="animate-spin h-10 w-10 text-indigo-600 mx-auto" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
              </path>
            </svg>
            <p class="mt-3 text-gray-500">正在加载任务信息...</p>
          </div>
        </div>
      </div>

      <!-- Success Message -->
      <div v-if="uploadSuccess" class="mt-6">
        <a-alert message="上传成功" description="您的文件已成功上传！" type="success" show-icon closable
          @close="() => { uploadSuccess = false }" />
      </div>

      <!-- Error Message -->
      <div v-if="uploadError && showError" class="mt-6">
        <a-alert :message="uploadError" type="error" show-icon closable @close="hideErrorMessage" />
      </div>

      <!-- Limit Info -->
      <div v-if="limitInfo" class="mt-6">
        <a-alert message="上传限制" type="info" show-icon>
          <template #description>
            <ul class="list-disc pl-5 space-y-1">
              <li v-if="limitInfo.max_file_size">单文件大小限制: {{ limitInfo.max_file_size }}MB</li>
              <li v-if="limitInfo.max_files_per_upload">单次上传文件数量限制: {{ limitInfo.max_files_per_upload }}个</li>
              <li v-if="limitInfo.max_upload_errors">最大上传错误数: {{ limitInfo.max_upload_errors }}</li>
            </ul>
          </template>
        </a-alert>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { Alert, Progress } from 'ant-design-vue';

// Route and router
const route = useRoute()
const router = useRouter()

// Reactive data
const taskInfo = ref<any>(null)
const taskNotFound = ref(false)
const uploaderName = ref('')
const selectedFiles = ref<File[]>([])
const uploading = ref(false)
const uploadSuccess = ref(false)
const uploadError = ref('')
const limitInfo = ref<any>(null)
const fileInput = ref<HTMLInputElement | null>(null)

// Components
const AAlert = Alert;
const AProgress = Progress; // 添加这一行

// 添加进度相关数据
const uploadProgress = ref(0)
const uploadSpeed = ref(0) // bytes per second
const timeRemaining = ref(0) // seconds

// 错误消息显示控制
const showError = ref(false)
const hideErrorMessage = () => {
  uploadError.value = ''
  showError.value = false
}

// API base URL
const API_BASE = 'http://localhost:8000/api'

// Load task info on mount
onMounted(() => {
  loadTaskInfo()
  loadLimitInfo()
})

const loadTaskInfo = async () => {
  try {
    const response = await axios.get(`${API_BASE}/tasks/${route.params.taskId}/info`)
    taskInfo.value = response.data
  } catch (error: any) {
    if (error.response?.status === 404) {
      taskNotFound.value = true
    } else {
      console.error('加载任务信息失败:', error)
    }
  }
}

const loadLimitInfo = async () => {
  try {
    // 尝试获取系统设置信息（公开接口）
    const response = await axios.get(`${API_BASE}/settings/public`)
    limitInfo.value = response.data
  } catch (error) {
    // 如果没有公开的设置接口，忽略错误
    console.log('无法加载限制信息:', error)
  }
}

const handleFileSelect = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files) {
    const files = Array.from(input.files)

    // 前端预检查文件数量限制
    if (limitInfo.value?.max_files_per_upload && files.length > limitInfo.value.max_files_per_upload) {
      uploadError.value = `单次上传文件数量超过限制 (${limitInfo.value.max_files_per_upload}个文件)`
      // 清空已选择的文件
      selectedFiles.value = []
      input.value = ''
      showError.value = true
      return
    }

    // 前端预检查文件大小限制
    if (limitInfo.value?.max_file_size) {
      const maxSizeInBytes = limitInfo.value.max_file_size * 1024 * 1024
      let oversizedFile = null
      for (const file of files) {
        if (file.size > maxSizeInBytes) {
          oversizedFile = file
          break
        }
      }

      if (oversizedFile) {
        uploadError.value = `文件 ${oversizedFile.name} 超过大小限制 (${limitInfo.value.max_file_size}MB)`
        // 清空已选择的文件
        selectedFiles.value = []
        input.value = ''
        showError.value = true
        return
      }
    }

    selectedFiles.value = files
  }
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  if (event.dataTransfer?.files) {
    const files = Array.from(event.dataTransfer.files)

    // 前端预检查文件数量限制
    if (limitInfo.value?.max_files_per_upload && files.length > limitInfo.value.max_files_per_upload) {
      uploadError.value = `单次上传文件数量超过限制 (${limitInfo.value.max_files_per_upload}个文件)`
      showError.value = true
      return
    }

    // 前端预检查文件大小限制
    if (limitInfo.value?.max_file_size) {
      const maxSizeInBytes = limitInfo.value.max_file_size * 1024 * 1024
      let oversizedFile = null
      for (const file of files) {
        if (file.size > maxSizeInBytes) {
          oversizedFile = file
          break
        }
      }

      if (oversizedFile) {
        uploadError.value = `文件 ${oversizedFile.name} 超过大小限制 (${limitInfo.value.max_file_size}MB)`
        showError.value = true
        return
      }
    }

    selectedFiles.value = files
  }
}

const removeFile = (index: number) => {
  selectedFiles.value.splice(index, 1)
}

const uploadFiles = async () => {
  if (!uploaderName.value.trim() || selectedFiles.value.length === 0) return

  // 前端验证上传限制（二次确认）
  if (limitInfo.value) {
    // 验证文件数量限制
    if (limitInfo.value.max_files_per_upload && selectedFiles.value.length > limitInfo.value.max_files_per_upload) {
      uploadError.value = `单次上传文件数量超过限制 (${limitInfo.value.max_files_per_upload}个文件)`
      showError.value = true
      return
    }

    // 验证文件大小限制
    if (limitInfo.value.max_file_size) {
      const maxSizeInBytes = limitInfo.value.max_file_size * 1024 * 1024
      for (const file of selectedFiles.value) {
        if (file.size > maxSizeInBytes) {
          uploadError.value = `文件 ${file.name} 超过大小限制 (${limitInfo.value.max_file_size}MB)`
          showError.value = true
          return
        }
      }
    }
  }

  uploading.value = true
  uploadSuccess.value = false
  uploadError.value = ''
  uploadProgress.value = 0
  uploadSpeed.value = 0
  timeRemaining.value = 0

  try {
    const formData = new FormData()
    formData.append('uploader_name', uploaderName.value.trim())
    
    for (const file of selectedFiles.value) {
      formData.append('files', file)
    }

    // 记录开始时间
    const startTime = Date.now()
    let lastTime = startTime
    let lastLoaded = 0

    await axios.post(`${API_BASE}/upload/${route.params.taskId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          // 计算进度百分比
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          uploadProgress.value = percentCompleted

          // 计算上传速度和剩余时间
          const currentTime = Date.now()
          const timeElapsed = (currentTime - lastTime) / 1000 // 转换为秒
          const dataLoaded = progressEvent.loaded - lastLoaded

          if (timeElapsed >= 1) { // 每秒更新一次速度
            uploadSpeed.value = dataLoaded / timeElapsed
            lastTime = currentTime
            lastLoaded = progressEvent.loaded

            // 计算剩余时间（秒）
            const remainingBytes = progressEvent.total - progressEvent.loaded
            if (uploadSpeed.value > 0) {
              timeRemaining.value = remainingBytes / uploadSpeed.value
            }
          } else if (lastTime === startTime) {
            // 首次计算速度
            const totalElapsed = (currentTime - startTime) / 1000
            if (totalElapsed > 0) {
              uploadSpeed.value = progressEvent.loaded / totalElapsed
              const remainingBytes = progressEvent.total - progressEvent.loaded
              if (uploadSpeed.value > 0) {
                timeRemaining.value = remainingBytes / uploadSpeed.value
              }
            }
          }
        }
      }
    })

    uploadSuccess.value = true
    selectedFiles.value = []
    uploaderName.value = ''
  } catch (error: any) {
    console.error('上传失败:', error)
    // 显示详细的错误信息
    if (error.response?.data?.detail) {
      uploadError.value = error.response.data.detail
    } else {
      uploadError.value = '文件上传失败，请稍后重试'
    }
    showError.value = true
  } finally {
    uploading.value = false
    uploadProgress.value = 0
    uploadSpeed.value = 0
    timeRemaining.value = 0
  }
}

// Utility functions
const getStatusClass = (status: string) => {
  switch (status) {
    case 'active':
      return 'bg-green-100 text-green-800'
    case 'inactive':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'active':
      return '开放上传'
    case 'inactive':
      return '已关闭'
    default:
      return '未知状态'
  }
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 添加格式化速度和时间的工具函数
const formatSpeed = (bytesPerSecond: number) => {
  if (bytesPerSecond === 0) return '0 B/s'
  const k = 1024
  const sizes = ['B/s', 'KB/s', 'MB/s', 'GB/s']
  const i = Math.floor(Math.log(bytesPerSecond) / Math.log(k))
  return parseFloat((bytesPerSecond / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatTime = (seconds: number) => {
  if (seconds < 60) {
    return `${Math.round(seconds)}秒`
  } else if (seconds < 3600) {
    return `${Math.floor(seconds / 60)}分${Math.round(seconds % 60)}秒`
  } else {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}小时${minutes}分`
  }
}
</script>