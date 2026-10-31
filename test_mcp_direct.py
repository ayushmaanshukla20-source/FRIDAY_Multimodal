import time
from backend.integrations.chrome_mcp import chrome_mcp_client

print("--- Testing Chrome DevTools MCP Direct Connection ---")
print(f"NPX available: {chrome_mcp_client.is_npx_available()}")

# Connect with timeout
start = time.time()
connected = chrome_mcp_client.connect(timeout_sec=20)
elapsed = time.time() - start
print(f"Connected: {connected} in {elapsed:.2f}s")

status = chrome_mcp_client.get_status()
print(f"Status: {status.get('connected')}")
print(f"Server Info: {status.get('server_info')}")
print(f"Tools Count: {status.get('tools_count')}")
print(f"Available Tools (first 5): {status.get('tool_names', [])[:5]}")

chrome_mcp_client.disconnect()
print("Disconnected cleanly.")
