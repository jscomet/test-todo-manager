"""OpenCode CLI 封装 - 使用 serve + attach 模式"""
import subprocess
import tempfile
import os
import json
import time
from pathlib import Path
from typing import Optional

class OpenCodeClient:
    """OpenCode 客户端 - 使用 headless server 模式"""
    
    def __init__(self, server_url: str = "http://localhost:4096", timeout: int = 300):
        self.server_url = server_url
        self.timeout = timeout
        self.server_process = None
    
    def start_server(self) -> bool:
        """启动 headless OpenCode 服务器"""
        try:
            # 检查服务器是否已在运行
            import urllib.request
            try:
                urllib.request.urlopen(f"{self.server_url}/health", timeout=2)
                print(f"   OpenCode 服务器已在运行")
                return True
            except:
                pass
            
            # 启动服务器
            print(f"   启动 OpenCode 服务器...")
            self.server_process = subprocess.Popen(
                ["opencode", "serve", "--port", "4096"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, "OPENCODE_NON_INTERACTIVE": "1"}
            )
            
            # 等待服务器启动
            time.sleep(3)
            
            # 验证服务器是否启动成功
            try:
                urllib.request.urlopen(f"{self.server_url}/health", timeout=5)
                print(f"   服务器启动成功")
                return True
            except Exception as e:
                print(f"   服务器启动失败: {e}")
                return False
                
        except Exception as e:
            print(f"   启动服务器出错: {e}")
            return False
    
    def stop_server(self):
        """停止服务器"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None
    
    def execute(self, prompt: str) -> dict:
        """
        执行 Prompt - 使用 attach 模式
        
        Returns:
            {
                "success": bool,
                "output": str,
                "error": Optional[str]
            }
        """
        # 确保服务器在运行
        if not self.start_server():
            return {
                "success": False,
                "output": "",
                "error": "无法启动 OpenCode 服务器"
            }
        
        try:
            # 使用 attach 模式执行
            result = subprocess.run(
                ["opencode", "run", "--attach", self.server_url, prompt],
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
