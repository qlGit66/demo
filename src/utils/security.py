from cryptography.fernet import Fernet
import base64
import os
from pathlib import Path

class Security:
    def __init__(self, encryption_key=None):
        self.key = encryption_key or self._load_or_generate_key()
        self.cipher_suite = Fernet(self.key)
        
    def _load_or_generate_key(self):
        """加载或生成加密密钥"""
        key_file = Path('data/.key')
        if key_file.exists():
            return key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            key_file.parent.mkdir(exist_ok=True)
            key_file.write_bytes(key)
            return key
            
    def encrypt(self, data: str) -> str:
        """加密数据"""
        return self.cipher_suite.encrypt(data.encode()).decode()
        
    def decrypt(self, encrypted_data: str) -> str:
        """解密数据"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode() 