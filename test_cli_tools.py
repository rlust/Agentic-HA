"""
Automated test script for agentic Home Assistant CLI tools.
This script will test the REST API endpoints directly, not via the CLI, to ensure all tool logic works.
Fill in .env with correct values before running.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://192.168.100.101:8123/api")
TOKEN = os.getenv("ASPIRE_MCP_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def test_list_entities():
    resp = requests.get(f"{API_URL}/states", headers=HEADERS, timeout=10)
    resp.raise_for_status()
    entities = [e["entity_id"] for e in resp.json()]
    print("Entities:", entities[:10], "... (total:", len(entities), ")")
    return entities

def test_list_lights():
    entities = test_list_entities()
    lights = [e for e in entities if e.startswith("light.")]
    print("Lights:", lights)
    return lights

def test_get_state(entity_id):
    resp = requests.get(f"{API_URL}/states/{entity_id}", headers=HEADERS, timeout=10)
    resp.raise_for_status()
    state = resp.json()
    print(f"State for {entity_id}:", state)
    return state

def test_turn_on(entity_id):
    domain = entity_id.split(".")[0]
    resp = requests.post(f"{API_URL}/services/{domain}/turn_on", headers=HEADERS, json={"entity_id": entity_id}, timeout=10)
    resp.raise_for_status()
    print(f"Turned on {entity_id}")

def test_turn_off(entity_id):
    domain = entity_id.split(".")[0]
    resp = requests.post(f"{API_URL}/services/{domain}/turn_off", headers=HEADERS, json={"entity_id": entity_id}, timeout=10)
    resp.raise_for_status()
    print(f"Turned off {entity_id}")

def test_set_value(entity_id, value):
    domain = entity_id.split(".")[0]
    if domain == "input_number":
        resp = requests.post(f"{API_URL}/services/input_number/set_value", headers=HEADERS, json={"entity_id": entity_id, "value": value}, timeout=10)
        try:
            resp.raise_for_status()
            print(f"Set {entity_id} to {value}")
        except requests.HTTPError as e:
            print(f"Failed to set {entity_id} to {value}: {e}")
            try:
                print("Error response:", resp.json())
            except Exception:
                print("Error response (not JSON):", resp.text)
    else:
        print(f"set_value not implemented for domain {domain}")

def main():
    entities = test_list_entities()
    lights = [e for e in entities if e.startswith("light.")]
    if lights:
        test_get_state(lights[0])
        test_turn_on(lights[0])
        test_turn_off(lights[0])
    # Test set_value for all input_number entities
    input_numbers = [e for e in entities if e.startswith("input_number.")]
    for entity in input_numbers:
        state = test_get_state(entity)
        min_val = state['attributes'].get('min', 0)
        max_val = state['attributes'].get('max', 100)
        step = state['attributes'].get('step', 1)
        test_val = min_val + step if min_val + step <= max_val else min_val
        print(f"Trying to set {entity} to {test_val} (min={min_val}, max={max_val}, step={step})")
        test_set_value(entity, test_val)

if __name__ == "__main__":
    main()
