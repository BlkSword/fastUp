from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"

class TaskCreate(BaseModel):
    name: str
    description: Optional[str] = None
    
class TaskResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    status: TaskStatus
    folder_path: str
    created_at: datetime
    uploaded_files_count: int = 0
    
    class Config:
        from_attributes = True

class FileUploadResponse(BaseModel):
    filename: str
    file_path: str
    size: int
    upload_time: datetime
    uploader_name: str

class UploadTaskInfo(BaseModel):
    task_id: str
    task_name: str
    description: Optional[str] = None
    status: TaskStatus