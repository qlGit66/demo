class ChaoXingAutoAnswer:
    def __init__(self, chaoxing_token=None, openai_api_key=None):
        self.chaoxing_token = chaoxing_token
        self.openai_api_key = openai_api_key
        self.token_usage = {
            'remaining': None,
            'warning_threshold': 50
        }
        
    def answer_question(self, question_element):
        """处理单个题目"""
        try:
            question_text = question_element.text
            question_type = self.get_question_type(question_element)
            
            # 1. 如果有token，优先尝试题库
            if self.chaoxing_token:
                answer = self.search_chaoxing_answer(question_text)
                if answer:
                    self.logger.info("从题库找到答案")
                    return self.submit_answer(question_element, answer)
            
            # 2. 题库没答案或token用完，使用AI
            if self.openai_api_key:
                self.logger.info("使用AI生成答案")
                answer = self.get_ai_answer(question_text, question_type)
                if answer:
                    return self.submit_answer(question_element, answer)
            
            self.logger.warning("未能获取答案")
            return False
            
        except Exception as e:
            self.logger.error(f"处理题目失败: {str(e)}")
            return False 