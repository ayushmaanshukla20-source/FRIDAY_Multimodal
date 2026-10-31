import unittest
from fastapi.testclient import TestClient
from backend.main import app
from backend.integrations.desktop_control import desktop_control
from backend.integrations.spotify import spotify_integration
from backend.services.intent_service import intent_service

class TestChromeAndSpotifyIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    # --------------------------------------------------------------------------
    # 1. Chrome Unit & Endpoint Tests
    # --------------------------------------------------------------------------
    def test_chrome_executable_found(self):
        """Validates that Chrome executable path is discovered on Windows."""
        path = desktop_control.chrome_path
        self.assertIsNotNone(path)
        self.assertTrue(path.lower().endswith("chrome.exe"))

    def test_chrome_search_google_query_building(self):
        """Validates Google search URL generation and command response."""
        res = desktop_control.search_google("machine learning tutorials")
        self.assertTrue(res["success"])
        self.assertEqual(res["action"], "search_google")
        self.assertIn("machine learning tutorials", res["output"])

    def test_chrome_open_website_shortcuts(self):
        """Validates direct shortcuts for YouTube, Google Classroom, and UIDAI."""
        yt = desktop_control.open_website("YouTube")
        self.assertTrue(yt["success"])
        self.assertIn("https://www.youtube.com", yt["target"])

        classroom = desktop_control.open_website("Google Classroom")
        self.assertTrue(classroom["success"])
        self.assertIn("https://classroom.google.com", classroom["target"])

        aadhaar = desktop_control.open_website("Aadhaar card official website")
        self.assertTrue(aadhaar["success"])
        self.assertIn("https://uidai.gov.in", aadhaar["target"])

    def test_desktop_execute_api_chrome(self):
        """Tests /api/desktop/execute with open_chrome action."""
        resp = self.client.post("/api/desktop/execute", json={"action": "open_chrome", "target": "chrome"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])

    # --------------------------------------------------------------------------
    # 2. Spotify Unit & Endpoint Tests
    # --------------------------------------------------------------------------
    def test_spotify_search_track_and_artist(self):
        """Validates Spotify search catalog response structure."""
        resp = self.client.post("/api/spotify/search", json={"query": "Arijit Singh", "search_type": "artist"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("items", data)
        self.assertTrue(len(data["items"]) > 0)
        self.assertIn("Arijit Singh", data["items"][0]["name"])

    def test_spotify_playback_endpoints(self):
        """Tests /api/spotify play, pause, resume, next, and playlist endpoints."""
        # Play track
        p_resp = self.client.post("/api/spotify/play", json={"track": "Believer", "artist": "Imagine Dragons"})
        self.assertEqual(p_resp.status_code, 200)
        p_data = p_resp.json()
        self.assertTrue(p_data["success"])
        self.assertIn("Believer", p_data["message"])

        # Pause
        pause_resp = self.client.post("/api/spotify/pause")
        self.assertEqual(pause_resp.status_code, 200)
        self.assertTrue(pause_resp.json()["success"])

        # Resume
        resume_resp = self.client.post("/api/spotify/resume")
        self.assertEqual(resume_resp.status_code, 200)
        self.assertTrue(resume_resp.json()["success"])

        # Next
        next_resp = self.client.post("/api/spotify/next")
        self.assertEqual(next_resp.status_code, 200)
        self.assertTrue(next_resp.json()["success"])

        # Playlist
        pl_resp = self.client.post("/api/spotify/playlist", json={"playlist_name": "Discover Weekly"})
        self.assertEqual(pl_resp.status_code, 200)
        self.assertTrue(pl_resp.json()["success"])

    def test_spotify_status_endpoint(self):
        """Validates /api/spotify/status returns structured telemetry."""
        resp = self.client.get("/api/spotify/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("is_configured", data)
        self.assertIn("is_playing", data)

    # --------------------------------------------------------------------------
    # 3. End-to-End Chat Voice Directive Tests for All 12 Requirements
    # --------------------------------------------------------------------------
    def test_chat_voice_directive_open_youtube(self):
        resp = self.client.post("/api/chat", json={"prompt": "Open YouTube."})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Opening YouTube in Google Chrome", resp.json()["response"])

    def test_chat_voice_directive_open_chrome(self):
        resp = self.client.post("/api/chat", json={"prompt": "Open Google Chrome."})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Google Chrome has been launched", resp.json()["response"])

    def test_chat_voice_directive_search_aadhaar(self):
        resp = self.client.post("/api/chat", json={"prompt": "Search for the Aadhaar card official website on Google."})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Searching Google for 'the aadhaar card official website' in Chrome", resp.json()["response"])

    def test_chat_voice_directive_search_ml_tutorials(self):
        resp = self.client.post("/api/chat", json={"prompt": "Search for machine learning tutorials."})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Searching Google for 'machine learning tutorials' in Chrome", resp.json()["response"])

    def test_chat_voice_directive_open_classroom(self):
        resp = self.client.post("/api/chat", json={"prompt": "Open Google Classroom."})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Opening Google Classroom in Google Chrome", resp.json()["response"])

    def test_chat_voice_directive_play_believer(self):
        resp = self.client.post("/api/chat", json={"prompt": "Play Believer by Imagine Dragons on Spotify."})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("believer", resp.json()["response"].lower())

    def test_chat_voice_directive_play_perfect(self):
        resp = self.client.post("/api/chat", json={"prompt": "Play Perfect by Ed Sheeran."})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("perfect", resp.json()["response"].lower())

    def test_chat_voice_directive_search_arijit(self):
        resp = self.client.post("/api/chat", json={"prompt": "Search for Arijit Singh on Spotify."})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("arijit singh", resp.json()["response"].lower())

    def test_chat_voice_directive_pause_spotify(self):
        resp = self.client.post("/api/chat", json={"prompt": "Pause Spotify."})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Paused Spotify playback", resp.json()["response"])

    def test_chat_voice_directive_resume_spotify(self):
        resp = self.client.post("/api/chat", json={"prompt": "Resume Spotify."})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Resumed Spotify playback", resp.json()["response"])

    def test_chat_voice_directive_next_song(self):
        resp = self.client.post("/api/chat", json={"prompt": "Play the next song."})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Skipped to the next track", resp.json()["response"])

    def test_chat_voice_directive_play_discover_weekly(self):
        resp = self.client.post("/api/chat", json={"prompt": "Play my Discover Weekly playlist."})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Discover Weekly", resp.json()["response"])

if __name__ == "__main__":
    unittest.main()
