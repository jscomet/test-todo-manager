"""OpenCode CLI 封装"""
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Optional

class OpenCodeClient:
    """OpenCode 客户端"""
    
    def __init__(self, timeout: int = 300):
        self.timeout = timeout
    
    def execute(self, prompt: str) -> dict:
        """
        执行 Prompt
        
        Returns:
            {
                "success": bool,
                "output": str,
                "error": Optional[str]
            }
        """
        # 创建临时 prompt 文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(prompt)
            prompt_file = f.name
        
        try:
            # 调用 OpenCode
            result = subprocess.run(
                ["opencode", "run", prompt_file],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"Timeout after {self.timeout}s"
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e)
            }
        finally:
            os.unlink(prompt_file)
