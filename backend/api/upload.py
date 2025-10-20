from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
import os
import aiofiles
from datetime import datetime
from models.schemas import FileUploadResponse
from core.storage import task_storage
import json
from pydantic import BaseModel

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

class UploadPrecheckResponse(BaseModel):
    """上传预检查响应模型"""
    can_upload: bool
    reason: Optional[str] = None
    max_files_per_upload: Optional[int] = None
    max_file_size: Optional[int] = None
    max_uploads_per_user: Optional[int] = None
    current_upload_count: Optional[int] = None

@router.post("/{task_id}/precheck", response_model=UploadPrecheckResponse)
async def precheck_upload(
    task_id: str,
    uploader_name: str = Form(...),
    file_count: int = Form(...),
    total_size: int = Form(...)
):
    """预检查上传是否符合限制条件"""
    # 检查任务是否存在且活跃
    task = task_storage.get_task(task_id)
    if not task:
        return UploadPrecheckResponse(
            can_upload=False,
            reason="任务不存在"
        )
    
    if task.status.value != "active":
        return UploadPrecheckResponse(
            can_upload=False,
            reason="任务已关闭，无法上传文件"
        )
    
    # 检查上传者是否在白名单中
    if not check_upload_whitelist(uploader_name):
        return UploadPrecheckResponse(
            can_upload=False,
            reason="您不在允许上传的名单中"
        )
    
    # 获取设置
    settings = get_settings()
    max_files_per_upload = settings.get("max_files_per_upload")
    max_file_size = settings.get("max_file_size")
    max_uploads_per_user = settings.get("max_uploads_per_user")
    
    # 检查文件数量限制
    if max_files_per_upload and max_files_per_upload > 0:
        if file_count > max_files_per_upload:
            return UploadPrecheckResponse(
                can_upload=False,
                reason=f"单次上传文件数量超过限制 ({max_files_per_upload}个文件)",
                max_files_per_upload=max_files_per_upload
            )
    
    # 检查每人上传次数限制
    if max_uploads_per_user and max_uploads_per_user > 0:
        current_upload_count = get_user_upload_count(task_id, uploader_name)
        if current_upload_count + file_count > max_uploads_per_user:
            return UploadPrecheckResponse(
                can_upload=False,
                reason=f"上传文件数量将超过您的上传次数限制 ({max_uploads_per_user}次)，当前已上传 {current_upload_count} 次",
                max_uploads_per_user=max_uploads_per_user,
                current_upload_count=current_upload_count
            )
    
    # 返回检查通过的结果
    return UploadPrecheckResponse(
        can_upload=True,
        max_files_per_upload=max_files_per_upload,
        max_file_size=max_file_size,
        max_uploads_per_user=max_uploads_per_user,
        current_upload_count=get_user_upload_count(task_id, uploader_name) if max_uploads_per_user else None
    )

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
    
    # 直接保存文件，使用流式写入避免内存占用过大
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            # 使用64KB的缓冲区进行流式写入
            while True:
                chunk = await file.read(65536)  # 64KB
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
    
@router.post("/check-whitelist/{task_id}")
async def check_whitelist(
    task_id: str,
    uploader_name: str = Form(..., description="上传者姓名")
):
    """检查上传者是否在白名单中"""
    task = task_storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task.status.value != "active":
        raise HTTPException(status_code=400, detail="任务已关闭，无法上传文件")
    
    if not check_upload_whitelist(uploader_name):
        raise HTTPException(status_code=403, detail="您不在允许上传的名单中")
    
    return {"message": "用户在白名单中"}

@router.get("/user-upload-count/{task_id}/{uploader_name}")
async def get_user_upload_count_endpoint(
    task_id: str,
    uploader_name: str
):
    """获取用户在特定任务中的上传文件数量"""
    count = get_user_upload_count(task_id, uploader_name)
    return {"count": count}

@router.post("/{task_id}", response_model=List[FileUploadResponse])
async def upload_files(
    task_id: str,
    uploader_name: str = Form(..., description="上传者姓名"),
    files: List[UploadFile] = File(..., description="要上传的文件列表")
):
    """直接上传文件到指定任务"""
    
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
