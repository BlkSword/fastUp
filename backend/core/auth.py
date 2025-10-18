from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
import secrets
import json
import os

# 创建基本HTTP认证实例
security = HTTPBasic()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 获取配置文件路径
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')

# 从配置文件加载管理员凭据
def load_admin_credentials():
    """从配置文件加载管理员凭据"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('admin', {})
    except FileNotFoundError:
        # 如果配置文件不存在，抛出异常
        raise FileNotFoundError("配置文件未找到")

def verify_password(plain_password, expected_password):
    """验证密码"""
    return secrets.compare_digest(plain_password, expected_password)

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """
    验证凭据
    """
    # 加载最新的管理员凭据
    admin_config = load_admin_credentials()
    admin_username = admin_config.get("username")
    admin_password = admin_config.get("password")
    
    # 确保配置文件中有用户名和密码
    if not admin_username or not admin_password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="管理员凭据未在配置文件中正确配置",
        )
    
    # 验证用户名
    correct_username = secrets.compare_digest(credentials.username, admin_username)
    
    # 验证密码
    correct_password = verify_password(credentials.password, admin_password)
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username