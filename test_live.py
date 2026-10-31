"""
FRIDAY Multimodal Voice Assistant
Author: Ayushmaan Shukla
Roll / Enrollment No.: 202510101240164
Department: Computer Science & Engineering (AI & ML)
Institution: Shri Ramswaroop Memorial University
Notice: This project is strictly for academic evaluation. 
        Unauthorized reproduction or submission is a violation of academic integrity.
"""
import requests
import json

base = "http://127.0.0.1:8000"

print("--- Testing Live MCP Status Endpoint ---")
r = requests.get(f"{base}/api/desktop/mcp/status")
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2))

print("\n--- Testing Browser Voice Commands via Live API ---")
cmds = [
    "Open YouTube",
    "Search for the Aadhaar official website on Google",
    "Open Google Classroom"
]

for cmd in cmds:
    resp = requests.post(f"{base}/api/chat", json={"prompt": cmd})
    print(f"Command: '{cmd}'")
    print(f"HTTP Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Friday Response: {data.get('response')}")
        print(f"Direct Speech: {data.get('direct_speech')}")
        print(f"Context: {data.get('context')}")
    else:
        print(f"Error: {resp.text}")
    print("-" * 50)

