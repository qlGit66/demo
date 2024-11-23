from dataclasses import dataclass
import yaml
import os

@dataclass
class Config:
    # 基础配置
    openai_api_key: str
    chaoxing_token: str
    
    # 通知配置
    notification_threshold: int = 50
    enable_desktop_notification: bool = True
    enable_email_notification: bool = False
    
    # 邮件配置
    email: dict = None
    
    # 答题配置
    retry_times: int = 3
    delay_range: tuple = (1, 3)
    timeout: int = 30
    debug_mode: bool = False
    
    # 日志配置
    log_level: str = "INFO"
    log_dir: str = "logs"
    
    @classmethod
    def from_yaml(cls, path: str = "config.yaml"):
        if not os.path.exists(path):
            raise FileNotFoundError(f"配置文件不存在: {path}")
            
        with open(path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        return cls(**config_dict) 