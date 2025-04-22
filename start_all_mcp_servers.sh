#!/bin/bash
# Script to start all MCP servers as defined in mcp_config.json

# Start context7 MCP server
echo "Starting context7 MCP server..."
npx -y @upstash/context7-mcp@latest &

# Start Home Assistant MCP server
echo "Starting Home Assistant MCP server..."
SSE_URL='http://100.72.110.22:8123/mcp_server/sse' \
API_ACCESS_TOKEN='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIyMjBmYjQ5NmVkNmQ0N2I1ODZmMjc2NDc4NTVlNzE0ZSIsImlhdCI6MTc0MzM5OTAwNiwiZXhwIjoyMDU4NzU5MDA2fQ.eQcQIPBV555OuVeAB3pJBpUypbEYNsymwyShOx3b8zo' \
mcp-proxy &

# Start Aspire New MCP server
echo "Starting Aspire New MCP server..."
SSE_URL='http://192.168.100.101:8123/mcp_server/sse' \
API_ACCESS_TOKEN='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjZjkzODQxNjBhN2Y0NjM2YjgzYTNkYTYyYjNlMWY1MiIsImlhdCI6MTc0NTI2MzI1MywiZXhwIjoyMDYwNjIzMjUzfQ.qNueMkpSlP7S0Os18u3yHWKR4rY2a2GkbEqmgpglWGY' \
mcp-proxy &

echo "All MCP servers started."

echo
# List all running MCP servers
echo "Listing running MCP servers:"
ps aux | grep -E 'npx -y @upstash/context7-mcp@latest|mcp-proxy' | grep -v grep | awk '{print $2, $11, $12, $13, $14}'
echo
