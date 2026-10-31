import unittest
from fastapi.testclient import TestClient
from backend.main import app
from backend.integrations.desktop_control import desktop_control
from backend.integrations.music_player import music_player
from backend.services.intent_service import intent_service

class TestBrowserAndMusicFeatures(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    # --------------------------------------------------------------------------
    # 1. Browser & Search Tests
    # --------------------------------------------------------------------------
    def test_browser_direct_sites_routing(self):
        """Validates that direct sites are detected by intent router."""
        # YouTube
        res_yt = intent_service.detect_and_execute("open YouTube")
        self.assertTrue(res_yt.is_handled)
        self.assertEqual(res_yt.domain, "chrome")
        self.assertEqual(res_yt.action, "open_website")
        self.assertIn("YouTube", res_yt.response_message)

        # GitHub
        res_gh = intent_service.detect_and_execute("open GitHub")
        self.assertTrue(res_gh.is_handled)
        self.assertEqual(res_gh.domain, "chrome")
        self.assertEqual(res_gh.action, "open_website")
        self.assertIn("GitHub", res_gh.response_message)

        # Chrome
        res_chrome = intent_service.detect_and_execute("open Chrome")
        self.assertTrue(res_chrome.is_handled)
        self.assertEqual(res_chrome.domain, "chrome")
        self.assertEqual(res_chrome.action, "open_chrome")
        self.assertIn("Google Chrome", res_chrome.response_message)

        # Google
        res_google = intent_service.detect_and_execute("open Google")
        self.assertTrue(res_google.is_handled)
        self.assertEqual(res_google.domain, "chrome")
        self.assertEqual(res_google.action, "open_website")
        self.assertIn("Google", res_google.response_message)

    def test_google_search_query_extraction(self):
        """Validates that Google search queries are cleaned and routed without conversational fluff."""
        # Pattern: search for X on Google
        res1 = intent_service.detect_and_execute("search for python tutorials on Google")
        self.assertTrue(res1.is_handled)
        self.assertEqual(res1.action, "search_google")
        self.assertEqual(res1.details.get("target"), "python tutorials")

        # Pattern: search Google for X
        res2 = intent_service.detect_and_execute("search Google for latest space news")
        self.assertTrue(res2.is_handled)
        self.assertEqual(res2.action, "search_google")
        self.assertEqual(res2.details.get("target"), "latest space news")

        # Pattern: search for X
        res3 = intent_service.detect_and_execute("search for machine learning architecture")
        self.assertTrue(res3.is_handled)
        self.assertEqual(res3.action, "search_google")
        self.assertEqual(res3.details.get("target"), "machine learning architecture")

    # --------------------------------------------------------------------------
    # 2. Music Streaming & Control Tests
    # --------------------------------------------------------------------------
    def test_music_controls_routing(self):
        """Validates play, pause, resume, stop, and volume controls."""
        # Pause
        p_res = intent_service.detect_and_execute("pause the music")
        self.assertTrue(p_res.is_handled)
        self.assertEqual(p_res.domain, "music")
        self.assertEqual(p_res.action, "pause")
        self.assertIn("Paused", p_res.response_message)

        # Resume
        r_res = intent_service.detect_and_execute("continue playing")
        self.assertTrue(r_res.is_handled)
        self.assertEqual(r_res.domain, "music")
        self.assertEqual(r_res.action, "resume")
        self.assertIn("Resumed", r_res.response_message)

        # Stop
        s_res = intent_service.detect_and_execute("stop music")
        self.assertTrue(s_res.is_handled)
        self.assertEqual(s_res.domain, "music")
        self.assertEqual(s_res.action, "stop")
        self.assertIn("stopped", s_res.response_message)

        # Volume Set
        v_res = intent_service.detect_and_execute("set volume to 85")
        self.assertTrue(v_res.is_handled)
        self.assertEqual(v_res.domain, "music")
        self.assertEqual(v_res.action, "volume")
        self.assertIn("85 percent", v_res.response_message)

        # Volume Up
        v_up = intent_service.detect_and_execute("increase volume")
        self.assertTrue(v_up.is_handled)
        self.assertEqual(v_up.domain, "music")
        self.assertIn("increased", v_up.response_message)

        # Volume Down
        v_down = intent_service.detect_and_execute("decrease volume")
        self.assertTrue(v_down.is_handled)
        self.assertEqual(v_down.domain, "music")
        self.assertIn("decreased", v_down.response_message)

    def test_music_api_endpoints(self):
        """Validates new /api/music/* endpoints."""
        # Pause endpoint
        r_pause = self.client.post("/api/music/pause")
        self.assertEqual(r_pause.status_code, 200)
        self.assertTrue(r_pause.json()["success"])

        # Resume endpoint
        r_resume = self.client.post("/api/music/resume")
        self.assertEqual(r_resume.status_code, 200)
        self.assertTrue(r_resume.json()["success"])

        # Stop endpoint
        r_stop = self.client.post("/api/music/stop")
        self.assertEqual(r_stop.status_code, 200)
        self.assertTrue(r_stop.json()["success"])

        # Volume endpoint
        r_vol = self.client.post("/api/music/volume?volume=60")
        self.assertEqual(r_vol.status_code, 200)
        self.assertEqual(r_vol.json()["volume"], 60)

        # Status endpoint
        r_st = self.client.get("/api/music/status")
        self.assertEqual(r_st.status_code, 200)
        self.assertIn("engine", r_st.json())

    # --------------------------------------------------------------------------
    # 3. Intent Separation & Conversation Pass-through Tests
    # --------------------------------------------------------------------------
    def test_conversational_pass_through(self):
        """Validates that general queries do not trigger intent routing."""
        queries = [
            "Who was Alan Turing?",
            "Can you write a poem about artificial intelligence?",
            "What is the airspeed velocity of an unladen swallow?",
            "Explain quantum computing in simple terms."
        ]
        for q in queries:
            res = intent_service.detect_and_execute(q)
            self.assertFalse(res.is_handled, f"Query '{q}' should pass through to LLM.")
            self.assertEqual(res.domain, "none")

if __name__ == "__main__":
    unittest.main()

