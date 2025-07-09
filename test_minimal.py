#!/usr/bin/env python3
"""
Test the minimal weather server
"""

import json
import subprocess
import sys
import time
import os

def test_minimal_server():
    """Test the minimal weather server"""
    print("🧪 Testing Minimal MCP Weather Server")
    print("=" * 40)
    
    # Check if API key is set
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("⚠️  Warning: OPENWEATHER_API_KEY not set in environment")
        print("   Set it in .env file or environment variables")
    else:
        print("✅ API key found in environment")
    
    try:
        # Start the server
        print("\n🚀 Starting server...")
        process = subprocess.Popen(
            [sys.executable, "minimal_weather_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=os.environ.copy()  # Pass current environment
        )
        
        def send_message(msg_dict):
            """Send a message and get response"""
            msg = json.dumps(msg_dict) + "\n"
            process.stdin.write(msg)
            process.stdin.flush()
            response = process.stdout.readline()
            return json.loads(response.strip()) if response.strip() else None
        
        # Test 1: Initialize
        print("📡 Testing initialization...")
        init_response = send_message({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        })
        
        if init_response and "result" in init_response:
            print("✅ Initialization successful")
            server_info = init_response["result"]["serverInfo"]
            print(f"   Server: {server_info['name']} v{server_info['version']}")
        else:
            print("❌ Initialization failed")
            print(f"   Response: {init_response}")
        
        # Test 2: List tools
        print("\n🔧 Testing tool listing...")
        tools_response = send_message({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        })
        
        if tools_response and "result" in tools_response:
            tools = tools_response["result"]["tools"]
            print(f"✅ Found {len(tools)} tool(s):")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print("❌ Tool listing failed")
            print(f"   Response: {tools_response}")
        
        # Test 3: Call weather tool
        print("\n🌤️  Testing weather tool...")
        weather_response = send_message({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_weather",
                "arguments": {"location": "London"}
            }
        })
        
        if weather_response and "result" in weather_response:
            content = weather_response["result"]["content"][0]["text"]
            print("✅ Weather tool successful")
            print("📋 Weather data:")
            print(content)
        elif weather_response and "error" in weather_response:
            print("⚠️  Weather tool returned error:")
            print(f"   {weather_response['error']['message']}")
        else:
            print("❌ Weather tool failed")
            print(f"   Response: {weather_response}")
        
        # Cleanup
        process.terminate()
        process.wait(timeout=5)
        
        print("\n🎉 Test completed!")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        if 'process' in locals():
            process.terminate()

if __name__ == "__main__":
    test_minimal_server()