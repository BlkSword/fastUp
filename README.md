# 文件收集系统 (fastUp)

一个基于 FastAPI 和 Vue 3 的文件收集系统，用于创建和管理文件上传任务。

## 功能特点

- 📁 **任务管理**: 创建、管理和监控文件收集任务
- 🔐 **权限控制**: 管理员后台管理与公开上传页面分离
- ⚙️ **灵活配置**: 支持多种上传限制设置（文件大小、数量、上传者白名单等）
- 🔄 **断点续传**: 支持大文件分块上传
- 📊 **实时统计**: 实时显示任务进度和上传统计信息
- 🎨 **现代化界面**: 基于 Vue 3 和 Tailwind CSS 的响应式设计

## 技术栈

### 后端
- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速（高性能）的Web框架
- [Uvicorn](https://www.uvicorn.org/) - 用于Python的轻量级ASGI服务器
- [Python-Multipart](https://github.com/andrew-d/python-multipart) - 用于处理multipart/form-data
- [Passlib](https://passlib.readthedocs.io/en/stable/) - 用于密码哈希处理

### 前端
- [Vue 3](https://v3.vuejs.org/) - 渐进式JavaScript框架
- [Tailwind CSS](https://tailwindcss.com/) - 实用优先的CSS框架
- [Ant Design Vue](https://www.antdv.com/) - Vue UI库

## 安装与运行

### 后端

1. 创建虚拟环境并激活:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. 安装依赖:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. 运行后端服务:
   ```bash
   cd backend
   python main.py
   ```
   
   或使用 uvicorn:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### 前端

1. 安装依赖:
   ```bash
   cd frontend
   npm install
   ```

2. 运行开发服务器:
   ```bash
   npm run dev
   ```

3. 构建生产版本:
   ```bash
   npm run build
   ```

## 项目结构

```
fastUp/
├── backend/                 # 后端代码
│   ├── api/                 # API路由
│   │   ├── settings.py      # 系统设置相关接口
│   │   ├── tasks.py         # 任务管理相关接口
│   │   └── upload.py        # 文件上传相关接口
│   ├── core/                # 核心模块
│   │   ├── auth.py          # 认证模块
│   │   └── storage.py       # 存储管理模块
│   ├── models/              # 数据模型
│   │   └── schemas.py       # Pydantic模型定义
│   ├── uploads/             # 上传文件存储目录
│   ├── config.json          # 系统配置文件
│   ├── main.py              # 应用入口
│   └── requirements.txt     # Python依赖
└── frontend/                # 前端代码
    ├── src/
    │   ├── views/           # 页面组件
    │   │   ├── AdminView.vue # 管理员界面
    │   │   ├── LoginView.vue # 登录界面
    │   │   └── UploadView.vue # 文件上传界面
    │   └── ...
```

## API 接口

### 公共接口
- `GET /api/health` - 健康检查
- `GET /api/tasks/{task_id}/info` - 获取任务信息
- `POST /api/upload/{task_id}` - 上传文件到指定任务
- `GET /api/settings/public` - 获取公开的系统设置

### 管理员接口
- `POST /api/tasks/` - 创建新任务
- `GET /api/tasks/` - 获取所有任务列表
- `GET /api/tasks/{task_id}` - 获取特定任务详情
- `PUT /api/tasks/{task_id}` - 更新任务状态
- `DELETE /api/tasks/{task_id}` - 删除任务
- `GET /api/tasks/{task_id}/download` - 下载任务中的所有文件
- `GET /api/settings` - 获取系统设置
- `PUT /api/settings` - 更新系统设置

## 配置说明

系统配置存储在 `backend/config.json` 文件中，包括：

- 管理员账户信息
- 上传限制设置（文件大小、数量等）
- 白名单设置
- 其他系统参数

