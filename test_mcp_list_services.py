import requests

url = "http://localhost:8081/mcp"
payload = {
    "jsonrpc": "2.0",
    "method": "call_service",
    "params": {
        "domain": "homeassistant",
        "service": "services",
        "service_data": {}
    },
    "id": 6
}
response = requests.post(url, json=payload)
print("Status code:", response.status_code)
print("Response:", response.json())
