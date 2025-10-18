from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import json
import os
from core.auth import verify_admin

router = APIRouter()
public_router = APIRouter()

# 获取配置文件路径
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class SettingsUpdate(BaseModel):
    max_file_size: Optional[int] = None  # MB
    max_files_per_upload: Optional[int] = None
    max_upload_errors: Optional[int] = None

class SettingsResponse(BaseModel):
    max_file_size: Optional[int] = None  # MB
    max_files_per_upload: Optional[int] = None
    max_upload_errors: Optional[int] = None

class PublicSettingsResponse(BaseModel):
    max_file_size: Optional[int] = None  # MB
    max_files_per_upload: Optional[int] = None
    max_upload_errors: Optional[int] = None

def load_config():
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_config(config):
    """保存配置文件"""
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

@router.get("/settings", response_model=SettingsResponse)
async def get_settings(username: str = Depends(verify_admin)):
    """获取系统设置"""
    config = load_config()
    settings = config.get("settings", {})
    return SettingsResponse(
        max_file_size=settings.get("max_file_size"),
        max_files_per_upload=settings.get("max_files_per_upload"),
        max_upload_errors=settings.get("max_upload_errors")
    )

@public_router.get("/settings/public", response_model=PublicSettingsResponse)
async def get_public_settings():
    """获取公开的系统设置（供上传页面显示限制信息）"""
    config = load_config()
    settings = config.get("settings", {})
    return PublicSettingsResponse(
        max_file_size=settings.get("max_file_size"),
        max_files_per_upload=settings.get("max_files_per_upload"),
        max_upload_errors=settings.get("max_upload_errors")
    )

@router.put("/settings", response_model=SettingsResponse)
async def update_settings(settings: SettingsUpdate, username: str = Depends(verify_admin)):
    """更新系统设置"""
    config = load_config()
    
    # 如果没有设置部分，创建一个空的
    if "settings" not in config:
        config["settings"] = {}
    
    # 更新设置
    if settings.max_file_size is not None:
        config["settings"]["max_file_size"] = settings.max_file_size
    
    if settings.max_files_per_upload is not None:
        config["settings"]["max_files_per_upload"] = settings.max_files_per_upload
        
    if settings.max_upload_errors is not None:
        config["settings"]["max_upload_errors"] = settings.max_upload_errors
    
    # 保存配置
    save_config(config)
    
    return SettingsResponse(
        max_file_size=config["settings"].get("max_file_size"),
        max_files_per_upload=config["settings"].get("max_files_per_upload"),
        max_upload_errors=config["settings"].get("max_upload_errors")
    )

@router.put("/settings/password")
async def change_password(password_data: PasswordChange, username: str = Depends(verify_admin)):
    """修改管理员密码"""
    config = load_config()
    
    # 验证当前密码
    admin_config = config.get("admin", {})
    current_password = admin_config.get("password")
    
    if current_password != password_data.current_password:
        raise HTTPException(status_code=400, detail="当前密码错误")
    
    # 更新密码
    config["admin"]["password"] = password_data.new_password
    
    # 保存配置
    save_config(config)
    
    return {"message": "密码修改成功"}