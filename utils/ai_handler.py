from typing import Optional
from .spark_api import SparkAPI

class AIHandler:
    def __init__(self, app_id: str, api_key: str, api_secret: str):
        self.spark = SparkAPI(app_id, api_key, api_secret)
        
    def get_answer(self, question_text: str, question_type: str) -> Optional[str]:
        """使用星火模型生成答案"""
        try:
            prompt = f"""
            请回答以下{question_type}题，只需要给出答案，不需要解释：
            问题：{question_text}
            """
            
            response = self.spark.get_answer(prompt)
            return response.strip() if response else None
                
        except Exception as e:
            print(f"AI回答出错：{str(e)}")
            return None