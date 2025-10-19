from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
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
import zipfile
from fastapi.responses import FileResponse
import tempfile
import asyncio
from concurrent.futures import ThreadPoolExecutor

router = APIRouter()

# 创建线程池用于文件操作
file_operation_executor = ThreadPoolExecutor(max_workers=10)

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

# 分块上传相关常量
def get_chunk_size():
    """获取分块大小设置，默认为1MB"""
    settings = get_settings()
    chunk_size_mb = settings.get("chunk_size", 1)  # 默认1MB
    return chunk_size_mb * 1024 * 1024  # 转换为字节

CHUNK_SIZE = get_chunk_size()

def get_user_upload_count(task_id: str, uploader_name: str) -> int:
    """获取用户在特定任务中的上传文件数量"""
    task = task_storage.get_task(task_id)
    if not task:
        return 0
    
    task_folder = task.folder_path
    uploader_folder = os.path.join(task_folder, uploader_name)
    
    if not os.path.exists(uploader_folder):
        return 0
    
    # 计算该用户文件夹中的文件数量
    count = 0
    try:
        for filename in os.listdir(uploader_folder):
            file_path = os.path.join(uploader_folder, filename)
            if os.path.isfile(file_path):
                count += 1
    except OSError:
        pass
    
    return count

def check_upload_whitelist(uploader_name: str) -> bool:
    """检查上传者是否在白名单中"""
    settings = get_settings()
    whitelist = settings.get("upload_whitelist")
    
    # 如果没有设置白名单，则允许所有用户上传
    if not whitelist:
        return True
    
    # 如果白名单为空，则允许所有用户上传
    if len(whitelist) == 0:
        return True
    
    # 检查上传者是否在白名单中（不区分大小写）
    return uploader_name.strip().lower() in [name.strip().lower() for name in whitelist]

async def save_uploaded_file(file: UploadFile, task_id: str, uploader_name: str) -> FileUploadResponse:
    """保存上传的文件到指定任务目录下的姓名文件夹"""
    
    # 验证任务是否存在且状态为活跃
    task = task_storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task.status.value != "active":
        raise HTTPException(status_code=400, detail="任务已关闭，无法上传文件")
    
    # 检查上传者是否在白名单中
    if not check_upload_whitelist(uploader_name):
        raise HTTPException(status_code=403, detail="您不在允许上传的名单中")
    
    # 获取设置
    settings = get_settings()
    max_file_size = settings.get("max_file_size")
    max_uploads_per_user = settings.get("max_uploads_per_user")
    
    # 检查每人上传次数限制
    if max_uploads_per_user and max_uploads_per_user > 0:
        current_upload_count = get_user_upload_count(task_id, uploader_name)
        if current_upload_count >= max_uploads_per_user:
            raise HTTPException(
                status_code=400,
                detail=f"您已达到上传次数限制 ({max_uploads_per_user}次)"
            )
    
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
    
    # 流式保存文件，适用于大文件
    try:
        # 获取分块大小设置，默认为16MB
        chunk_size = get_chunk_size() or (16 * 1024 * 1024)
        async with aiofiles.open(file_path, 'wb') as f:
            # 分块读取和写入，避免将整个文件载入内存
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                await f.write(chunk)
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
    
    # 检查上传者是否在白名单中（提前检查）
    if not check_upload_whitelist(uploader_name):
        raise HTTPException(status_code=403, detail="您不在允许上传的名单中")
    
    # 获取设置
    settings = get_settings()
    max_files_per_upload = settings.get("max_files_per_upload")
    max_uploads_per_user = settings.get("max_uploads_per_user")
    
    # 检查每人上传次数限制（提前检查）
    if max_uploads_per_user and max_uploads_per_user > 0:
        current_upload_count = get_user_upload_count(task_id, uploader_name)
        if current_upload_count + len(files) > max_uploads_per_user:
            raise HTTPException(
                status_code=400,
                detail=f"上传文件数量将超过您的上传次数限制 ({max_uploads_per_user}次)，当前已上传 {current_upload_count} 次"
            )
    
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
    # 但如果所有文件都失败了，则应该返回错误
    if upload_errors and len(upload_errors) == len(files):
        # 所有文件都上传失败
        error_details = "; ".join([f"{err['filename']}: {err['error']}" for err in upload_errors])
        raise HTTPException(status_code=400, detail=error_details)
    elif upload_errors:
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
        
        # 获取实际的文件数量和上传人数
        actual_file_count, actual_users_count = task_storage.get_actual_counts(task_folder)
        
        return {
            "files": files_info, 
            "total_count": len(files_info),
            "actual_file_count": actual_file_count,
            "actual_users_count": actual_users_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")

# 分块上传相关常量
CHUNK_SIZE = 1024 * 1024  # 1MB chunks

@router.post("/{task_id}/chunked")
async def upload_large_file_chunk(
    task_id: str,
    uploader_name: str = Form(...),
    filename: str = Form(...),
    chunk: UploadFile = File(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
):
    """
    分块上传大文件
    """
    # 验证任务是否存在且状态为活跃
    task = task_storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task.status.value != "active":
        raise HTTPException(status_code=400, detail="任务已关闭，无法上传文件")
    
    # 检查上传者是否在白名单中
    if not check_upload_whitelist(uploader_name):
        raise HTTPException(status_code=403, detail="您不在允许上传的名单中")
    
    # 获取设置
    settings = get_settings()
    max_uploads_per_user = settings.get("max_uploads_per_user")
    
    # 检查每人上传次数限制（仅在第一个块时检查）
    if chunk_index == 0 and max_uploads_per_user and max_uploads_per_user > 0:
        current_upload_count = get_user_upload_count(task_id, uploader_name)
        if current_upload_count >= max_uploads_per_user:
            raise HTTPException(
                status_code=400,
                detail=f"您已达到上传次数限制 ({max_uploads_per_user}次)"
            )
    
    # 获取分块大小设置
    chunk_size = get_chunk_size()
    
    # 创建临时目录存储文件块
    temp_dir = os.path.join(task.folder_path, "temp_uploads", uploader_name)
    os.makedirs(temp_dir, exist_ok=True)
    
    # 存储当前块
    chunk_filename = f"{filename}.part{chunk_index}"
    chunk_path = os.path.join(temp_dir, chunk_filename)
    
    try:
        async with aiofiles.open(chunk_path, 'wb') as f:
            while True:
                data = await chunk.read(chunk_size)
                if not data:
                    break
                await f.write(data)
                
        # 检查是否所有块都已上传完成
        all_chunks_received = all(
            os.path.exists(os.path.join(temp_dir, f"{filename}.part{i}"))
            for i in range(total_chunks)
        )
        
        if all_chunks_received:
            # 组装完整文件
            final_path = os.path.join(task.folder_path, uploader_name, filename)
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            
            # 合并所有块
            async with aiofiles.open(final_path, 'wb') as final_file:
                for i in range(total_chunks):
                    chunk_file_path = os.path.join(temp_dir, f"{filename}.part{i}")
                    async with aiofiles.open(chunk_file_path, 'rb') as chunk_file:
                        while True:
                            data = await chunk_file.read(chunk_size)
                            if not data:
                                break
                            await final_file.write(data)
                    
                    # 删除已合并的块
                    os.remove(chunk_file_path)
            
            # 删除临时目录
            try:
                os.rmdir(temp_dir)
            except OSError:
                pass  # 目录可能不为空或其他原因，暂不处理
            
            # 更新任务的文件数量
            task_storage.increment_file_count(task_id)
            
            # 返回最终文件信息
            stat = os.stat(final_path)
            return {
                "filename": filename,
                "file_path": final_path,
                "size": stat.st_size,
                "upload_time": datetime.fromtimestamp(stat.st_mtime),
                "uploader_name": uploader_name
            }
        else:
            return {"message": f"分块 {chunk_index+1}/{total_chunks} 上传成功"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分块上传失败: {str(e)}")