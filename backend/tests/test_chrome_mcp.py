import unittest
from fastapi.testclient import TestClient
from backend.main import app
from backend.integrations.chrome_mcp import chrome_mcp_client
from backend.integrations.desktop_control import desktop_control

class TestChromeMCPIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_npx_binary_availability(self):
        """Verifies that npx is detectable for launching the Chrome DevTools MCP server."""
        available = chrome_mcp_client.is_npx_available()
        self.assertTrue(available, "npx.cmd / npx should be available in system PATH")

    def test_chrome_mcp_status_structure(self):
        """Tests that get_status returns properly structured configuration dictionary."""
        status = chrome_mcp_client.get_status()
        self.assertIsInstance(status, dict)
        self.assertTrue(status.get("configured"))
        self.assertIn("connected", status)
        self.assertIn("npx_available", status)
        self.assertIn("tools_count", status)

    def test_mcp_status_api_endpoint(self):
        """Tests FastAPI /api/desktop/mcp/status endpoint returns valid telemetry."""
        resp = self.client.get("/api/desktop/mcp/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("configured"))
        self.assertTrue(data.get("npx_available"))

    def test_desktop_execute_mcp_action(self):
        """Tests desktop_control.execute_action with mcp_status action."""
        res = desktop_control.execute_action(action="mcp_status", target="")
        self.assertTrue(res.get("success"))
        self.assertIn("Chrome DevTools MCP", res.get("output"))

    def test_website_shortcuts_coverage(self):
        """Verifies required voice commands map to valid targets."""
        for site, expected_url in [
            ("youtube", "https://www.youtube.com"),
            ("google classroom", "https://classroom.google.com"),
            ("aadhaar card official website", "https://uidai.gov.in")
        ]:
            res = desktop_control.open_website(site)
            self.assertTrue(res.get("success"))
            self.assertIn(expected_url, res.get("target"))

if __name__ == "__main__":
    unittest.main()
