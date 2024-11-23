import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
import json

class Logger:
    def __init__(self, config):
        self.config = config
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """设置日志系统"""
        logger = logging.getLogger("chaoxing")
        logger.setLevel(getattr(logging, self.config.logging['level']))
        
        # 创建日志目录
        os.makedirs(self.config.logging['dir'], exist_ok=True)
        
        # 文件处理器（带轮转）
        log_file = os.path.join(
            self.config.logging['dir'], 
            f"chaoxing_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.config.logging['max_size'] * 1024 * 1024,
            backupCount=self.config.logging['backup_count'],
            encoding='utf-8'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        
        # 格式化
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
        
    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)
        
    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)
        
    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)
        
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs) 