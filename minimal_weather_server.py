#!/usr/bin/env python3
"""
Minimal MCP Weather Server - Based on official MCP specification
"""

import asyncio
import json
import sys
import os
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional

class MCPWeatherServer:
    def __init__(self):
        self.server_info = {
            "name": "weather-server",
            "version": "1.0.0"
        }
        
    async def handle_message(self, message: str) -> Optional[str]:
        """Handle incoming JSON-RPC message"""
        try:
            data = json.loads(message.strip())
            response = await self.process_request(data)
            return json.dumps(response) if response else None
        except json.JSONDecodeError:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"}
            })
        except Exception as e:
            return json.dumps({
                "jsonrpc": "2.0", 
                "id": data.get("id"),
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            })
    
    async def process_request(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process JSON-RPC request"""
        method = data.get("method")
        params = data.get("params", {})
        request_id = data.get("id")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": self.server_info
                }
            }
        
        elif method == "notifications/initialized":
            # Notification - no response needed
            return None
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "get_weather",
                            "description": "Get current weather for a location",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "location": {
                                        "type": "string",
                                        "description": "City name (e.g., 'London', 'New York')"
                                    }
                                },
                                "required": ["location"]
                            }
                        },
                        {
                            "name": "get_weather_forecast",
                            "description": "Get 5-day weather forecast for a location",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "location": {
                                        "type": "string",
                                        "description": "City name (e.g., 'London', 'New York')"
                                    },
                                    "days": {
                                        "type": "number",
                                        "description": "Number of days to forecast (1-5)",
                                        "minimum": 1,
                                        "maximum": 5,
                                        "default": 5
                                    }
                                },
                                "required": ["location"]
                            }
                        }
                    ]
                }
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "get_weather":
                try:
                    weather_data = await self.get_weather(arguments.get("location", ""))
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": weather_data
                                }
                            ]
                        }
                    }
                except Exception as e:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": f"Weather API error: {str(e)}"
                        }
                    }
            elif tool_name == "get_weather_forecast":
                try:
                    forecast_data = await self.get_weather_forecast(
                        arguments.get("location", ""),
                        arguments.get("days", 5)
                    )
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": forecast_data
                                }
                            ]
                        }
                    }
                except Exception as e:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": f"Forecast API error: {str(e)}"
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
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Unknown method: {method}"
                }
            }
    
    async def get_weather(self, location: str) -> str:
        """Get weather data from OpenWeatherMap"""
        api_key = os.getenv("OPENWEATHER_API_KEY")
        
        if not api_key:
            return "❌ Error: OPENWEATHER_API_KEY environment variable not set"
        
        if not location:
            return "❌ Error: No location provided"
        
        try:
            # Build API URL
            base_url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": location,
                "appid": api_key,
                "units": "metric"
            }
            url = f"{base_url}?{urllib.parse.urlencode(params)}"
            
            # Make API request
            with urllib.request.urlopen(url) as response:
                if response.status != 200:
                    return f"❌ Error: Weather API returned status {response.status}"
                
                weather_data = json.loads(response.read().decode())
            
            # Format weather information
            city = weather_data["name"]
            country = weather_data["sys"]["country"]
            temp = weather_data["main"]["temp"]
            feels_like = weather_data["main"]["feels_like"]
            humidity = weather_data["main"]["humidity"]
            pressure = weather_data["main"]["pressure"]
            description = weather_data["weather"][0]["description"].title()
            wind_speed = weather_data["wind"]["speed"]
            
            weather_report = f"""🌤️ Weather Report for {city}, {country}

🌡️ Temperature: {temp}°C (feels like {feels_like}°C)
☁️ Conditions: {description}
💧 Humidity: {humidity}%
🌪️ Wind Speed: {wind_speed} m/s
📊 Pressure: {pressure} hPa"""
            
            return weather_report
            
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return f"❌ Error: Location '{location}' not found"
            else:
                return f"❌ Error: HTTP {e.code} - {e.reason}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    async def get_weather_forecast(self, location: str, days: int = 5) -> str:
        """Get weather forecast from OpenWeatherMap"""
        api_key = os.getenv("OPENWEATHER_API_KEY")
        
        if not api_key:
            return "❌ Error: OPENWEATHER_API_KEY environment variable not set"
        
        if not location:
            return "❌ Error: No location provided"
        
        try:
            # Build API URL for forecast
            base_url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {
                "q": location,
                "appid": api_key,
                "units": "metric"
            }
            url = f"{base_url}?{urllib.parse.urlencode(params)}"
            
            # Make API request
            with urllib.request.urlopen(url) as response:
                if response.status != 200:
                    return f"❌ Error: Weather API returned status {response.status}"
                
                forecast_data = json.loads(response.read().decode())
            
            # Format forecast information
            city = forecast_data["city"]["name"]
            country = forecast_data["city"]["country"]
            
            forecast_report = f"📅 5-Day Weather Forecast for {city}, {country}\n\n"
            
            # Group forecasts by day
            daily_forecasts = {}
            for item in forecast_data["list"]:
                date = item["dt_txt"].split()[0]  # Extract date part
                if date not in daily_forecasts:
                    daily_forecasts[date] = []
                daily_forecasts[date].append(item)
            
            # Display daily summary (limit to requested days)
            for i, (date, forecasts) in enumerate(list(daily_forecasts.items())[:days]):
                # Find forecast closest to midday (12:00)
                midday_forecast = min(forecasts, key=lambda x: abs(12 - int(x["dt_txt"].split()[1].split(":")[0])))
                
                temp = midday_forecast["main"]["temp"]
                temp_min = min(f["main"]["temp_min"] for f in forecasts)
                temp_max = max(f["main"]["temp_max"] for f in forecasts)
                description = midday_forecast["weather"][0]["description"].title()
                humidity = midday_forecast["main"]["humidity"]
                
                # Format date nicely
                from datetime import datetime
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                day_name = date_obj.strftime("%A, %B %d")
                
                forecast_report += f"🗓️ **{day_name}**\n"
                forecast_report += f"   🌡️ {temp_min:.1f}°C - {temp_max:.1f}°C\n"
                forecast_report += f"   ☁️ {description}\n"
                forecast_report += f"   💧 Humidity: {humidity}%\n\n"
            
            return forecast_report
            
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return f"❌ Error: Location '{location}' not found"
            else:
                return f"❌ Error: HTTP {e.code} - {e.reason}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

async def main():
    """Main server loop"""
    server = MCPWeatherServer()
    
    try:
        while True:
            # Read line from stdin
            line = sys.stdin.readline()
            if not line:  # EOF
                break
                
            # Process message
            response = await server.handle_message(line)
            
            # Send response if needed
            if response:
                print(response, flush=True)
                
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(json.dumps({
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32603, "message": f"Server error: {str(e)}"}
        }), flush=True)

if __name__ == "__main__":
    asyncio.run(main())