import random
import json
from typing import Dict
import hashlib
import platform
import psutil
import uuid
import cpuinfo

class BrowserFingerprint:
    def __init__(self, logger):
        self.logger = logger
        self.fingerprints = self._load_fingerprints()
        self.current_fingerprint = None
        
    def _load_fingerprints(self) -> Dict:
        """加载或生成浏览器指纹库"""
        try:
            with open('data/fingerprints.json', 'r') as f:
                return json.load(f)
        except:
            return self._generate_fingerprint_database()
            
    def _generate_fingerprint_database(self) -> Dict:
        """生成多样化的浏览器指纹数据库"""
        fingerprints = {}
        
        # 生成100个不同的指纹
        for i in range(100):
            fingerprint = {
                "userAgent": self._generate_user_agent(),
                "webGL": self._generate_webgl_data(),
                "canvas": self._generate_canvas_data(),
                "audio": self._generate_audio_data(),
                "hardware": self._generate_hardware_info(),
                "fonts": self._generate_font_list(),
                "plugins": self._generate_plugins(),
                "screen": self._generate_screen_info(),
                "languages": self._generate_languages(),
                "timezone": self._generate_timezone(),
                "webRTC": self._generate_webrtc_info(),
                "battery": self._generate_battery_info(),
                "mediaDevices": self._generate_media_devices(),
                "sensors": self._generate_sensor_data(),
                "performance": self._generate_performance_data()
            }
            
            fingerprint_id = hashlib.md5(
                json.dumps(fingerprint, sort_keys=True).encode()
            ).hexdigest()
            
            fingerprints[fingerprint_id] = fingerprint
            
        return fingerprints
        
    def _generate_user_agent(self) -> str:
        """生成真实的User-Agent"""
        chrome_versions = ['90.0.4430.212', '91.0.4472.124', '92.0.4515.159']
        os_versions = {
            'Windows': ['10.0', '6.1'],
            'Macintosh': ['10_15_7', '11_2_3'],
            'Linux': ['x86_64', 'aarch64']
        }
        
        os_type = random.choice(list(os_versions.keys()))
        os_ver = random.choice(os_versions[os_type])
        chrome_ver = random.choice(chrome_versions)
        
        if os_type == 'Windows':
            return f'Mozilla/5.0 (Windows NT {os_ver}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36'
        elif os_type == 'Macintosh':
            return f'Mozilla/5.0 (Macintosh; Intel Mac OS X {os_ver}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36'
        else:
            return f'Mozilla/5.0 (X11; Linux {os_ver}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36'
            
    def _generate_webgl_data(self) -> Dict:
        """生成WebGL指纹数据"""
        vendors = ['Google Inc.', 'Intel Inc.', 'NVIDIA Corporation', 'AMD']
        renderers = [
            'ANGLE (Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)',
            'ANGLE (NVIDIA GeForce GTX 1660 Direct3D11 vs_5_0 ps_5_0)',
            'Mesa DRI Intel(R) UHD Graphics 620 (KBL GT2)'
        ]
        
        return {
            "vendor": random.choice(vendors),
            "renderer": random.choice(renderers),
            "unmaskedVendor": random.choice(vendors),
            "unmaskedRenderer": random.choice(renderers),
            "extensions": self._generate_webgl_extensions()
        }
        
    def _generate_hardware_info(self) -> Dict:
        """生成硬件信息"""
        return {
            "deviceMemory": random.choice([4, 8, 16, 32]),
            "hardwareConcurrency": random.choice([4, 6, 8, 12, 16]),
            "platform": platform.system(),
            "cpuClass": cpuinfo.get_cpu_info()['brand_raw'],
            "deviceId": str(uuid.uuid4()),
            "maxTouchPoints": random.choice([0, 1, 2, 5, 10])
        } 