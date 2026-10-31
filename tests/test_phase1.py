import unittest
from fastapi.testclient import TestClient
from backend.main import app

class TestPhase1(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_chat_endpoint(self):
        response = self.client.post("/chat", json={"prompt": "Test hello"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        self.assertTrue(len(data["response"]) > 0)

if __name__ == "__main__":
    unittest.main()
