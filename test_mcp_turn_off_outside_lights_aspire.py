import requests

# Aspire MCP server config from mcp_config.json and .env
url = "http://192.168.100.101:8123/mcp_server/mcp"  # This is the SSE/MCP endpoint for Aspire MCP
headers = {
    "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjZjkzODQxNjBhN2Y0NjM2YjgzYTNkYTYyYjNlMWY1MiIsImlhdCI6MTc0NTI2MzI1MywiZXhwIjoyMDYwNjIzMjUzfQ.qNueMkpSlP7S0Os18u3yHWKR4rY2a2GkbEqmgpglWGY",
    "Content-Type": "application/json"
}
payload = {
    "jsonrpc": "2.0",
    "method": "call_service",
    "params": {
        "domain": "light",
        "service": "turn_off",
        "service_data": {"entity_id": "light.outside_lights"}
    },
    "id": 9
}
response = requests.post(url, json=payload, headers=headers)
print("Status code:", response.status_code)
print("Response:", response.json())
