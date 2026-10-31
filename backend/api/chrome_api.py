import os
import re
import urllib.parse
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.integrations.desktop_control import open_chrome, WEBSITE_SHORTCUTS
from backend.core.logging import logger

router = APIRouter(prefix="/api/chrome", tags=["Chrome Automation"])

class ChromeCommandRequest(BaseModel):
    command: Optional[str] = None
    action: Optional[str] = None
    query: Optional[str] = None
    url: Optional[str] = None

class ChromeCommandResponse(BaseModel):
    success: bool
    action: str
    message: str
    details: Dict[str, Any] = {}

WEBSITE_DOMAINS = {
    "youtube": ("YouTube", "https://www.youtube.com"),
    "yt": ("YouTube", "https://www.youtube.com"),
    "github": ("GitHub", "https://www.github.com"),
    "gmail": ("Gmail", "https://mail.google.com"),
    "google": ("Google", "https://www.google.com"),
    "google search": ("Google", "https://www.google.com"),
    "google classroom": ("Google Classroom", "https://classroom.google.com"),
    "classroom": ("Google Classroom", "https://classroom.google.com"),
    "chatgpt": ("ChatGPT", "https://chat.openai.com"),
    "reddit": ("Reddit", "https://www.reddit.com"),
    "stackoverflow": ("Stack Overflow", "https://stackoverflow.com"),
    "wikipedia": ("Wikipedia", "https://www.wikipedia.org"),
    "twitter": ("X / Twitter", "https://x.com"),
    "x": ("X", "https://x.com"),
    "netflix": ("Netflix", "https://www.netflix.com"),
    "linkedin": ("LinkedIn", "https://www.linkedin.com"),
    "whatsapp": ("WhatsApp Web", "https://web.whatsapp.com"),
    "whatsapp web": ("WhatsApp Web", "https://web.whatsapp.com"),
}

@router.post("", response_model=ChromeCommandResponse)
@router.post("/", response_model=ChromeCommandResponse)
def execute_chrome_command(req: ChromeCommandRequest):
    """
    Executes Chrome automation commands:
    - Search queries: "search python tutorials on chrome", "google the weather"
    - Open websites: "open youtube", "open github", "open gmail"
    - Tab & window controls: "new tab", "close tab", "minimize", "maximize", "refresh"
    """
    raw_cmd = (req.command or "").strip()
    cmd_lower = raw_cmd.lower()
    action = (req.action or "").lower().strip()
    query = (req.query or "").strip()
    url = (req.url or "").strip()

    logger.info(f"Received Chrome automation directive: cmd='{raw_cmd}', action='{action}', query='{query}'")

    # 1. TAB & WINDOW ACTIONS (Hotkeys via pyautogui)
    is_tab_action = False
    tab_action_type = None

    if action in ["new_tab", "close_tab", "reopen_tab", "next_tab", "prev_tab", "minimize", "maximize", "refresh", "scroll_down", "scroll_up"]:
        is_tab_action = True
        tab_action_type = action
    elif re.search(r"\b(?:new\s+tab|open\s+(?:a\s+)?new\s+tab)\b", cmd_lower):
        is_tab_action = True
        tab_action_type = "new_tab"
    elif re.search(r"\b(?:close\s+tab|close\s+(?:the\s+)?tab|close\s+this\s+tab)\b", cmd_lower):
        is_tab_action = True
        tab_action_type = "close_tab"
    elif re.search(r"\b(?:reopen\s+tab|restore\s+tab)\b", cmd_lower):
        is_tab_action = True
        tab_action_type = "reopen_tab"
    elif re.search(r"\b(?:next\s+tab|switch\s+tab)\b", cmd_lower):
        is_tab_action = True
        tab_action_type = "next_tab"
    elif re.search(r"\b(?:previous\s+tab|prev\s+tab)\b", cmd_lower):
        is_tab_action = True
        tab_action_type = "prev_tab"
    elif re.search(r"\b(?:minimize\s+window|minimize\s+chrome|minimize)\b", cmd_lower):
        is_tab_action = True
        tab_action_type = "minimize"
    elif re.search(r"\b(?:maximize\s+window|maximize\s+chrome|maximize)\b", cmd_lower):
        is_tab_action = True
        tab_action_type = "maximize"
    elif re.search(r"\b(?:refresh\s+page|reload\s+page|refresh|reload)\b", cmd_lower):
        is_tab_action = True
        tab_action_type = "refresh"
    elif re.search(r"\b(?:scroll\s+down|page\s+down)\b", cmd_lower):
        is_tab_action = True
        tab_action_type = "scroll_down"
    elif re.search(r"\b(?:scroll\s+up|page\s+up)\b", cmd_lower):
        is_tab_action = True
        tab_action_type = "scroll_up"

    if is_tab_action and tab_action_type:
        try:
            import pyautogui
            pyautogui.FAILSAFE = False

            if tab_action_type == "new_tab":
                pyautogui.hotkey("ctrl", "t")
                msg = "Opened a new tab in Chrome, Boss."
            elif tab_action_type == "close_tab":
                pyautogui.hotkey("ctrl", "w")
                msg = "Closed the active Chrome tab, Boss."
            elif tab_action_type == "reopen_tab":
                pyautogui.hotkey("ctrl", "shift", "t")
                msg = "Reopened the recently closed tab, Boss."
            elif tab_action_type == "next_tab":
                pyautogui.hotkey("ctrl", "tab")
                msg = "Switched to the next tab, Boss."
            elif tab_action_type == "prev_tab":
                pyautogui.hotkey("ctrl", "shift", "tab")
                msg = "Switched to the previous tab, Boss."
            elif tab_action_type == "minimize":
                pyautogui.hotkey("win", "down")
                msg = "Minimized active window, Boss."
            elif tab_action_type == "maximize":
                pyautogui.hotkey("win", "up")
                msg = "Maximized active window, Boss."
            elif tab_action_type == "refresh":
                pyautogui.hotkey("ctrl", "r")
                msg = "Refreshed the active page, Boss."
            elif tab_action_type == "scroll_down":
                pyautogui.scroll(-600)
                msg = "Scrolled down page, Boss."
            elif tab_action_type == "scroll_up":
                pyautogui.scroll(600)
                msg = "Scrolled up page, Boss."
            else:
                msg = f"Executed {tab_action_type} hotkey action."

            return ChromeCommandResponse(
                success=True,
                action=tab_action_type,
                message=msg,
                details={"method": "pyautogui_hotkey"}
            )
        except Exception as e:
            logger.error(f"pyautogui hotkey execution failed: {e}")
            return ChromeCommandResponse(
                success=False,
                action=tab_action_type,
                message=f"Boss, hotkey action failed: {str(e)}",
                details={"error": str(e)}
            )

    # 2. SEARCH QUERIES
    is_search = False
    search_query = query

    if action in ["search", "search_google", "google"]:
        is_search = True
        search_query = query or raw_cmd
    else:
        # Pattern match search directives
        m_search = re.search(
            r"^(?:search\s+for|search|find|google)\s+(.+?)(?:\s+(?:on|in|using)\s+(?:google|chrome))?$",
            cmd_lower
        )
        if not m_search:
            m_search = re.search(r"^(?:search\s+google\s+for|google\s+search\s+for|google\s+search)\s+(.+)$", cmd_lower)
        if not m_search and "search" in cmd_lower:
            m_search = re.search(r"\bsearch\s+(.+?)(?:\s+in\s+chrome|\s+on\s+chrome|\s+on\s+google)?\b", cmd_lower)

        if m_search:
            is_search = True
            search_query = m_search.group(1).strip()
            # Clean trailing fluff
            search_query = re.sub(r"\s+on\s+(?:google|chrome)$", "", search_query, flags=re.IGNORECASE).strip()
            search_query = re.sub(r"\s+in\s+(?:google|chrome)$", "", search_query, flags=re.IGNORECASE).strip()

    if is_search and search_query:
        encoded = urllib.parse.quote(search_query)
        search_url = f"https://www.google.com/search?q={encoded}"
        success = open_chrome(search_url)

        msg = f"Searching Google for '{search_query}' in Chrome now, Boss." if success else "Boss, I was unable to open Chrome for the search."
        return ChromeCommandResponse(
            success=success,
            action="search",
            message=msg,
            details={"query": search_query, "url": search_url}
        )

    # 3. DIRECT WEBSITES & URL NAVIGATION
    target_site = url
    site_name = None

    if not target_site:
        # Check explicit action
        if action in ["open_website", "navigate"] and (query or url):
            target_site = url or query
        else:
            # Pattern match "open <website>"
            m_site = re.search(r"^(?:open|launch|go\s+to|navigate\s+to)\s+(?:the\s+)?(.+?)(?:\s+(?:website|site|portal))?$", cmd_lower)
            if m_site:
                target_site = m_site.group(1).strip()

    if target_site:
        clean_site = target_site.lower().strip()

        # Check domain dictionary
        if clean_site in WEBSITE_DOMAINS:
            name, dest_url = WEBSITE_DOMAINS[clean_site]
            success = open_chrome(dest_url)
            msg = f"Opening {name} in Chrome now, Boss." if success else f"Boss, unable to launch Chrome for {name}."
            return ChromeCommandResponse(
                success=success,
                action="open_website",
                message=msg,
                details={"name": name, "url": dest_url}
            )

        # Check for TLD (e.g. reddit.com, news.ycombinator.com)
        if any(clean_site.endswith(tld) or f"{tld}/" in clean_site for tld in [".com", ".org", ".net", ".edu", ".gov", ".io", ".in", ".co", ".ai"]):
            dest_url = clean_site if clean_site.startswith(("http://", "https://")) else f"https://{clean_site}"
            success = open_chrome(dest_url)
            msg = f"Navigating to {dest_url} in Chrome now, Boss." if success else f"Boss, unable to open {dest_url}."
            return ChromeCommandResponse(
                success=success,
                action="open_website",
                message=msg,
                details={"url": dest_url}
            )

    # 4. OPEN CHROME ITSELF
    if action == "open_chrome" or re.search(r"^(?:open|launch|start)\s+(?:google\s+chrome|chrome|browser)$", cmd_lower):
        success = open_chrome("https://www.google.com")
        msg = "Opening Google Chrome now, Boss." if success else "Boss, unable to launch Google Chrome."
        return ChromeCommandResponse(
            success=success,
            action="open_chrome",
            message=msg,
            details={"url": "https://www.google.com"}
        )

    # 5. Default fallback: treat as search
    if raw_cmd:
        encoded = urllib.parse.quote(raw_cmd)
        search_url = f"https://www.google.com/search?q={encoded}"
        success = open_chrome(search_url)
        return ChromeCommandResponse(
            success=success,
            action="search",
            message=f"Searching Google for '{raw_cmd}' in Chrome, Boss.",
            details={"query": raw_cmd, "url": search_url}
        )

    return ChromeCommandResponse(
        success=False,
        action="none",
        message="No valid Chrome automation directive recognized, Boss.",
        details={}
    )

