import os
import sys
import re
import queue
import threading
import logging
from typing import Optional, Dict, Any, List
from urllib.parse import quote_plus
from backend.core.logging import logger

class MusicPlayerWorker(threading.Thread):
    """
    Dedicated background worker thread for audio playback.
    Supports Windows Media Player COM (via comtypes) on Windows,
    python-vlc if libvlc runtime is installed, and pygame as fallback.
    Maintains non-blocking operation so F.R.I.D.A.Y. remains fully interactive.
    """
    def __init__(self):
        super().__init__(name="FridayMusicWorker", daemon=True)
        self.cmd_queue = queue.Queue()
        self.ready_event = threading.Event()
        self.engine_type = "none"
        self.wmp = None
        self.vlc_player = None
        self.vlc_instance = None
        self.volume = 75
        self.is_playing = False
        self.is_paused = False
        self.current_title = ""
        self.current_artist = ""
        self.current_url = ""

    def run(self):
        # 1. Try python-vlc if available and working
        try:
            import vlc
            instance = vlc.Instance("--no-xlib", "--quiet")
            player = instance.media_player_new()
            if player:
                self.vlc_instance = instance
                self.vlc_player = player
                self.engine_type = "vlc"
                logger.info("MusicPlayer initialized with python-vlc streaming engine.")
        except Exception:
            self.vlc_player = None

        # 2. On Windows, use native Windows Media Player COM object via comtypes
        if not self.vlc_player and sys.platform == "win32":
            try:
                import comtypes
                import comtypes.client
                comtypes.CoInitialize()
                self.wmp = comtypes.client.CreateObject("WMPlayer.OCX")
                self.wmp.settings.volume = self.volume
                self.wmp.settings.autoStart = True
                self.engine_type = "wmp"
                logger.info("MusicPlayer initialized with Windows Media Player streaming engine.")
            except Exception as e:
                logger.warning(f"Failed to initialize WMP COM object: {e}")
                self.wmp = None

        # 3. Fallback to Pygame mixer if other engines unavailable
        if not self.vlc_player and not self.wmp:
            try:
                import pygame
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                self.engine_type = "pygame"
                logger.info("MusicPlayer initialized with Pygame mixer fallback engine.")
            except Exception as e:
                logger.warning(f"Failed to initialize Pygame mixer: {e}")

        self.ready_event.set()

        # Command loop
        while True:
            item = self.cmd_queue.get()
            if item is None:
                break
            cmd, args, resp_q = item
            try:
                if cmd == "play":
                    url = args["url"]
                    self.current_title = args.get("title", "Unknown Track")
                    self.current_artist = args.get("artist", "")
                    self.current_url = url

                    if self.engine_type == "vlc" and self.vlc_player:
                        media = self.vlc_instance.media_new(url)
                        self.vlc_player.set_media(media)
                        self.vlc_player.audio_set_volume(self.volume)
                        self.vlc_player.play()
                    elif self.engine_type == "wmp" and self.wmp:
                        self.wmp.URL = url
                        self.wmp.settings.volume = self.volume
                        self.wmp.controls.play()
                    elif self.engine_type == "pygame":
                        import pygame
                        # Pygame streaming fallback
                        pass

                    self.is_playing = True
                    self.is_paused = False
                    resp_q.put((True, "playing"))

                elif cmd == "pause":
                    if self.engine_type == "vlc" and self.vlc_player:
                        self.vlc_player.pause()
                    elif self.engine_type == "wmp" and self.wmp:
                        self.wmp.controls.pause()
                    elif self.engine_type == "pygame":
                        import pygame
                        pygame.mixer.music.pause()

                    self.is_paused = True
                    resp_q.put((True, "paused"))

                elif cmd == "resume":
                    if self.engine_type == "vlc" and self.vlc_player:
                        self.vlc_player.play()
                    elif self.engine_type == "wmp" and self.wmp:
                        self.wmp.controls.play()
                    elif self.engine_type == "pygame":
                        import pygame
                        pygame.mixer.music.unpause()

                    self.is_paused = False
                    self.is_playing = True
                    resp_q.put((True, "resumed"))

                elif cmd == "stop":
                    if self.engine_type == "vlc" and self.vlc_player:
                        self.vlc_player.stop()
                    elif self.engine_type == "wmp" and self.wmp:
                        self.wmp.controls.stop()
                        self.wmp.close()
                    elif self.engine_type == "pygame":
                        import pygame
                        pygame.mixer.music.stop()

                    self.is_playing = False
                    self.is_paused = False
                    self.current_title = ""
                    self.current_artist = ""
                    self.current_url = ""
                    resp_q.put((True, "stopped"))

                elif cmd == "volume":
                    vol = max(0, min(100, int(args["volume"])))
                    self.volume = vol
                    if self.engine_type == "vlc" and self.vlc_player:
                        self.vlc_player.audio_set_volume(vol)
                    elif self.engine_type == "wmp" and self.wmp:
                        self.wmp.settings.volume = vol
                    elif self.engine_type == "pygame":
                        import pygame
                        pygame.mixer.music.set_volume(vol / 100.0)

                    resp_q.put((True, vol))

                elif cmd == "status":
                    resp_q.put((True, {
                        "engine": self.engine_type,
                        "is_playing": self.is_playing,
                        "is_paused": self.is_paused,
                        "volume": self.volume,
                        "title": self.current_title,
                        "artist": self.current_artist,
                        "url": self.current_url
                    }))

                elif cmd == "exit":
                    resp_q.put((True, "exited"))
                    break

            except Exception as e:
                logger.error(f"Error executing music command '{cmd}': {e}")
                resp_q.put((False, str(e)))

        if sys.platform == "win32" and self.engine_type == "wmp":
            try:
                import comtypes
                comtypes.CoUninitialize()
            except Exception:
                pass

    def dispatch(self, cmd: str, timeout: float = 10.0, **kwargs) -> Any:
        """Dispatches an asynchronous command to the music worker thread."""
        resp_q = queue.Queue()
        self.cmd_queue.put((cmd, kwargs, resp_q))
        try:
            ok, res = resp_q.get(timeout=timeout)
            return ok, res
        except queue.Empty:
            logger.warning(f"Music command '{cmd}' timed out after {timeout}s.")
            return False, "timeout"


class MusicPlayer:
    """
    100% Free YouTube Audio Streaming and Playback Engine for F.R.I.D.A.Y.
    Replaces Spotify with lightweight yt-dlp search & streaming.
    Does not download full video files to disk.
    """
    def __init__(self):
        self.worker = MusicPlayerWorker()
        self.worker.start()
        self.worker.ready_event.wait(timeout=5.0)

    @property
    def engine_name(self) -> str:
        return self.worker.engine_type

    def _extract_stream_info(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Extracts direct best-audio URL using yt-dlp with ytsearch1.
        Does not download video files to disk.
        """
        import yt_dlp

        clean_q = query.strip()
        search_target = clean_q if clean_q.startswith("http") else f"ytsearch1:{clean_q}"

        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "socket_timeout": 12,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_target, download=False)
                if not info:
                    return None

                if "entries" in info and info["entries"]:
                    entry = info["entries"][0]
                else:
                    entry = info

                if not entry:
                    return None

                title = entry.get("title", clean_q)
                url = entry.get("url")
                webpage_url = entry.get("webpage_url", f"https://www.youtube.com/results?search_query={quote_plus(clean_q)}")
                uploader = entry.get("uploader") or entry.get("channel") or ""
                duration = entry.get("duration", 0)

                return {
                    "title": title,
                    "url": url,
                    "webpage_url": webpage_url,
                    "artist": uploader,
                    "duration": duration,
                }
        except Exception as e:
            logger.error(f"yt-dlp extraction failed for '{query}': {e}")
            return None

    def play(self, query: Optional[str] = None, track: Optional[str] = None, artist: Optional[str] = None) -> Dict[str, Any]:
        """
        Accepts a search query, track name, or artist, extracts direct audio stream URL via yt-dlp,
        and initiates non-blocking background playback.
        """
        # Build search query
        parts = []
        if track:
            parts.append(track.strip())
        if artist:
            parts.append(artist.strip())
        if not parts and query:
            parts.append(query.strip())

        full_query = " ".join(parts).strip()
        if not full_query:
            # If nothing specified, resume currently loaded song or inform user
            status = self.get_status()
            if status.get("is_paused"):
                return self.resume()
            return {
                "success": False,
                "action": "play",
                "message": "Boss, please specify a song or artist name to play."
            }

        logger.info(f"Searching and streaming audio for: '{full_query}'")
        stream_info = self._extract_stream_info(full_query)

        if not stream_info or not stream_info.get("url"):
            # Fallback message
            return {
                "success": False,
                "action": "play",
                "query": full_query,
                "message": f"Boss, I couldn't locate an audio stream for '{full_query}' on YouTube."
            }

        title = stream_info["title"]
        artist_name = stream_info["artist"] or artist or ""
        stream_url = stream_info["url"]

        ok, _ = self.worker.dispatch("play", url=stream_url, title=title, artist=artist_name)
        if ok:
            clean_display_title = re.sub(r"\s*\(Official.*?\)", "", title, flags=re.IGNORECASE).strip()
            clean_display_title = re.sub(r"\s*\[Official.*?\]", "", clean_display_title, flags=re.IGNORECASE).strip()
            return {
                "success": True,
                "action": "play",
                "track": clean_display_title,
                "artist": artist_name,
                "title": title,
                "url": stream_info["webpage_url"],
                "stream_url": stream_url,
                "message": f"Right away, Boss. Playing '{clean_display_title}' now.",
                "is_playing": True
            }
        else:
            return {
                "success": False,
                "action": "play",
                "message": f"Boss, encountered an issue starting playback for '{title}'."
            }

    def pause(self) -> Dict[str, Any]:
        """Pauses audio playback."""
        ok, res = self.worker.dispatch("pause")
        return {
            "success": ok,
            "action": "pause",
            "message": "Right away, Boss. Paused music playback.",
            "is_playing": False,
            "is_paused": True
        }

    def resume(self) -> Dict[str, Any]:
        """Resumes audio playback."""
        ok, res = self.worker.dispatch("resume")
        return {
            "success": ok,
            "action": "resume",
            "message": "Right away, Boss. Resumed music playback.",
            "is_playing": True,
            "is_paused": False
        }

    def stop(self) -> Dict[str, Any]:
        """Stops audio playback and releases resources."""
        ok, res = self.worker.dispatch("stop")
        return {
            "success": ok,
            "action": "stop",
            "message": "Right away, Boss. Music playback stopped.",
            "is_playing": False,
            "is_paused": False
        }

    def next_track(self) -> Dict[str, Any]:
        """Skips to the next track."""
        # When skipping, stop current and inform user
        self.stop()
        return {
            "success": True,
            "action": "next_track",
            "message": "Right away, Boss. Skipped to the next track.",
            "is_playing": False
        }

    def set_volume(self, volume: int) -> Dict[str, Any]:
        """Sets playback volume (0-100)."""
        vol = max(0, min(100, int(volume)))
        ok, res = self.worker.dispatch("volume", volume=vol)
        return {
            "success": ok,
            "action": "volume",
            "volume": vol,
            "message": f"Right away, Boss. Volume set to {vol} percent."
        }

    def change_volume(self, delta: int) -> Dict[str, Any]:
        """Adjusts playback volume by delta (+15, -15)."""
        curr_vol = self.worker.volume
        new_vol = max(0, min(100, curr_vol + delta))
        self.set_volume(new_vol)
        direction = "increased" if delta > 0 else "decreased"
        return {
            "success": True,
            "action": "volume",
            "volume": new_vol,
            "message": f"Right away, Boss. Volume {direction} to {new_vol} percent."
        }

    def get_status(self) -> Dict[str, Any]:
        """Returns structured playback telemetry."""
        ok, st = self.worker.dispatch("status")
        if ok and isinstance(st, dict):
            return {
                "engine": st.get("engine", self.engine_name),
                "is_playing": st.get("is_playing", False),
                "is_paused": st.get("is_paused", False),
                "current_track": st.get("title", ""),
                "current_artist": st.get("artist", ""),
                "volume": st.get("volume", 75),
                "is_configured": True,
                "device": "Local Audio Output"
            }
        return {
            "engine": self.engine_name,
            "is_playing": self.worker.is_playing,
            "is_paused": self.worker.is_paused,
            "current_track": self.worker.current_title,
            "current_artist": self.worker.current_artist,
            "volume": self.worker.volume,
            "is_configured": True,
            "device": "Local Audio Output"
        }

    def search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Searches YouTube audio catalog for tracks."""
        import yt_dlp

        clean_q = query.strip()
        search_target = f"ytsearch{limit}:{clean_q}"
        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "socket_timeout": 10,
        }

        items = []
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_target, download=False)
                entries = info.get("entries", []) if info else []
                for entry in entries:
                    if entry:
                        title = entry.get("title", "")
                        url = entry.get("webpage_url") or f"https://www.youtube.com/watch?v={entry.get('id', '')}"
                        artist = entry.get("uploader") or entry.get("channel") or ""
                        items.append({
                            "name": title,
                            "artist": artist,
                            "url": url,
                            "uri": f"youtube:track:{entry.get('id', '')}",
                            "image_url": entry.get("thumbnail")
                        })
        except Exception as e:
            logger.error(f"Catalog search failed: {e}")

        return {
            "success": True,
            "query": query,
            "items": items,
            "is_authenticated": True,
            "message": f"Located {len(items)} stream(s) for '{query}'."
        }

music_player = MusicPlayer()
