"""思考记录管理"""
from pathlib import Path
from datetime import datetime

class ThinkingRecorder:
    """思考记录器"""
    
    def __init__(self, thinking_dir: str = "thinking"):
        self.thinking_dir = Path(thinking_dir)
        self.thinking_dir.mkdir(exist_ok=True)
    
    def save(self, task, output: str):
        """保存思考记录"""
        # 生成文件名
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" 
                           for c in task.objective[:30])
        filename = f"task-{task.id}-{safe_name}.md"
        filepath = self.thinking_dir / filename
        
        # 构建内容
        content = f"""# 任务 {task.id} 思考记录

**任务**: {task.objective}  
**时间**: {datetime.now().isoformat()}  
**状态**: {'成功' if 'success' in str(output).lower() else '失败'}

---

## 执行输出

```
{output[:5000] if output else '无输出'}
```

---

*记录时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        
        # 写入文件
        filepath.write_text(content, encoding='utf-8')
        print(f"📝 保存思考记录: {filepath}")
