import os
import sys
import platform
import subprocess
import shutil
import webbrowser
import urllib.parse
from urllib.parse import quote_plus
from typing import Dict, Any, List, Optional
from backend.core.config import settings
from backend.core.logging import logger

def open_chrome(url: str = None) -> bool:
    """
    Reliably opens Google Chrome on Windows.
    Checks direct Chrome installation paths first, then falls back gracefully across Windows Shell.
    """
    target = url.strip() if url else "https://www.google.com"
    
    # Ensure standard web scheme is present
    if not target.startswith(("http://", "https://")):
        target = f"https://{target}"

    # Common Windows Chrome installation locations
    chrome_paths = [
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
    ]

    # Method 1: Launch via direct Chrome executable path (guaranteed to launch actual Chrome)
    for path in chrome_paths:
        if os.path.isfile(path):
            try:
                subprocess.Popen([path, target])
                return True
            except Exception as e:
                logger.debug(f"Direct Chrome launch via {path} failed: {e}")
                continue

    # Method 2: Launch via Windows 'start chrome' command
    try:
        if os.system(f'start chrome "{target}"') == 0:
            return True
    except Exception as e:
        logger.debug(f"Windows start chrome failed: {e}")

    # Method 3: Direct Windows Shell launcher via os.startfile
    try:
        os.startfile(target)
        return True
    except Exception as e:
        logger.debug(f"Windows Shell startfile failed: {e}")

    # Method 4: Fall back to default system browser
    try:
        return webbrowser.open(target)
    except Exception as e:
        logger.error(f"All browser launch fallbacks failed: {e}")
        return False

def search_google(query: str) -> bool:
    encoded = urllib.parse.quote(query.strip())
    search_url = f"https://www.google.com/search?q={encoded}"
    return open_chrome(search_url)

ALLOWED_APPLICATIONS = {
    "notepad": ["notepad.exe"],
    "calc": ["calc.exe"],
    "calculator": ["calc.exe"],
    "paint": ["mspaint.exe"],
    "mspaint": ["mspaint.exe"],
    "explorer": ["explorer.exe"],
    "code": ["code.cmd"],
    "cmd": ["cmd.exe", "/c", "start"],
    "powershell": ["powershell.exe", "-NoExit"],
    "edge": ["start", "msedge"],
    "chrome": ["chrome.exe"],
    "google chrome": ["chrome.exe"],
    "google-chrome": ["chrome.exe"],
    "browser": ["chrome.exe"],
}

SAFE_DOMAINS = [
    "google.com", "github.com", "stackoverflow.com",
    "huggingface.co", "wikipedia.org", "python.org",
    "fastapi.tiangolo.com", "docs.streamlit.io", "threejs.org",
    "youtube.com", "classroom.google.com", "uidai.gov.in"
]

WEBSITE_SHORTCUTS = {
    "youtube": ("YouTube", "https://www.youtube.com"),
    "yt": ("YouTube", "https://www.youtube.com"),
    "google classroom": ("Google Classroom", "https://classroom.google.com"),
    "classroom": ("Google Classroom", "https://classroom.google.com"),
    "google": ("Google", "https://www.google.com"),
    "google search": ("Google", "https://www.google.com"),
    "aadhaar": ("UIDAI Aadhaar Official Portal", "https://uidai.gov.in"),
    "aadhaar card": ("UIDAI Aadhaar Official Portal", "https://uidai.gov.in"),
    "the aadhaar card official website": ("UIDAI Aadhaar Official Portal", "https://uidai.gov.in"),
    "aadhaar card official website": ("UIDAI Aadhaar Official Portal", "https://uidai.gov.in"),
    "uidai": ("UIDAI Aadhaar Official Portal", "https://uidai.gov.in"),
    "github": ("GitHub", "https://github.com"),
    "wikipedia": ("Wikipedia", "https://www.wikipedia.org"),
    "stackoverflow": ("Stack Overflow", "https://stackoverflow.com"),
    "reddit": ("Reddit", "https://www.reddit.com"),
    "linkedin": ("LinkedIn", "https://www.linkedin.com"),
    "twitter": ("X / Twitter", "https://x.com"),
    "x": ("X", "https://x.com"),
    "gmail": ("Gmail", "https://mail.google.com"),
    "chatgpt": ("ChatGPT", "https://chat.openai.com"),
    "netflix": ("Netflix", "https://www.netflix.com"),
    "whatsapp": ("WhatsApp Web", "https://web.whatsapp.com"),
    "whatsapp web": ("WhatsApp Web", "https://web.whatsapp.com"),
}

class DesktopControlIntegration:
    def __init__(self):
        self._chrome_path: Optional[str] = None
        self._chrome_registered: bool = False
        self._init_chrome_browser()

    def _init_chrome_browser(self) -> Optional[str]:
        """Discovers and registers the Google Chrome browser executable."""
        if self._chrome_path and os.path.isfile(self._chrome_path):
            return self._chrome_path

        candidates = [
            os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), r"Google\Chrome\Application\chrome.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"), r"Google\Chrome\Application\chrome.exe"),
            os.path.join(os.environ.get("LocalAppData", ""), r"Google\Chrome\Application\chrome.exe"),
        ]

        found_path = None
        for c in candidates:
            if os.path.isfile(c):
                found_path = c
                break

        if not found_path:
            # Query Windows Registry
            try:
                import winreg
                for reg_root in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
                    try:
                        with winreg.OpenKey(reg_root, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe") as key:
                            val, _ = winreg.QueryValueEx(key, "")
                            if os.path.isfile(val):
                                found_path = val
                                break
                    except Exception:
                        pass
                    if found_path:
                        break
            except Exception:
                pass

        if not found_path:
            found_path = shutil.which("chrome") or shutil.which("google-chrome")

        if found_path:
            self._chrome_path = found_path
            try:
                webbrowser.register("chrome", None, webbrowser.BackgroundBrowser(found_path))
                self._chrome_registered = True
                logger.info(f"Registered Google Chrome at: {found_path}")
            except Exception as e:
                logger.warning(f"Failed to register Chrome with webbrowser: {e}")
        else:
            logger.warning("Google Chrome executable not detected in standard system paths.")

        return found_path

    @property
    def chrome_path(self) -> Optional[str]:
        return self._chrome_path or self._init_chrome_browser()

    @staticmethod
    def get_system_diagnostics() -> Dict[str, Any]:
        """Collects safe local operating system telemetry."""
        return {
            "os": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor() or "Multi-Core x86_64",
            "python_version": platform.python_version(),
            "hostname": platform.node()
        }

    def open_chrome(self, url: Optional[str] = None, use_mcp: bool = False) -> Dict[str, Any]:
        """
        Direct Windows Shell launcher method delegating to open_chrome.
        Bypasses subprocess and path lookups entirely via Windows Shell.
        """
        target = url.strip() if url else "https://www.google.com"

        # Optional Chrome DevTools MCP automation if explicitly requested
        if use_mcp and url:
            try:
                from backend.integrations.chrome_mcp import chrome_mcp_client
                mcp_res = chrome_mcp_client.navigate(target)
                if mcp_res.get("success"):
                    logger.info(f"Dispatched URL via Chrome DevTools MCP: {target}")
                    return {
                        "success": True,
                        "action": "open_chrome",
                        "method": "chrome_devtools_mcp",
                        "target": target,
                        "output": f"Right away, Boss. Dispatched '{target}' via Chrome DevTools MCP.",
                        "requires_confirmation": False
                    }
            except Exception as e:
                logger.warning(f"Chrome DevTools MCP dispatch failed, falling back to launcher: {e}")

        # Execute direct Windows Shell launcher
        success = open_chrome(target)

        if success:
            if url:
                msg = f"Right away, Boss. Opened '{target}' in Google Chrome."
            else:
                msg = "Opening Chrome now, Boss. Google Chrome has been launched."
            return {
                "success": True,
                "action": "open_chrome",
                "target": target,
                "output": msg,
                "method": "windows_shell_startfile",
                "requires_confirmation": False
            }
        else:
            return {
                "success": False,
                "action": "open_chrome",
                "target": target,
                "output": "Boss, I was unable to locate Google Chrome on this system.",
                "method": "none",
                "requires_confirmation": False
            }

    def search_google(self, query: str) -> Dict[str, Any]:
        """
        Executes a Google search query directly in Google Chrome / default browser.
        """
        clean_query = query.strip()
        # Strip common conversational fluff
        for prefix in ["search for ", "search google for ", "search on google for ", "search ", "google search for ", "google "]:
            if clean_query.lower().startswith(prefix):
                clean_query = clean_query[len(prefix):].strip()
                break

        for suffix in [" on google", " in google", " using google", " in chrome", " on chrome"]:
            if clean_query.lower().endswith(suffix):
                clean_query = clean_query[:-len(suffix)].strip()
                break

        if not clean_query:
            clean_query = "Google"

        encoded = urllib.parse.quote(clean_query)
        search_url = f"https://www.google.com/search?q={encoded}"
        success = open_chrome(search_url)

        if success:
            return {
                "success": True,
                "action": "search_google",
                "target": clean_query,
                "output": f"Right away, Boss. Searching Google for '{clean_query}' in Chrome.",
                "requires_confirmation": False
            }
        else:
            return {
                "success": False,
                "action": "search_google",
                "target": clean_query,
                "output": f"Boss, I was unable to launch Google Chrome to search for '{clean_query}'.",
                "requires_confirmation": False
            }

    def open_website(self, site_query: str) -> Dict[str, Any]:
        """
        Opens a target website or recognized service in Google Chrome.
        """
        clean = site_query.strip().lower()
        # Remove leading 'open ' or 'launch '
        for prefix in ["open ", "launch ", "go to ", "navigate to "]:
            if clean.startswith(prefix):
                clean = clean[len(prefix):].strip()

        # Check website shortcuts
        if clean in WEBSITE_SHORTCUTS:
            name, url = WEBSITE_SHORTCUTS[clean]
            res = self.open_chrome(url)
            if res["success"]:
                res["output"] = f"Right away, Boss. Opening {name} in Google Chrome."
                res["target"] = url
                res["action"] = "open_website"
            return res

        # Check if query matches a domain pattern
        if any(clean.endswith(tld) or f"{tld}/" in clean for tld in [".com", ".org", ".net", ".edu", ".gov", ".io", ".in", ".co", ".ai"]):
            url = clean if clean.startswith("http") else f"https://{clean}"
            res = self.open_chrome(url)
            if res["success"]:
                res["output"] = f"Right away, Boss. Navigating to '{url}' in Google Chrome."
                res["target"] = url
                res["action"] = "open_website"
            return res

        # Otherwise perform Google Search for the term
        return self.search_google(site_query)

    def execute_action(self, action: str, target: str, confirmed: bool = False) -> Dict[str, Any]:
        """
        Executes an allowlisted desktop operation with strict safety validation.
        """
        if not settings.desktop_control_enabled:
            return {
                "success": False,
                "action": action,
                "target": target,
                "output": "Boss, desktop automation is disabled in configuration (DESKTOP_CONTROL_ENABLED=false).",
                "requires_confirmation": False
            }

        action_clean = action.strip().lower()
        target_clean = target.strip()

        # Action: System Info
        if action_clean in ["system_info", "diagnostics", "status"]:
            diag = self.get_system_diagnostics()
            msg = (
                f"Boss, system diagnostics reported:\n"
                f"- OS: {diag['os']} {diag['os_release']} ({diag['architecture']})\n"
                f"- Node: {diag['hostname']}\n"
                f"- Python: {diag['python_version']}\n"
                f"- CPU: {diag['processor']}"
            )
            return {
                "success": True,
                "action": action,
                "target": target,
                "output": msg,
                "requires_confirmation": False
            }

        # Action: Chrome / Browser Operations
        if action_clean in ["open_chrome", "chrome"]:
            return self.open_chrome(target_clean if target_clean and target_clean.lower() != "chrome" else None)

        if action_clean in ["search_google", "google_search", "google"]:
            return self.search_google(target_clean)

        if action_clean in ["open_website", "open_site", "website"]:
            return self.open_website(target_clean)

        # Action: Chrome DevTools MCP Operations
        if action_clean in ["mcp_navigate", "mcp_open"]:
            return self.open_chrome(target_clean, use_mcp=True)

        if action_clean in ["mcp_status"]:
            from backend.integrations.chrome_mcp import chrome_mcp_client
            status = chrome_mcp_client.get_status()
            msg = f"Boss, Chrome DevTools MCP status: Connected={status['connected']}, Tools={status['tools_count']}"
            return {
                "success": True,
                "action": action,
                "target": target,
                "output": msg,
                "details": status,
                "requires_confirmation": False
            }


        # Action: Open Application
        if action_clean == "open_app":
            app_key = target_clean.lower()

            # Dedicated routing for Chrome
            if app_key in ["chrome", "google chrome", "google-chrome", "browser"]:
                return self.open_chrome()

            if app_key not in ALLOWED_APPLICATIONS:
                allowed_list = ", ".join(ALLOWED_APPLICATIONS.keys())
                return {
                    "success": False,
                    "action": action,
                    "target": target,
                    "output": f"Boss, '{target}' is not in the approved applications allowlist ({allowed_list}).",
                    "requires_confirmation": False
                }

            cmd = ALLOWED_APPLICATIONS[app_key]
            try:
                if sys.platform == "win32":
                    subprocess.Popen(cmd, shell=True)
                else:
                    subprocess.Popen(cmd)

                logger.info(f"Launched application '{app_key}' via desktop integration.")
                return {
                    "success": True,
                    "action": action,
                    "target": target,
                    "output": f"Right away, Boss. Launched '{target}' successfully.",
                    "requires_confirmation": False
                }
            except Exception as e:
                logger.error(f"Failed to launch app '{target}': {e}")
                return {
                    "success": False,
                    "action": action,
                    "target": target,
                    "output": f"Boss, encountered an error launching '{target}': {str(e)}",
                    "requires_confirmation": False
                }

        # Action: Open Website / URL
        if action_clean == "open_url":
            # Direct to Chrome handler to maintain consistent user browser preference
            return self.open_chrome(target_clean)

        # Destructive or Unapproved Action
        if any(term in action_clean or term in target_clean.lower() for term in ["shutdown", "restart", "delete", "rmdir", "format"]):
            if not confirmed:
                return {
                    "success": False,
                    "action": action,
                    "target": target,
                    "output": f"Boss, '{action} {target}' is a critical system action requiring explicit tactical confirmation.",
                    "requires_confirmation": True
                }

        return {
            "success": False,
            "action": action,
            "target": target,
            "output": f"Boss, action '{action}' is not supported by current tactical protocols.",
            "requires_confirmation": False
        }

desktop_control = DesktopControlIntegration()

