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
from typing import Dict, Any, List, Optional
from backend.core.logging import logger
from backend.integrations.music_player import music_player, MusicPlayer

class SpotifyIntegration:
    """
    100% Free Audio Streaming Adapter replacing Spotify with yt-dlp & native playback.
    Maintains full backward compatibility with existing F.R.I.D.A.Y. API contracts
    without requiring Spotify Premium, Spotify developer credentials, or spotipy tokens.
    """
    def __init__(self):
        self.player: MusicPlayer = music_player

    def is_configured(self) -> bool:
        """Returns True since free streaming requires zero API credentials."""
        return True

    def get_auth_url(self) -> Optional[str]:
        return None

    def save_auth_code(self, code: str) -> bool:
        return True

    def launch_spotify_target(self, uri: str, web_url: str):
        pass

    def search(self, query: str, search_type: str = "track") -> Dict[str, Any]:
        """Searches audio catalog using free YouTube stream discovery."""
        res = self.player.search(query=query, limit=5)
        # Ensure items have expected Spotify-like shape
        formatted_items = []
        for it in res.get("items", []):
            formatted_items.append({
                "name": it.get("name"),
                "artist": it.get("artist"),
                "url": it.get("url"),
                "uri": it.get("uri"),
                "image_url": it.get("image_url")
            })

        return {
            "query": query,
            "items": formatted_items,
            "is_authenticated": True,
            "message": f"Right away, Boss. Located audio streams for '{query}'."
        }

    def play(self, query: Optional[str] = None, track: Optional[str] = None, artist: Optional[str] = None) -> Dict[str, Any]:
        """Streams track directly via free audio player."""
        res = self.player.play(query=query, track=track, artist=artist)
        return {
            "success": res.get("success", True),
            "action": "play",
            "message": res.get("message", f"Right away, Boss. Playing '{track or query}' now."),
            "track": res.get("track"),
            "artist": res.get("artist"),
            "url": res.get("url"),
            "target": res.get("track")
        }

    def pause(self) -> Dict[str, Any]:
        """Pauses audio playback."""
        res = self.player.pause()
        return {
            "success": res.get("success", True),
            "action": "pause",
            "message": "Right away, Boss. Paused playback.",
            "is_playing": False
        }

    def resume(self) -> Dict[str, Any]:
        """Resumes audio playback."""
        res = self.player.resume()
        return {
            "success": res.get("success", True),
            "action": "resume",
            "message": "Right away, Boss. Resumed playback.",
            "is_playing": True
        }

    def next_track(self) -> Dict[str, Any]:
        """Skips to the next track."""
        res = self.player.next_track()
        return {
            "success": res.get("success", True),
            "action": "next_track",
            "message": "Right away, Boss. Skipped to the next track.",
            "is_playing": False
        }

    def play_playlist(self, playlist_name: str) -> Dict[str, Any]:
        """Streams songs from playlist query."""
        res = self.player.play(query=f"{playlist_name} playlist")
        return {
            "success": res.get("success", True),
            "action": "play_playlist",
            "message": f"Right away, Boss. Playing '{playlist_name}' playlist now.",
            "target": playlist_name,
            "url": res.get("url")
        }

    def get_playback_status(self) -> Dict[str, Any]:
        """Reports current playback and device status."""
        st = self.player.get_status()
        current_track = None
        if st.get("current_track"):
            current_track = {
                "name": st.get("current_track"),
                "artist": st.get("current_artist", ""),
                "album": "Free Streaming"
            }
        return {
            "is_configured": True,
            "has_user_auth": True,
            "is_playing": st.get("is_playing", False),
            "device": f"Local Audio Engine ({st.get('engine', 'wmp')})",
            "current_track": current_track
        }

spotify_integration = SpotifyIntegration()

