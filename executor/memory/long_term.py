"""长期记忆 - 经验积累"""
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime

class LongTermMemory:
    """长期记忆管理"""
    
    def __init__(self, memory_file: str = "memory/experiences.json"):
        self.memory_file = Path(memory_file)
        self._ensure_dir()
        self.experiences = self._load()
    
    def _ensure_dir(self):
        """确保目录存在"""
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _load(self) -> List[Dict]:
        """加载经验"""
        if not self.memory_file.exists():
            return []
        
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save(self):
        """保存经验"""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.experiences, f, ensure_ascii=False, indent=2)
    
    def record(self, pattern: str, solution: str, success: bool):
        """记录经验"""
        experience = {
            "id": f"exp-{len(self.experiences)+1:03d}",
            "pattern": pattern,
            "solution": solution,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "count": 1
        }
        
        # 检查是否已存在相似经验
        for exp in self.experiences:
            if exp["pattern"] == pattern:
                exp["count"] += 1
                exp["timestamp"] = datetime.now().isoformat()
                self.save()
                return
        
        self.experiences.append(experience)
        self.save()
    
    def find_relevant(self, keyword: str) -> List[Dict]:
        """查找相关经验"""
        relevant = [
            exp for exp in self.experiences
            if keyword.lower() in exp["pattern"].lower()
        ]
        
        # 按成功率和次数排序
        relevant.sort(key=lambda x: (x["success"], x["count"]), reverse=True)
        
        return relevant[:3]
