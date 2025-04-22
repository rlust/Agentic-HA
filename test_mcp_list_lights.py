import requests

url = "http://localhost:8081/mcp"
payload = {
    "jsonrpc": "2.0",
    "method": "search",
    "params": {},
    "id": 3
}
response = requests.post(url, json=payload)
result = response.json()["result"]

# Filter for entities that are lights
lights = [entity for entity in result if entity.get("entity_id", "").startswith("light.")]

print("All light entities:")
for light in lights:
    print(f"- {light['entity_id']}: {light.get('state')}")
