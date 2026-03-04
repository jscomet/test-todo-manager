"""短期记忆 - 当前会话状态"""
import json
from pathlib import Path
from typing import List, Dict, Optional

class ShortTermMemory:
    """短期记忆管理"""
    
    def __init__(self, memory_file: str = "memory/context.json"):
        self.memory_file = Path(memory_file)
        self._ensure_dir()
    
    def _ensure_dir(self):
        """确保目录存在"""
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> Dict:
        """加载当前会话状态"""
        if not self.memory_file.exists():
            return {
                "current_task": None,
                "last_thinking": None,
                "recent_experiences": []
            }
        
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save(self, data: Dict):
        """保存会话状态"""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_recent_thinking(self, count: int = 2) -> List[str]:
        """获取最近 N 个思考记录"""
        thinking_dir = Path("thinking")
        if not thinking_dir.exists():
            return []
        
        # 按修改时间排序
        files = sorted(thinking_dir.glob("task-*.md"), 
                      key=lambda x: x.stat().st_mtime, 
                      reverse=True)
        
        return [str(f) for f in files[:count]]
