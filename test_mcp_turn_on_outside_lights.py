import requests

url = "http://localhost:8081/mcp"
payload = {
    "jsonrpc": "2.0",
    "method": "call_service",
    "params": {
        "domain": "light",
        "service": "turn_on",
        "service_data": {"entity_id": "light.outside_lights"}
    },
    "id": 4
}
response = requests.post(url, json=payload)
print("Status code:", response.status_code)
print("Response:", response.json())
