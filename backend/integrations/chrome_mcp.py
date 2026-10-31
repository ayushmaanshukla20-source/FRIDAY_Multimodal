"""
FRIDAY Multimodal Voice Assistant
Author: Ayushmaan Shukla
Roll / Enrollment No.: 202510101240164
Department: Computer Science & Engineering (AI & ML)
Institution: Shri Ramswaroop Memorial University
Notice: This project is strictly for academic evaluation. 
        Unauthorized reproduction or submission is a violation of academic integrity.
"""
import os
import sys
import json
import shutil
import subprocess
import threading
from typing import Dict, Any, List, Optional
from backend.core.logging import logger

class ChromeDevToolsMCPClient:
    """
    Direct Python client for the Chrome DevTools Model Context Protocol (MCP) server.
    Spawns 'npx chrome-devtools-mcp@latest' and communicates via stdio JSON-RPC 2.0.
    Provides advanced browser automation, navigation, script evaluation, and screenshots.
    """

    def __init__(self, command: str = "npx", args: Optional[List[str]] = None):
        self.command = command
        self.args = args or ["chrome-devtools-mcp@latest", "--no-usage-statistics"]
        self._proc: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()
        self._req_id = 0
        self._tools: List[Dict[str, Any]] = []
        self._is_connected = False
        self._server_info: Dict[str, Any] = {}

    def _get_next_id(self) -> int:
        self._req_id += 1
        return self._req_id

    def is_npx_available(self) -> bool:
        """Verifies if npx or node is installed and accessible in the system path."""
        candidates = ["npx.cmd", "npx", "npx.exe"] if sys.platform == "win32" else ["npx"]
        for c in candidates:
            if shutil.which(c):
                return True
        return False

    def connect(self, timeout_sec: int = 15) -> bool:
        """
        Initializes connection to the Chrome DevTools MCP server via stdio.
        """
        with self._lock:
            if self._is_connected and self._proc and self._proc.poll() is None:
                return True

            if not self.is_npx_available():
                logger.warning("npx is not available in system PATH. Cannot launch Chrome DevTools MCP server.")
                return False

            cmd_bin = shutil.which("npx.cmd") if sys.platform == "win32" else shutil.which("npx")
            full_cmd = [cmd_bin or "npx", "-y"] + self.args

            try:
                logger.info(f"Spawning Chrome DevTools MCP process: {' '.join(full_cmd)}")
                self._proc = subprocess.Popen(
                    full_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )

                # Step 1: Send initialize request
                init_id = self._get_next_id()
                init_payload = {
                    "jsonrpc": "2.0",
                    "id": init_id,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "friday-ai-assistant",
                            "version": "1.0.0"
                        }
                    }
                }
                self._proc.stdin.write(json.dumps(init_payload) + "\n")
                self._proc.stdin.flush()

                # Read initialize response
                init_raw = self._proc.stdout.readline()
                if not init_raw:
                    logger.error("Empty response received from Chrome DevTools MCP server during initialization.")
                    return False

                init_data = json.loads(init_raw)
                if "error" in init_data:
                    logger.error(f"MCP Initialize Error: {init_data['error']}")
                    return False

                self._server_info = init_data.get("result", {}).get("serverInfo", {})
                logger.info(f"Connected to MCP Server: {self._server_info.get('name')} v{self._server_info.get('version')}")

                # Step 2: Send initialized notification
                self._proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
                self._proc.stdin.flush()

                # Step 3: Fetch available tools list
                list_id = self._get_next_id()
                self._proc.stdin.write(json.dumps({
                    "jsonrpc": "2.0",
                    "id": list_id,
                    "method": "tools/list",
                    "params": {}
                }) + "\n")
                self._proc.stdin.flush()

                tools_raw = self._proc.stdout.readline()
                if tools_raw:
                    tools_data = json.loads(tools_raw)
                    self._tools = tools_data.get("result", {}).get("tools", [])
                    logger.info(f"Loaded {len(self._tools)} MCP tools from Chrome DevTools server.")

                self._is_connected = True
                return True

            except Exception as e:
                logger.error(f"Failed to start Chrome DevTools MCP client: {e}")
                self.disconnect()
                return False

    def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes a named MCP tool on the Chrome DevTools server.
        """
        if not self._is_connected or not self._proc or self._proc.poll() is not None:
            if not self.connect():
                return {"success": False, "error": "Chrome DevTools MCP server is not connected."}

        with self._lock:
            try:
                call_id = self._get_next_id()
                payload = {
                    "jsonrpc": "2.0",
                    "id": call_id,
                    "method": "tools/call",
                    "params": {
                        "name": name,
                        "arguments": arguments or {}
                    }
                }
                self._proc.stdin.write(json.dumps(payload) + "\n")
                self._proc.stdin.flush()

                resp_line = self._proc.stdout.readline()
                if not resp_line:
                    return {"success": False, "error": "No response received from MCP server."}

                data = json.loads(resp_line)
                if "error" in data:
                    return {"success": False, "error": data["error"]}

                return {"success": True, "result": data.get("result", {})}
            except Exception as e:
                logger.error(f"Error calling MCP tool '{name}': {e}")
                return {"success": False, "error": str(e)}

    def navigate(self, url: str) -> Dict[str, Any]:
        """
        Navigates Chrome to the target URL using MCP 'new_page' or 'navigate_page'.
        """
        target_url = url.strip()
        if not target_url.startswith("http://") and not target_url.startswith("https://"):
            target_url = f"https://{target_url}"

        # Prefer new_page if available, fallback to navigate_page
        res = self.call_tool("new_page", {"url": target_url})
        if not res.get("success"):
            res = self.call_tool("navigate_page", {"url": target_url})
        return res

    def search_google(self, query: str) -> Dict[str, Any]:
        """
        Executes a Google Search using the Chrome DevTools MCP server.
        """
        from urllib.parse import quote_plus
        encoded = quote_plus(query.strip())
        search_url = f"https://www.google.com/search?q={encoded}"
        return self.navigate(search_url)

    def take_screenshot(self) -> Dict[str, Any]:
        """
        Captures a viewport screenshot of the current page using Chrome DevTools MCP.
        """
        return self.call_tool("take_screenshot", {})

    def get_status(self) -> Dict[str, Any]:
        """
        Reports connection telemetry and available tool roster.
        """
        connected = bool(self._is_connected and self._proc and self._proc.poll() is None)
        return {
            "configured": True,
            "connected": connected,
            "npx_available": self.is_npx_available(),
            "server_info": self._server_info,
            "tools_count": len(self._tools),
            "tool_names": [t.get("name") for t in self._tools]
        }

    def disconnect(self):
        """Terminates the MCP server process cleanly."""
        with self._lock:
            self._is_connected = False
            if self._proc:
                try:
                    self._proc.terminate()
                    self._proc.wait(timeout=2)
                except Exception:
                    try:
                        self._proc.kill()
                    except Exception:
                        pass
                self._proc = None

chrome_mcp_client = ChromeDevToolsMCPClient()

