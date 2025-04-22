import os
import json
from dotenv import load_dotenv
load_dotenv()
from pydantic_ai.agent import Agent
from pydantic_ai.mcp import MCPServerHTTP
from pathlib import Path

# Load MCP config
with open(Path(__file__).parent / "mcp_config.json") as f:
    MCP_CONFIG = json.load(f)["mcpServers"]

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai._cli import cli
from pydantic_ai.tools import Tool
import requests

def debug_mcp_events():
    import sseclient
    import requests
    print("[DEBUG] Connecting to MCP SSE endpoint for event debug...")
    resp = requests.get(
        "http://192.168.100.101:8123/mcp_server/sse",
        headers={
            "Authorization": f"Bearer {os.environ.get('ASPIRE_MCP_TOKEN')}",
            "Accept": "text/event-stream"
        },
        stream=True,
        timeout=15,
    )
    resp.encoding = 'utf-8'
    try:
        client = sseclient.SSEClient(resp.iter_content(decode_unicode=True))
        for i, event in enumerate(client.events()):
            print(f"[DEBUG] SSE event {i}: type={event.event!r} data={event.data!r}")
            if i >= 3:
                break
    except Exception as e:
        print("[DEBUG] Exception while reading SSE events:", repr(e))
    finally:
        resp.close()

def get_aspire_mcp_server():
    """Return an MCPServerHTTP instance for Aspire New MCP (SSE transport)."""
    cfg = MCP_CONFIG["Aspire New"]["env"]
    token = os.environ.get("ASPIRE_MCP_TOKEN")
    headers = {"Accept": "text/event-stream"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    print("[DEBUG] Attempting MCPServerHTTP connection with:")
    print(f"  URL: {cfg['SSE_URL']}")
    print(f"  Headers: {headers}")
    try:
        server = MCPServerHTTP(
            url=cfg["SSE_URL"],
            headers=headers,
            timeout=15,
            sse_read_timeout=300,
        )
        print("[DEBUG] MCPServerHTTP instance created successfully.")
        return server
    except Exception as e:
        print("[DEBUG] MCPServerHTTP connection failed:", repr(e), type(e), e.args)
        raise

def get_context7_mcp_server():
    """Return an MCPServerHTTP instance for context7 MCP (SSE transport), configurable via .env or mcp_config.json."""
    url = os.environ.get("CONTEXT7_MCP_SSE_URL")
    token = os.environ.get("CONTEXT7_MCP_TOKEN")
    if not url:
        cfg = MCP_CONFIG.get("context7", {}).get("env", {})
        url = cfg.get("SSE_URL")
        token = cfg.get("API_ACCESS_TOKEN")
    if url:
        headers = {"Accept": "text/event-stream"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return MCPServerHTTP(url=url, headers=headers, timeout=15, sse_read_timeout=300)
    return None

def get_openai_model():
    """Return an OpenAIModel instance using env variables for model and base URL."""
    return OpenAIModel(
        model_name=os.environ["OPENAI_MODEL"]
    )

# --- Aspire Home Assistant Tool Functions ---

API_URL = "http://192.168.100.101:8123/api"
API_TOKEN = os.environ.get("ASPIRE_MCP_TOKEN")
HEADERS = {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}

def list_entities() -> list[str]:
    resp = requests.get(f"{API_URL}/states", headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return [e["entity_id"] for e in resp.json()]

def list_entities_by_domain(domain: str) -> list[str]:
    resp = requests.get(f"{API_URL}/states", headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return [e["entity_id"] for e in resp.json() if e["entity_id"].startswith(f"{domain}.")]

def filter_entities_by_state(domain: str, state: str) -> list[str]:
    resp = requests.get(f"{API_URL}/states", headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return [e["entity_id"] for e in resp.json() if e["entity_id"].startswith(f"{domain}.") and e["state"] == state]

def show_entity_attributes(entity_id: str) -> dict:
    resp = requests.get(f"{API_URL}/states/{entity_id}", headers=HEADERS, timeout=10)
    if resp.status_code != 200:
        print(f"Entity {entity_id} not found.")
        return {}
    data = resp.json()
    print(json.dumps(data.get("attributes", {}), indent=2, sort_keys=True))
    return data.get("attributes", {})


def list_lights() -> list[str]:
    """Return a list of all Home Assistant light entities (entity_ids starting with 'light.')."""
    print("[DEBUG] list_lights tool called")
    resp = requests.get(f"{API_URL}/states", headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return [e["entity_id"] for e in resp.json() if e["entity_id"].startswith("light.")]

def get_state(entity_id: str) -> dict:
    resp = requests.get(f"{API_URL}/states/{entity_id}", headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()

def turn_on(entity_id: str) -> str:
    domain = entity_id.split(".")[0]
    resp = requests.post(f"{API_URL}/services/{domain}/turn_on", headers=HEADERS, json={"entity_id": entity_id}, timeout=10)
    resp.raise_for_status()
    return f"Turned on {entity_id}"

def turn_off(entity_id: str) -> str:
    domain = entity_id.split(".")[0]
    resp = requests.post(f"{API_URL}/services/{domain}/turn_off", headers=HEADERS, json={"entity_id": entity_id}, timeout=10)
    resp.raise_for_status()
    return f"Turned off {entity_id}"

def set_value(entity_id: str, value: float) -> str:
    domain = entity_id.split(".")[0]
    # This example targets input_number; extend for other domains as needed
    if domain == "input_number":
        resp = requests.post(f"{API_URL}/services/input_number/set_value", headers=HEADERS, json={"entity_id": entity_id, "value": value}, timeout=10)
        resp.raise_for_status()
        return f"Set {entity_id} to {value}"
    return f"Setting value for domain {domain} is not implemented."

def main():
    """Simple CLI for Aspire MCP server only."""
    try:
        mcp_aspire = get_aspire_mcp_server()
    except Exception as e:
        print("[ERROR] Could not initialize Aspire MCP server. Exception details:")
        print(repr(e), type(e), e.args)
        return
    if not mcp_aspire:
        print("[ERROR] Could not initialize Aspire MCP server. Check your configuration.")
        return
    llm = get_openai_model()
    agent = Agent(
        model=llm,
        name="AspireHomeAssistantAgent",
        mcp_servers=[mcp_aspire],
        tools=[
            Tool(list_entities, name="list_entities", description="List all Home Assistant entities."),
            Tool(list_lights, name="list_lights", description="List all Home Assistant light entities."),
            Tool(get_state, name="get_state", description="Get the state of a Home Assistant entity."),
            Tool(turn_on, name="turn_on", description="Turn on a Home Assistant entity (e.g., light, switch, etc.)."),
            Tool(turn_off, name="turn_off", description="Turn off a Home Assistant entity (e.g., light, switch, etc.)."),
            Tool(set_value, name="set_value", description="Set a value for a Home Assistant entity (e.g., input_number, climate, etc.)"),
            Tool(list_entities_by_domain, name="list_entities_by_domain", description="List all entities of a given domain (e.g., sensor, light, switch)."),
            Tool(filter_entities_by_state, name="filter_entities_by_state", description="List all entities of a domain in a given state (e.g., all lights that are on)."),
            Tool(show_entity_attributes, name="show_entity_attributes", description="Show all attributes for a given entity in pretty-printed JSON."),
        ]
    )
    print("Aspire Home Assistant Agent CLI (type 'exit' to quit)")
    while True:
        user_input = input("pai ➤ ")
        if user_input.strip().lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        try:
            result = agent.run_sync(user_input)
            print(result.output)
        except Exception as e:
            print(f"[ERROR] {e}")
            print("[DEBUG] Exception details:", repr(e), type(e), e.args)


if __name__ == "__main__":
    main()
