from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasicCredentials
import os

from api import tasks, upload, settings
from core.auth import verify_admin

app = FastAPI(title="文件收集系统 API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers - 受保护的路由需要添加依赖
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"], dependencies=[Depends(verify_admin)])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(settings.router, prefix="/api", tags=["settings"], dependencies=[Depends(verify_admin)])

# Include public routers - 不需要认证的公开路由
app.include_router(tasks.public_router, prefix="/api/tasks", tags=["public tasks"])
app.include_router(settings.public_router, prefix="/api", tags=["public settings"])

# 公开的不需要认证的路由
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "文件收集系统 API 运行正常"}

# 添加认证检查端点
@app.get("/api/auth/check")
async def auth_check(username: str = Depends(verify_admin)):
    return {"authenticated": True, "username": username}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)