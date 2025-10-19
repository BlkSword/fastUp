from fastapi import APIRouter, HTTPException
from typing import List
import os
from models.schemas import TaskCreate, TaskResponse, TaskStatus, UploadTaskInfo
from core.storage import task_storage

router = APIRouter()
public_router = APIRouter()

@public_router.get("/{task_id}/info", response_model=UploadTaskInfo)
async def get_upload_task_info(task_id: str):
    """获取上传任务信息（用于上传页面）"""
    task = task_storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task.status != TaskStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="任务已关闭，无法上传文件")
    
    # 获取实际的文件数量和上传人数
    actual_file_count, actual_users_count = task_storage.get_actual_counts(task.folder_path)
    
    return UploadTaskInfo(
        task_id=task.id,
        task_name=task.name,
        description=task.description,
        status=task.status,
        uploaded_files_count=actual_file_count,
        uploaded_users_count=actual_users_count
    )

@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate):
    """创建新的上传任务"""
    try:
        new_task = task_storage.create_task(task.name, task.description)
        return new_task
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")

@router.get("/", response_model=List[TaskResponse])
async def get_all_tasks():
    """获取所有任务列表"""
    try:
        tasks = task_storage.get_all_tasks()
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """获取指定任务详情"""
    task = task_storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task

@router.put("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(task_id: str, status: TaskStatus):
    """更新任务状态"""
    task = task_storage.update_task_status(task_id, status)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task

@router.delete("/{task_id}")
async def delete_task(task_id: str):
    """删除任务"""
    success = task_storage.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"message": "任务删除成功"}