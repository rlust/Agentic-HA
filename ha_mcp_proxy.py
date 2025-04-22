import os
import sys
import json
import asyncio
import logging
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HA_URL = os.getenv("HA_URL", "http://localhost:8123")
HA_TOKEN = os.getenv("HA_TOKEN")
PORT = int(os.getenv("PORT", "8081"))

HEADERS = {"Authorization": f"Bearer {HA_TOKEN}", "Content-Type": "application/json"}

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# --- MCP Protocol Handler ---
def mcp_response(result, id=None):
    return {"jsonrpc": "2.0", "result": result, "id": id}

def mcp_error(message, id=None):
    return {"jsonrpc": "2.0", "error": {"message": message}, "id": id}

async def ha_rest_call(path, method="GET", data=None):
    url = f"{HA_URL}{path}"
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                resp = await client.get(url, headers=HEADERS)
            elif method == "POST":
                resp = await client.post(url, headers=HEADERS, json=data)
            else:
                resp = await client.request(method, url, headers=HEADERS, json=data)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logging.error(f"HA REST error: {e}")
            return {"error": str(e)}

# --- FastAPI HTTP MCP endpoint ---
@app.post("/mcp")
async def mcp_http(request: Request):
    payload = await request.json()
    method = payload.get("method")
    params = payload.get("params", {})
    req_id = payload.get("id")
    if method == "search":
        # Example: list all states
        result = await ha_rest_call("/api/states")
        return JSONResponse(mcp_response(result, req_id))
    elif method == "call_service":
        domain = params.get("domain")
        service = params.get("service")
        service_data = params.get("service_data", {})
        if not (domain and service):
            return JSONResponse(mcp_error("Missing domain/service", req_id))
        result = await ha_rest_call(f"/api/services/{domain}/{service}", method="POST", data=service_data)
        return JSONResponse(mcp_response(result, req_id))
    elif method == "list_services":
        # List all available Home Assistant services
        result = await ha_rest_call("/api/services")
        return JSONResponse(mcp_response(result, req_id))
    else:
        return JSONResponse(mcp_error("Unknown method", req_id))


# --- Stdio MCP mode ---
async def mcp_stdio():
    logging.info("MCP stdio mode started. Send JSON-RPC requests via stdin.")
    loop = asyncio.get_event_loop()
    while True:
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            break
        try:
            payload = json.loads(line)
            method = payload.get("method")
            params = payload.get("params", {})
            req_id = payload.get("id")
            if method == "search":
                result = await ha_rest_call("/api/states")
                response = mcp_response(result, req_id)
            elif method == "call_service":
                domain = params.get("domain")
                service = params.get("service")
                service_data = params.get("service_data", {})
                if not (domain and service):
                    response = mcp_error("Missing domain/service", req_id)
                else:
                    result = await ha_rest_call(f"/api/services/{domain}/{service}", method="POST", data=service_data)
                    response = mcp_response(result, req_id)
            elif method == "list_services":
                result = await ha_rest_call("/api/services")
                response = mcp_response(result, req_id)
            else:
                response = mcp_error("Unknown method", req_id)
            print(json.dumps(response), flush=True)
        except Exception as e:
            print(json.dumps(mcp_error(f"Parse error: {e}")), flush=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--stdio", action="store_true", help="Run in stdio mode (for MCP clients)")
    args = parser.parse_args()
    if args.stdio:
        asyncio.run(mcp_stdio())
    else:
        import uvicorn
        uvicorn.run("ha_mcp_proxy:app", host="0.0.0.0", port=PORT, reload=False)
