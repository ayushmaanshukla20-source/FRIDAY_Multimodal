"""
FRIDAY Multimodal Voice Assistant
Author: Ayushmaan Shukla
Roll / Enrollment No.: 202510101240164
Department: Computer Science & Engineering (AI & ML)
Institution: Shri Ramswaroop Memorial University
Notice: This project is strictly for academic evaluation. 
        Unauthorized reproduction or submission is a violation of academic integrity.
"""
import re
from dataclasses import dataclass
from typing import Optional, Dict, Any
from backend.integrations.desktop_control import desktop_control
from backend.integrations.music_player import music_player
from backend.core.logging import logger

@dataclass
class IntentResult:
    is_handled: bool
    domain: str  # "music", "chrome", "desktop", "none"
    action: str
    response_message: str
    details: Dict[str, Any]

class IntentService:
    """
    Direct tactical intent parser and router for system-level voice & text commands.
    Cleanly separates intents into:
    1. Music: play, pause, resume, stop, skip, volume controls (100% free streaming)
    2. Browser: open website shortcuts, open Chrome, Google search
    3. Desktop/System: allowlisted desktop applications and diagnostics
    4. AI Conversation: passes through to RAG and conversational LLM
    """

    def normalize_command(self, raw_cmd: str) -> str:
        """
        Normalizes voice input by repeatedly stripping wake words, assistant names,
        conversational prefixes, and trailing politeness tokens.
        """
        cmd = raw_cmd.strip()
        cmd = re.sub(r"[.!?,]+$", "", cmd).strip()
        cmd_lower = cmd.lower()

        prefix_patterns = [
            r"^(?:hey|ok|okay|hi|hello|yo)\s+(?:friday|jarvis|computer)\b[,:\s]*",
            r"^(?:friday|jarvis|f\.r\.i\.d\.a\.y\.|computer)\b[,:\s]*",
            r"^(?:open|launch)\s+(?:friday|jarvis)\b[,:\s]*",
            r"^(?:please|kindly)\s+",
            r"^(?:can\s+you|could\s+you|would\s+you|will\s+you)\s+(?:please\s+)?(?:help\s+me\s+to\s+)?",
            r"^(?:i\s+want\s+you\s+to|i\s+want\s+to|help\s+me\s+to|tell\s+me\s+to|just)\s+",
        ]

        changed = True
        iterations = 0
        while changed and iterations < 6:
            changed = False
            iterations += 1
            for pat in prefix_patterns:
                new_cmd = re.sub(pat, "", cmd_lower, flags=re.IGNORECASE).strip()
                if new_cmd != cmd_lower:
                    cmd_lower = new_cmd
                    changed = True

        # Strip trailing polite fluff
        cmd_lower = re.sub(r"\s+(?:please|now|for\s+me|thanks|thank\s+you)$", "", cmd_lower, flags=re.IGNORECASE).strip()
        return cmd_lower

    def detect_and_execute(self, command: str) -> IntentResult:
        cmd_raw = command.strip()
        cmd_lower = self.normalize_command(cmd_raw)

        # ----------------------------------------------------------------------
        # DOMAIN 0: CREATOR & IDENTITY DIRECTIVE
        # ----------------------------------------------------------------------
        if re.search(r"\b(?:who\s+(?:created|made|built|engineered|developed|coded|programmed)\s+(?:you|friday)|who\s+is\s+your\s+(?:creator|maker|developer|author|engineer|architect)|who\s+designed\s+you)\b", cmd_lower) or \
           re.search(r"^(?:who\s+created\s+you|who\s+made\s+you|who\s+built\s+you|your\s+creator|who\s+is\s+your\s+creator)$", cmd_lower):
            creator_msg = "I was created and engineered by Ayushmaan Shukla. He designed my architecture, built my 3D cybernetic interface, and brought all my productivity and automation subsystems to life."
            logger.info("Executed intent: Creator Identity (Ayushmaan Shukla)")
            return IntentResult(
                is_handled=True,
                domain="identity",
                action="creator_identity",
                response_message=creator_msg,
                details={"creator": "Ayushmaan Shukla"}
            )

        # ----------------------------------------------------------------------
        # DOMAIN 1: MUSIC PLAYBACK (100% Free YouTube Streaming Engine)
        # ----------------------------------------------------------------------

        # 1.1 Stop Music / Stop Playback / Stop
        if re.search(r"^(?:stop\s+music|stop\s+the\s+music|stop\s+song|stop\s+playing|stop\s+playback|stop)$", cmd_lower) or \
           re.search(r"\b(?:stop\s+music|stop\s+the\s+music|stop\s+playback)\b", cmd_lower):
            res = music_player.stop()
            logger.info("Executed intent: Music Stop")
            return IntentResult(
                is_handled=True,
                domain="music",
                action="stop",
                response_message=res.get("message", "Right away, Boss. Music playback stopped."),
                details=res
            )

        # 1.2 Pause Music / Pause Spotify / Pause
        if re.search(r"^(?:pause\s+music|pause\s+the\s+music|pause\s+the\s+song|pause\s+playback|pause|pause\s+spotify)$", cmd_lower) or \
           re.search(r"\b(?:pause\s+music|pause\s+the\s+music|pause\s+playback|pause\s+spotify)\b", cmd_lower):
            res = music_player.pause()
            logger.info("Executed intent: Music Pause")
            msg = "Right away, Boss. Paused Spotify playback." if "spotify" in cmd_lower else "Right away, Boss. Paused music playback."
            return IntentResult(
                is_handled=True,
                domain="music",
                action="pause",
                response_message=msg,
                details=res
            )

        # 1.3 Resume Music / Continue Playing / Unpause / Resume
        if re.search(r"^(?:resume\s+music|resume\s+the\s+music|resume\s+the\s+song|resume\s+playback|resume|unpause\s+music|unpause|continue\s+playing|continue\s+music|resume\s+spotify)$", cmd_lower) or \
           re.search(r"\b(?:resume\s+music|resume\s+the\s+music|continue\s+playing|resume\s+spotify)\b", cmd_lower):
            res = music_player.resume()
            logger.info("Executed intent: Music Resume")
            msg = "Right away, Boss. Resumed Spotify playback." if "spotify" in cmd_lower else "Right away, Boss. Resumed music playback."
            return IntentResult(
                is_handled=True,
                domain="music",
                action="resume",
                response_message=msg,
                details=res
            )

        # 1.4 Skip / Next Track / Next Song
        if re.search(r"^(?:play\s+(?:the\s+)?next\s+song|play\s+next|next\s+song|next\s+track|skip\s+song|skip\s+this\s+song|skip\s+track|skip)$", cmd_lower) or \
           re.search(r"\b(?:play\s+next\s+song|next\s+song|next\s+track|skip\s+this\s+song|skip\s+song)\b", cmd_lower):
            res = music_player.next_track()
            logger.info("Executed intent: Music Next Track")
            msg = "Right away, Boss. Skipped to the next track on Spotify." if "spotify" in cmd_lower else "Right away, Boss. Skipped to the next track."
            return IntentResult(
                is_handled=True,
                domain="music",
                action="next_track",
                response_message=msg,
                details=res
            )

        # 1.5 Volume Controls
        # 1.5.1 Set absolute volume (e.g. "volume 80", "set volume to 50", "volume to 70%")
        m_vol_set = re.search(r"(?:set\s+)?volume\s+(?:to\s+)?(\d{1,3})(?:\s*%)?", cmd_lower)
        if m_vol_set:
            vol_val = int(m_vol_set.group(1))
            res = music_player.set_volume(vol_val)
            logger.info(f"Executed intent: Music Volume Set to {vol_val}")
            return IntentResult(
                is_handled=True,
                domain="music",
                action="volume",
                response_message=res.get("message", f"Right away, Boss. Volume set to {vol_val} percent."),
                details=res
            )

        # 1.5.2 Increase volume
        if re.search(r"^(?:increase\s+volume|volume\s+up|turn\s+up\s+the\s+volume|turn\s+volume\s+up|louder)$", cmd_lower) or \
           re.search(r"\b(?:increase\s+volume|volume\s+up|turn\s+up\s+the\s+volume)\b", cmd_lower):
            res = music_player.change_volume(+15)
            logger.info("Executed intent: Music Volume Up")
            return IntentResult(
                is_handled=True,
                domain="music",
                action="volume",
                response_message=res.get("message", "Right away, Boss. Volume increased."),
                details=res
            )

        # 1.5.3 Decrease volume
        if re.search(r"^(?:decrease\s+volume|volume\s+down|turn\s+down\s+the\s+volume|turn\s+volume\s+down|lower\s+volume|quieter)$", cmd_lower) or \
           re.search(r"\b(?:decrease\s+volume|volume\s+down|turn\s+down\s+the\s+volume|lower\s+volume)\b", cmd_lower):
            res = music_player.change_volume(-15)
            logger.info("Executed intent: Music Volume Down")
            return IntentResult(
                is_handled=True,
                domain="music",
                action="volume",
                response_message=res.get("message", "Right away, Boss. Volume decreased."),
                details=res
            )

        # 1.6 Play Playlist (e.g. "play my Discover Weekly playlist", "play playlist Top Hits")
        m_playlist = re.search(r"play\s+(?:my\s+)?(.+?)\s+playlist(?:\s+on\s+spotify)?$", cmd_lower)
        if not m_playlist:
            m_playlist = re.search(r"play\s+playlist\s+(.+?)(?:\s+on\s+spotify)?$", cmd_lower)
        if m_playlist:
            pl_name = m_playlist.group(1).strip()
            display_pl = pl_name.title()
            res = music_player.play(query=f"{pl_name} playlist")
            logger.info(f"Executed intent: Music Play Playlist '{pl_name}'")
            return IntentResult(
                is_handled=True,
                domain="music",
                action="play_playlist",
                response_message=f"Right away, Boss. Playing your '{display_pl}' playlist.",
                details=res
            )

        # 1.7 Search Music / Search Spotify
        m_music_search = re.search(r"^(?:search\s+for|search|find)\s+(.+?)\s+on\s+(?:spotify|music|youtube)$", cmd_lower)
        if m_music_search:
            s_query = m_music_search.group(1).strip()
            res = music_player.play(query=s_query)
            logger.info(f"Executed intent: Music Search & Play '{s_query}'")
            return IntentResult(
                is_handled=True,
                domain="music",
                action="play",
                response_message=f"Right away, Boss. Located and playing '{s_query}' now.",
                details=res
            )

        # 1.8 Play Track / Artist / Song
        # Matches: "play <query>", "play <track> by <artist>", "play <query> on youtube / on spotify"
        m_play = re.search(r"^play\s+(.+)$", cmd_lower)
        if m_play and not re.search(r"^play\s+(?:the\s+)?next", cmd_lower):
            music_query = m_play.group(1).strip()
            # Clean possible trailing provider names
            music_query = re.sub(r"\s+on\s+(?:youtube|spotify|music)$", "", music_query, flags=re.IGNORECASE).strip()

            # Check if user specified "track by artist"
            m_by = re.search(r"^(.+?)\s+by\s+(.+)$", music_query)
            if m_by:
                track = m_by.group(1).strip()
                artist = m_by.group(2).strip()
                res = music_player.play(query=music_query, track=track, artist=artist)
            else:
                res = music_player.play(query=music_query)

            logger.info(f"Executed intent: Music Play '{music_query}'")
            return IntentResult(
                is_handled=True,
                domain="music",
                action="play",
                response_message=res.get("message", f"Right away, Boss. Playing '{music_query}' now."),
                details=res
            )

        # ----------------------------------------------------------------------
        # DOMAIN 2: BROWSER & GOOGLE SEARCH OPERATIONS
        # ----------------------------------------------------------------------

        # 2.1 Open Google Chrome browser directly
        if re.search(r"^(?:open|launch|start)\s+(?:google\s+chrome|chrome|the\s+browser|browser)$", cmd_lower) or \
           re.search(r"\b(?:open|launch)\s+(?:google\s+chrome|chrome)\b", cmd_lower):
            res = desktop_control.open_chrome()
            logger.info("Executed intent: Open Google Chrome")
            return IntentResult(
                is_handled=True,
                domain="chrome",
                action="open_chrome",
                response_message=res.get("output", "Right away, Boss. Google Chrome has been launched."),
                details=res
            )

        # 2.2 Google Search
        # Matches:
        # - "search for <query> on google"
        # - "search google for <query>"
        # - "search on google for <query>"
        # - "google search for <query>"
        # - "google <query>"
        # - "search for <query>"
        m_search = None
        # Pattern A: "search for X on/in google"
        m_search = re.search(r"^(?:search\s+for|search|find)\s+(.+?)\s+(?:on\s+google|in\s+google|using\s+google|in\s+chrome|on\s+chrome)$", cmd_lower)
        # Pattern B: "search google for X" or "google search for X" or "search on google for X"
        if not m_search:
            m_search = re.search(r"^(?:search\s+google\s+for|search\s+on\s+google\s+for|google\s+search\s+for|google\s+search)\s+(.+)$", cmd_lower)
        # Pattern C: Non-anchored "search for X on google"
        if not m_search:
            m_search = re.search(r"\b(?:search\s+for|search)\s+(.+?)\s+(?:on\s+google|in\s+google|using\s+google)\b", cmd_lower)
        # Pattern D: "google <query>"
        if not m_search:
            m_search = re.search(r"^google\s+(.+)$", cmd_lower)
        # Pattern E: "search for <query>"
        if not m_search:
            m_search = re.search(r"^search\s+for\s+(.+)$", cmd_lower)

        if m_search:
            raw_search_query = m_search.group(1).strip()
            # Clean search query of any trailing google tokens
            clean_search_query = re.sub(r"\s+on\s+google$", "", raw_search_query, flags=re.IGNORECASE).strip()
            clean_search_query = re.sub(r"\s+in\s+google$", "", clean_search_query, flags=re.IGNORECASE).strip()
            res = desktop_control.search_google(clean_search_query)
            logger.info(f"Executed intent: Google Search '{clean_search_query}'")
            return IntentResult(
                is_handled=True,
                domain="chrome",
                action="search_google",
                response_message=res.get("output", f"Right away, Boss. Searching Google for '{clean_search_query}' in Chrome."),
                details=res
            )

        # 2.3 Direct Website Navigation
        # Matches: "open youtube", "open github", "open google", "open google classroom", "go to wikipedia", etc.
        m_open_site = re.search(
            r"^(?:open|launch|go\s+to|navigate\s+to)\s+(youtube|google|google\s+classroom|classroom|aadhaar(?:.*?)|uidai|github|wikipedia|stackoverflow|reddit|linkedin|twitter|x|gmail|netflix|chatgpt|whatsapp(?:.*?)|[a-z0-9\-]+\.(?:com|org|in|net|edu|gov|io|ai)(?:/[^\s]*)?)$",
            cmd_lower
        )
        if not m_open_site:
            # Matches "Open <site> official website" or "Open <site> website"
            m_open_site = re.search(r"^(?:open|launch)\s+(?:the\s+)?(.+?)\s+(?:official\s+)?website$", cmd_lower)

        if not m_open_site:
            # Flexible non-anchored search for core websites if preceded by open/launch/go to
            m_open_site = re.search(
                r"\b(?:open|launch|go\s+to|navigate\s+to)\s+(youtube|google|google\s+classroom|classroom|aadhaar(?:.*?)|uidai|github|wikipedia|stackoverflow|reddit|linkedin|twitter|x|gmail|netflix|chatgpt|whatsapp(?:.*?))\b",
                cmd_lower
            )

        if m_open_site:
            site_target = m_open_site.group(1).strip()
            res = desktop_control.open_website(site_target)
            logger.info(f"Executed intent: Open Website '{site_target}' in Chrome")
            return IntentResult(
                is_handled=True,
                domain="chrome",
                action="open_website",
                response_message=res.get("output", f"Right away, Boss. Opening '{site_target}' in Google Chrome."),
                details=res
            )

        # ----------------------------------------------------------------------
        # DOMAIN 2.5: AI IMAGE & PICTURE GENERATION
        # ----------------------------------------------------------------------
        m_img = re.search(
            r"^(?:generate|create|draw|make|show|render|paint)\s+(?:a\s+|an\s+|me\s+a\s+|me\s+an\s+)?(?:picture|image|photo|artwork|drawing|illustration)\s+(?:of\s+)?(.+)$",
            cmd_lower
        )
        if not m_img:
            m_img = re.search(r"^(?:picture|image|photo)\s+(?:of\s+)?(.+)$", cmd_lower)

        if m_img:
            img_prompt = m_img.group(1).strip()
            img_prompt = re.sub(r"^(?:a\s+|an\s+|the\s+)", "", img_prompt).strip()
            if img_prompt:
                from backend.services.image_service import image_service
                img_res = image_service.generate_image(img_prompt)
                img_url = img_res.get("image_url", "")
                reply_msg = (
                    f"Boss, I have generated a picture of **{img_prompt}**:\n\n"
                    f"![{img_prompt}]({img_url})\n\n"
                    f"[Download Full-Res Picture]({img_url})"
                )
                logger.info(f"Executed intent: Generate Image '{img_prompt}'")
                return IntentResult(
                    is_handled=True,
                    domain="image",
                    action="generate_image",
                    response_message=reply_msg,
                    details=img_res
                )

        # ----------------------------------------------------------------------
        # DOMAIN 3: DESKTOP & OPERATING SYSTEM AUTOMATION
        # ----------------------------------------------------------------------
        m_app = re.search(r"^(?:open|launch|start)\s+(notepad|calculator|calc|paint|mspaint|explorer|file\s+explorer|powershell|cmd|terminal|code|vs\s*code)$", cmd_lower)
        if m_app:
            app_target = m_app.group(1).strip()
            if app_target == "file explorer":
                app_target = "explorer"
            elif app_target in ["vs code", "vscode"]:
                app_target = "code"
            elif app_target == "terminal":
                app_target = "powershell"
            res = desktop_control.execute_action("open_app", app_target)
            logger.info(f"Executed intent: Open Desktop App '{app_target}'")
            return IntentResult(
                is_handled=True,
                domain="desktop",
                action="open_app",
                response_message=res.get("output", f"Right away, Boss. Launched '{app_target}'."),
                details=res
            )

        # System diagnostics
        if re.search(r"^(?:system\s+diagnostics|system\s+info|hardware\s+status|hardware\s+diagnostics)$", cmd_lower):
            res = desktop_control.execute_action("system_info", "system")
            return IntentResult(
                is_handled=True,
                domain="desktop",
                action="system_info",
                response_message=res.get("output", "Right away, Boss. Systems nominal."),
                details=res
            )

        # ----------------------------------------------------------------------
        # DOMAIN 4: PASS THROUGH TO CONVERSATIONAL AI & RAG
        # ----------------------------------------------------------------------
        return IntentResult(
            is_handled=False,
            domain="none",
            action="none",
            response_message="",
            details={}
        )

intent_service = IntentService()

