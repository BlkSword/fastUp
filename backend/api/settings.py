from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
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
    max_uploads_per_user: Optional[int] = None  # 每人上传次数限制
    upload_whitelist: Optional[List[str]] = None  # 上传者白名单

class WhitelistToggle(BaseModel):
    enabled: bool

class SettingsResponse(BaseModel):
    max_file_size: Optional[int] = None  # MB
    max_files_per_upload: Optional[int] = None
    max_upload_errors: Optional[int] = None
    max_uploads_per_user: Optional[int] = None  # 每人上传次数限制
    upload_whitelist: Optional[List[str]] = None  # 上传者白名单

class PublicSettingsResponse(BaseModel):
    max_file_size: Optional[int] = None  # MB
    max_files_per_upload: Optional[int] = None
    max_upload_errors: Optional[int] = None
    max_uploads_per_user: Optional[int] = None  # 每人上传次数限制
    upload_whitelist_enabled: Optional[bool] = None  # 是否启用白名单

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
        max_upload_errors=settings.get("max_upload_errors"),
        max_uploads_per_user=settings.get("max_uploads_per_user"),
        upload_whitelist=settings.get("upload_whitelist")
    )

@public_router.get("/settings/public", response_model=PublicSettingsResponse)
async def get_public_settings():
    """获取公开的系统设置（供上传页面显示限制信息）"""
    config = load_config()
    settings = config.get("settings", {})
    # 只返回是否启用白名单，而不返回具体名单
    upload_whitelist = settings.get("upload_whitelist")
    upload_whitelist_enabled = bool(upload_whitelist and len(upload_whitelist) > 0)
    
    return PublicSettingsResponse(
        max_file_size=settings.get("max_file_size"),
        max_files_per_upload=settings.get("max_files_per_upload"),
        max_upload_errors=settings.get("max_upload_errors"),
        max_uploads_per_user=settings.get("max_uploads_per_user"),
        upload_whitelist_enabled=upload_whitelist_enabled
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
        
    if settings.max_uploads_per_user is not None:
        config["settings"]["max_uploads_per_user"] = settings.max_uploads_per_user
        
    if settings.upload_whitelist is not None:
        config["settings"]["upload_whitelist"] = settings.upload_whitelist
    
    # 保存配置
    save_config(config)
    
    return SettingsResponse(
        max_file_size=config["settings"].get("max_file_size"),
        max_files_per_upload=config["settings"].get("max_files_per_upload"),
        max_upload_errors=config["settings"].get("max_upload_errors"),
        max_uploads_per_user=config["settings"].get("max_uploads_per_user"),
        upload_whitelist=config["settings"].get("upload_whitelist")
    )

# 新增接口：控制白名单启用/禁用状态
@router.put("/settings/upload-whitelist-toggle")
async def toggle_upload_whitelist(toggle: WhitelistToggle, username: str = Depends(verify_admin)):
    """启用或禁用上传白名单"""
    config = load_config()
    
    # 如果没有设置部分，创建一个空的
    if "settings" not in config:
        config["settings"] = {}
    
    # 获取当前白名单
    current_whitelist = config["settings"].get("upload_whitelist", [])
    
    if toggle.enabled:
        # 启用白名单 - 如果当前没有白名单，则创建一个空的白名单
        if not current_whitelist:
            config["settings"]["upload_whitelist"] = []
    else:
        # 禁用白名单 - 清空调名单
        config["settings"]["upload_whitelist"] = []
    
    # 保存配置
    save_config(config)
    
    return {
        "enabled": toggle.enabled,
        "message": f"白名单已{'启用' if toggle.enabled else '禁用'}"
    }

# 新增接口：上传并解析白名单文件
@router.post("/settings/upload-whitelist-file")
async def upload_whitelist_file(file: UploadFile = File(...), username: str = Depends(verify_admin)):
    """上传并解析白名单文件"""
    try:
        # 读取文件内容
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # 按行分割并清理空白字符
        whitelist = [line.strip() for line in content_str.split('\n') if line.strip()]
        
        # 去重
        whitelist = list(set(whitelist))
        
        # 保存到配置
        config = load_config()
        if "settings" not in config:
            config["settings"] = {}
        config["settings"]["upload_whitelist"] = whitelist
        save_config(config)
        
        return {"message": "白名单文件上传成功", "whitelist": whitelist}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")

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