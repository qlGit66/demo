import dashscope
from dashscope import Generation
from typing import Optional

class AIHandler:
    def __init__(self, api_key: str):
        self.api_key = api_key
        dashscope.api_key = api_key
        
    def get_answer(self, question_text: str, question_type: str) -> Optional[str]:
        """使用星火模型生成答案"""
        try:
            prompt = f"""
            请回答以下{question_type}题，只需要给出答案，不需要解释：
            问题：{question_text}
            """
            
            response = Generation.call(
                model='qwen-turbo',  # 使用通义千问模型
                prompt=prompt,
                max_tokens=2048,
                temperature=0.1,  # 降低随机性，使答案更确定
                result_format='message'
            )
            
            if response.status_code == 200:
                return response.output.text.strip()
            else:
                return None
                
        except Exception as e:
            print(f"AI回答出错：{str(e)}")
            return None 