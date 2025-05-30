import requests

url = "http://localhost:8081/mcp"
payload = {
    "jsonrpc": "2.0",
    "method": "call_service",
    "params": {
        "domain": "persistent_notification",
        "service": "create",
        "service_data": {
            "message": "Good Night",
            "title": "Agentic HA"
        }
    },
    "id": 8
}
response = requests.post(url, json=payload)
print("Status code:", response.status_code)
print("Response:", response.json())
