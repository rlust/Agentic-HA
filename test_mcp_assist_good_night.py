import requests

url = "http://localhost:8081/mcp"
payload = {
    "jsonrpc": "2.0",
    "method": "call_service",
    "params": {
        "domain": "assist_pipeline",
        "service": "assist",
        "service_data": {"input": "Good Night"}
    },
    "id": 5
}
response = requests.post(url, json=payload)
print("Status code:", response.status_code)
print("Response:", response.json())
