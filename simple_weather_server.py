#!/usr/bin/env python3
"""
Simple MCP Weather Server - Minimal version for testing
"""

import asyncio
import json
import sys
import os
from typing import Any, Dict, List
from urllib.request import urlopen
from urllib.parse import urlencode

# Simple MCP server implementation
class SimpleMCPServer:
    def __init__(self, name: str):
        self.name = name
        self.tools = []
    
    def add_tool(self, name: str, description: str, schema: Dict[str, Any]):
        self.tools.append({
            "name": name,
            "description": description,
            "inputSchema": schema
        })
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id", 1)  # Provide default ID
        
        # Ensure request_id is not None
        if request_id is None:
            request_id = 1
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": self.name,
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "notifications/initialized":
            # Handle initialized notification (no response needed)
            return None
            
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": self.tools
                }
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            try:
                if tool_name == "get_weather":
                    result = await get_weather(arguments.get("location", ""))
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": result
                                }
                            ]
                        }
                    }
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": f"Tool execution error: {str(e)}"
                    }
                }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Unknown method: {method}"
                }
            }

async def get_weather(location: str) -> str:
    """Get weather using OpenWeatherMap API"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    if not api_key:
        return "Error: OPENWEATHER_API_KEY not set"
    
    if not location:
        return "Error: Location not provided"
    
    try:
        # Build URL
        params = {
            "q": location,
            "appid": api_key,
            "units": "metric"
        }
        url = f"https://api.openweathermap.org/data/2.5/weather?{urlencode(params)}"
        
        # Make request
        with urlopen(url) as response:
            data = json.loads(response.read().decode())
        
        # Format response
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        description = data["weather"][0]["description"]
        
        return f"""Weather in {data['name']}, {data['sys']['country']}:
🌡️ Temperature: {temp}°C (feels like {feels_like}°C)
☁️ Conditions: {description.title()}
💧 Humidity: {humidity}%"""
        
    except Exception as e:
        return f"Error getting weather for {location}: {str(e)}"

async def main():
    # Create server
    server = SimpleMCPServer("simple-weather-server")
    
    # Add weather tool
    server.add_tool(
        "get_weather",
        "Get current weather for a location",
        {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name"
                }
            },
            "required": ["location"]
        }
    )
    
    # Main loop
    try:
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                request = json.loads(line)
                response = await server.handle_request(request)
                
                # Only send response if it's not None (for notifications)
                if response is not None:
                    print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    asyncio.run(main())