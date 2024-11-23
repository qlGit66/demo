from dataclasses import dataclass
import yaml

@dataclass
class Config:
    openai_api_key: str
    chaoxing_token: str
    retry_times: int = 3
    delay_range: tuple = (1, 3)
    timeout: int = 30
    debug_mode: bool = False
    
    @classmethod
    def from_yaml(cls, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        return cls(**config_dict) 