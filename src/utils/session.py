import json
import os
from datetime import datetime
from typing import Dict, Optional

class AnswerSession:
    def __init__(self, logger):
        self.logger = logger
        self.session_file = 'data/current_session.json'
        self.session_data = self._load_session()
        
    def _load_session(self) -> Dict:
        """加载会话数据"""
        if not os.path.exists(self.session_file):
            return self._create_new_session()
            
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载会话失败: {str(e)}")
            return self._create_new_session()
            
    def _create_new_session(self) -> Dict:
        """创建新会话"""
        return {
            "session_id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "start_time": datetime.now().isoformat(),
            "status": "active",
            "questions_answered": 0,
            "correct_answers": 0,
            "current_question": None,
            "progress": []
        }
        
    def save_session(self):
        """保存会话数据"""
        try:
            os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存会话失败: {str(e)}")
            
    def start_question(self, question_data: Dict):
        """开始新的题目"""
        self.session_data["current_question"] = {
            "start_time": datetime.now().isoformat(),
            "question_data": question_data,
            "status": "in_progress"
        }
        self.save_session()
        
    def complete_question(self, answer: str, is_correct: Optional[bool] = None):
        """完成当前题目"""
        if self.session_data["current_question"]:
            question_record = self.session_data["current_question"]
            question_record.update({
                "end_time": datetime.now().isoformat(),
                "answer": answer,
                "is_correct": is_correct,
                "status": "completed"
            })
            
            self.session_data["progress"].append(question_record)
            self.session_data["questions_answered"] += 1
            if is_correct:
                self.session_data["correct_answers"] += 1
                
            self.session_data["current_question"] = None
            self.save_session()
            
    def pause_session(self):
        """暂停会话"""
        self.session_data["status"] = "paused"
        self.session_data["pause_time"] = datetime.now().isoformat()
        self.save_session()
        
    def resume_session(self):
        """恢复会话"""
        self.session_data["status"] = "active"
        self.session_data["resume_time"] = datetime.now().isoformat()
        self.save_session()
        
    def end_session(self):
        """结束会话"""
        self.session_data["status"] = "completed"
        self.session_data["end_time"] = datetime.now().isoformat()
        self.save_session()
        
        # 保存会话历史
        self._save_to_history()
        
    def _save_to_history(self):
        """保存到会话历史"""
        history_file = 'data/session_history.json'
        try:
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            else:
                history = []
                
            history.append(self.session_data)
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存会话历史失败: {str(e)}")
            
    def get_progress(self) -> Dict:
        """获取答题进度"""
        return {
            "total_questions": self.session_data["questions_answered"],
            "correct_answers": self.session_data["correct_answers"],
            "accuracy_rate": (self.session_data["correct_answers"] / 
                            self.session_data["questions_answered"]
                            if self.session_data["questions_answered"] > 0 else 0),
            "status": self.session_data["status"]
        } 