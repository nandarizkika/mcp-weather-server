"""
Test script for the MCP Weather Server
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_server():
    """Test the weather server"""
    print("Testing MCP Weather Server...")
    
    if not Path(".env").exists():
        print("❌ .env file not found. Please create it with your OpenWeatherMap API key.")
        return False
    
    try:
        process = subprocess.Popen(
            [sys.executable, "weather_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            if "result" in response:
                print("✅ Server initialized successfully!")
                print(f"   Server: {response['result']['serverInfo']['name']}")
                print(f"   Version: {response['result']['serverInfo']['version']}")
                
                list_tools_request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list"
                }
                
                process.stdin.write(json.dumps(list_tools_request) + "\n")
                process.stdin.flush()
                
                tools_response = process.stdout.readline()
                if tools_response:
                    tools_data = json.loads(tools_response)
                    if "result" in tools_data:
                        tools = tools_data["result"]["tools"]
                        print(f"✅ Found {len(tools)} tools:")
                        for tool in tools:
                            print(f"   - {tool['name']}: {tool['description']}")
                
                process.terminate()
                return True
            else:
                print("❌ Server initialization failed")
                print(f"   Error: {response.get('error', 'Unknown error')}")
        
        process.terminate()
        return False
        
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_server())
    sys.exit(0 if success else 1)