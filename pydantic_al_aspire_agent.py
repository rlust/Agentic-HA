import os
import json
from dotenv import load_dotenv
load_dotenv()
from pydantic_ai.agent import Agent
from pydantic_ai.mcp import MCPServerHTTP
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
        client = sseclient.SSEClient(resp.raw)
        for i, event in enumerate(client.events()):
            print(f"[DEBUG] SSE event {i}: type={event.event!r} data={event.data!r}")
            if i >= 3:
                break
    except Exception as e:
        print("[DEBUG] Exception while reading SSE events:", repr(e))
    finally:
        resp.close()

def get_aspire_mcp_server():
    """Return an MCPServerHTTP instance for Aspire MCP (SSE transport)."""
    return MCPServerHTTP(
        url="http://192.168.100.101:8123/mcp_server/sse",
        headers={
            "Authorization": f"Bearer {os.environ.get('ASPIRE_MCP_TOKEN')}",
            "Accept": "text/event-stream"
        },
        timeout=15,  # Increased timeout for slow connections
        sse_read_timeout=300,
    )

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
    # Create agent with Aspire MCP server
    debug_mcp_events()
    mcp_server = get_aspire_mcp_server()
    print("[DEBUG] MCP server configured:", mcp_server)
    llm = get_openai_model()
    agent = Agent(
        model=llm,
        name="AspireHomeAssistantAgent",
        mcp_servers=[mcp_server],
        tools=[
            Tool(list_entities, name="list_entities", description="List all Home Assistant entities."),
            Tool(
    list_lights,
    name="list_lights",
    description=(
        "List all Home Assistant light entities (entity_ids starting with 'light.'). "
        "Use this tool to answer any question about listing, showing, or finding lights, "
        "such as 'list all lights', 'what lights are available', 'show me my lights', 'which lights do I have', etc."
    )
),
            Tool(get_state, name="get_state", description="Get the state and attributes of an entity."),
            Tool(turn_on, name="turn_on", description="Turn on a Home Assistant entity (e.g., light, switch)."),
            Tool(turn_off, name="turn_off", description="Turn off a Home Assistant entity (e.g., light, switch)."),
            Tool(set_value, name="set_value", description="Set a value for a Home Assistant entity (e.g., input_number, climate, etc.)"),
        ]
    )
    # Start custom CLI loop (interactive)
    print("Aspire Home Assistant Agent CLI (type 'exit' to quit)")
    while True:
        user_input = input("pai ➤ ")
        if user_input.strip().lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        result = agent.run_sync(user_input)
        print(result.output)

if __name__ == "__main__":
    main()
