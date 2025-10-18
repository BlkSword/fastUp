<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6">
    <div class="max-w-3xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-10">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-indigo-100 mb-4">
          <svg class="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
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
              <input
                id="uploaderName"
                v-model="uploaderName"
                type="text"
                required
                :disabled="uploading"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors disabled:bg-gray-100"
                placeholder="请输入您的姓名"
              />
            </div>

            <!-- File Drop Zone -->
            <div class="mb-6">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                选择文件 <span class="text-red-500">*</span>
              </label>
              <div 
                @dragover.prevent
                @dragenter.prevent
                @drop="handleDrop"
                class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer transition-colors hover:border-indigo-400 hover:bg-indigo-50"
                :class="{ 'bg-gray-50': uploading }"
              >
                <input
                  ref="fileInput"
                  type="file"
                  multiple
                  @change="handleFileSelect"
                  class="hidden"
                  :disabled="uploading"
                />
                <div @click="$refs.fileInput.click()" class="space-y-2">
                  <div class="flex justify-center">
                    <svg class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
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
                <div
                  v-for="(file, index) in selectedFiles"
                  :key="index"
                  class="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div class="flex items-center space-x-3">
                    <svg class="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd" />
                    </svg>
                    <div>
                      <p class="text-sm font-medium text-gray-900 truncate max-w-xs">{{ file.name }}</p>
                      <p class="text-xs text-gray-500">{{ formatFileSize(file.size) }}</p>
                    </div>
                  </div>
                  <button
                    type="button"
                    @click="removeFile(index)"
                    :disabled="uploading"
                    class="text-gray-400 hover:text-red-500 transition-colors disabled:opacity-50"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
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
          </form>

          <!-- Task Inactive Message -->
          <div v-else-if="taskInfo?.status === 'inactive'" class="text-center py-10">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
            </svg>
            <h3 class="mt-2 text-lg font-medium text-gray-900">任务已关闭</h3>
            <p class="mt-1 text-gray-500">该文件收集任务已关闭，暂时无法上传文件。</p>
          </div>

          <!-- Task Not Found Message -->
          <div v-else-if="taskNotFound" class="text-center py-10">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
            </svg>
            <h3 class="mt-2 text-lg font-medium text-gray-900">任务不存在</h3>
            <p class="mt-1 text-gray-500">找不到指定的文件收集任务。</p>
          </div>

          <!-- Loading State -->
          <div v-else class="text-center py-10">
            <svg class="animate-spin h-10 w-10 text-indigo-600 mx-auto" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p class="mt-3 text-gray-500">正在加载任务信息...</p>
          </div>
        </div>
      </div>

      <!-- Success Message -->
      <div v-if="uploadSuccess" class="mt-6 bg-green-50 border border-green-200 rounded-lg p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-green-800">上传成功</h3>
            <div class="mt-2 text-sm text-green-700">
              <p>您的文件已成功上传！</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="uploadError" class="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">上传失败</h3>
            <div class="mt-2 text-sm text-red-700">
              <p>{{ uploadError }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Limit Info -->
      <div v-if="limitInfo" class="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-blue-800">上传限制</h3>
            <div class="mt-2 text-sm text-blue-700">
              <ul class="list-disc pl-5 space-y-1">
                <li v-if="limitInfo.maxFileSize">单文件大小限制: {{ limitInfo.maxFileSize }}MB</li>
                <li v-if="limitInfo.maxFilesPerUpload">单次上传文件数量限制: {{ limitInfo.maxFilesPerUpload }}个</li>
                <li v-if="limitInfo.maxUploadErrors">最大上传错误数: {{ limitInfo.maxUploadErrors }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

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
    selectedFiles.value = Array.from(input.files)
  }
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  if (event.dataTransfer?.files) {
    selectedFiles.value = Array.from(event.dataTransfer.files)
  }
}

const removeFile = (index: number) => {
  selectedFiles.value.splice(index, 1)
}

const uploadFiles = async () => {
  if (!uploaderName.value.trim() || selectedFiles.value.length === 0) return

  // 前端验证上传限制
  if (limitInfo.value) {
    // 验证文件数量限制
    if (limitInfo.value.maxFilesPerUpload && selectedFiles.value.length > limitInfo.value.maxFilesPerUpload) {
      uploadError.value = `单次上传文件数量超过限制 (${limitInfo.value.maxFilesPerUpload}个文件)`
      // 自动隐藏错误消息
      setTimeout(() => {
        uploadError.value = ''
      }, 5000)
      return
    }

    // 验证文件大小限制
    if (limitInfo.value.maxFileSize) {
      const maxSizeInBytes = limitInfo.value.maxFileSize * 1024 * 1024
      for (const file of selectedFiles.value) {
        if (file.size > maxSizeInBytes) {
          uploadError.value = `文件 ${file.name} 超过大小限制 (${limitInfo.value.maxFileSize}MB)`
          // 自动隐藏错误消息
          setTimeout(() => {
            uploadError.value = ''
          }, 5000)
          return
        }
      }
    }
  }

  uploading.value = true
  uploadSuccess.value = false
  uploadError.value = ''

  try {
    const formData = new FormData()
    formData.append('uploader_name', uploaderName.value.trim())
    
    for (const file of selectedFiles.value) {
      formData.append('files', file)
    }

    await axios.post(`${API_BASE}/upload/${route.params.taskId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    uploadSuccess.value = true
    selectedFiles.value = []
    uploaderName.value = ''
    
    // 自动隐藏成功消息
    setTimeout(() => {
      uploadSuccess.value = false
    }, 5000)
  } catch (error: any) {
    console.error('上传失败:', error)
    // 显示详细的错误信息
    if (error.response?.data?.detail) {
      uploadError.value = error.response.data.detail
    } else {
      uploadError.value = '文件上传失败，请稍后重试'
    }
    
    // 自动隐藏错误消息
    setTimeout(() => {
      uploadError.value = ''
    }, 10000)
  } finally {
    uploading.value = false
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
</script>