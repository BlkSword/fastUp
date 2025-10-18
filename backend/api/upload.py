from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import List
import os
import shutil
import aiofiles
from datetime import datetime
from models.schemas import FileUploadResponse
from core.storage import task_storage

# 添加导入
import json
from typing import Optional

router = APIRouter()

# 获取配置文件路径
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')

def load_config():
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def get_settings():
    """获取系统设置"""
    config = load_config()
    return config.get("settings", {})

async def save_uploaded_file(file: UploadFile, task_id: str, uploader_name: str) -> FileUploadResponse:
    """保存上传的文件到指定任务目录下的姓名文件夹"""
    
    # 验证任务是否存在且状态为活跃
    task = task_storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task.status.value != "active":
        raise HTTPException(status_code=400, detail="任务已关闭，无法上传文件")
    
    # 获取设置
    settings = get_settings()
    max_file_size = settings.get("max_file_size")
    
    # 检查文件大小限制
    if max_file_size and max_file_size > 0:
        # file.size 是字节，max_file_size 是 MB
        max_size_bytes = max_file_size * 1024 * 1024
        if file.size > max_size_bytes:
            raise HTTPException(
                status_code=400, 
                detail=f"文件 {file.filename} 超过大小限制 ({max_file_size}MB)"
            )
    
    # 创建上传者姓名文件夹路径
    uploader_folder = os.path.join(task.folder_path, uploader_name)
    os.makedirs(uploader_folder, exist_ok=True)
    
    # 生成文件保存路径
    file_path = os.path.join(uploader_folder, file.filename)
    
    # 如果文件已存在，添加时间戳后缀
    if os.path.exists(file_path):
        name, ext = os.path.splitext(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(uploader_folder, f"{name}_{timestamp}{ext}")
    
    # 保存文件
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
    
    # 更新任务的文件数量
    task_storage.increment_file_count(task_id)
    
    # 获取文件大小
    file_size = os.path.getsize(file_path)
    
    return FileUploadResponse(
        filename=file.filename,
        file_path=file_path,
        size=file_size,
        upload_time=datetime.now(),
        uploader_name=uploader_name
    )

@router.post("/{task_id}", response_model=List[FileUploadResponse])
async def upload_files(
    task_id: str,
    uploader_name: str = Form(..., description="上传者姓名"),
    files: List[UploadFile] = File(..., description="要上传的文件列表")
):
    """上传文件到指定任务"""
    
    if not uploader_name.strip():
        raise HTTPException(status_code=400, detail="请输入上传者姓名")
    
    if not files:
        raise HTTPException(status_code=400, detail="请选择要上传的文件")
    
    # 获取设置
    settings = get_settings()
    max_files_per_upload = settings.get("max_files_per_upload")
    
    # 检查文件数量限制
    if max_files_per_upload and max_files_per_upload > 0:
        if len(files) > max_files_per_upload:
            raise HTTPException(
                status_code=400, 
                detail=f"单次上传文件数量超过限制 ({max_files_per_upload}个文件)"
            )
    
    # 验证文件
    for file in files:
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        # 文件大小检查移到 save_uploaded_file 函数中处理
    
    uploaded_files = []
    upload_errors = []
    
    # 获取最大错误数设置
    max_upload_errors = settings.get("max_upload_errors", 0)
    
    # 保存所有文件
    for file in files:
        try:
            file_response = await save_uploaded_file(file, task_id, uploader_name.strip())
            uploaded_files.append(file_response)
        except Exception as e:
            # 记录错误
            upload_errors.append({
                "filename": file.filename,
                "error": str(e)
            })
            
            # 检查是否超过最大错误数
            if max_upload_errors > 0 and len(upload_errors) > max_upload_errors:
                raise HTTPException(
                    status_code=400, 
                    detail=f"上传错误数超过限制 ({max_upload_errors}个错误): {len(upload_errors)}个文件上传失败"
                )
            
            # 如果没有设置错误限制，继续处理其他文件
            # 如果设置了错误限制为0（无限制），也继续处理
    
    # 如果有错误但未超过限制，返回部分成功的结果
    if upload_errors:
        # 可以选择是否在此处抛出异常或返回部分结果
        # 这里我们选择继续，但可以在响应中包含错误信息
        pass
    
    return uploaded_files

@router.get("/{task_id}/files")
async def list_uploaded_files(task_id: str):
    """列出任务下所有已上传的文件"""
    task = task_storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    try:
        files_info = []
        task_folder = task.folder_path
        
        if os.path.exists(task_folder):
            # 遍历所有上传者文件夹
            for uploader_name in os.listdir(task_folder):
                uploader_folder = os.path.join(task_folder, uploader_name)
                if os.path.isdir(uploader_folder):
                    # 遍历上传者文件夹中的所有文件
                    for filename in os.listdir(uploader_folder):
                        file_path = os.path.join(uploader_folder, filename)
                        if os.path.isfile(file_path):
                            stat = os.stat(file_path)
                            files_info.append({
                                "filename": filename,
                                "uploader_name": uploader_name,
                                "file_path": file_path,
                                "size": stat.st_size,
                                "upload_time": datetime.fromtimestamp(stat.st_mtime)
                            })
        
        return {"files": files_info, "total_count": len(files_info)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")