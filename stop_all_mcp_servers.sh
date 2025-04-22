#!/bin/bash
# Script to stop all MCP servers started by start_all_mcp_servers.sh

# Stop context7 MCP server
CONTEXT7_PID=$(pgrep -f "npx -y @upstash/context7-mcp@latest")
if [ -n "$CONTEXT7_PID" ]; then
  echo "Stopping context7 MCP server (PID $CONTEXT7_PID)..."
  kill $CONTEXT7_PID
else
  echo "context7 MCP server not running."
fi

# Stop Home Assistant MCP server
HA_PID=$(pgrep -f "mcp-proxy.*100.72.110.22:8123")
if [ -n "$HA_PID" ]; then
  echo "Stopping Home Assistant MCP server (PID $HA_PID)..."
  kill $HA_PID
else
  echo "Home Assistant MCP server not running."
fi

# Stop Aspire New MCP server
ASPIRE_PID=$(pgrep -f "mcp-proxy.*192.168.100.101:8123")
if [ -n "$ASPIRE_PID" ]; then
  echo "Stopping Aspire New MCP server (PID $ASPIRE_PID)..."
  kill $ASPIRE_PID
else
  echo "Aspire New MCP server not running."
fi

echo "All MCP servers stopped."
