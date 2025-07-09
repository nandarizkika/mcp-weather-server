"""
MCP Weather Server - A simple Model Context Protocol server for weather data
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    EmbeddedResource,
    LoggingLevel
)
import os
from dotenv import load_dotenv

load_dotenv()

app = Server("weather-server")

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"

@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available weather tools"""
    return [
        Tool(
            name="get_current_weather",
            description="Get current weather for a specific location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name (e.g., 'London', 'New York', 'Jakarta')"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial", "kelvin"],
                        "default": "metric",
                        "description": "Temperature units (metric for Celsius, imperial for Fahrenheit)"
                    }
                },
                "required": ["location"]
            }
        ),
        Tool(
            name="get_weather_forecast",
            description="Get 5-day weather forecast for a specific location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name (e.g., 'London', 'New York', 'Jakarta')"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial", "kelvin"],
                        "default": "metric",
                        "description": "Temperature units"
                    }
                },
                "required": ["location"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    
    if not API_KEY:
        return [TextContent(
            type="text",
            text="Error: OpenWeatherMap API key not configured. Please set OPENWEATHER_API_KEY environment variable."
        )]
    
    try:
        if name == "get_current_weather":
            result = await get_current_weather(
                location=arguments["location"],
                units=arguments.get("units", "metric")
            )
            return [TextContent(type="text", text=result)]
            
        elif name == "get_weather_forecast":
            result = await get_weather_forecast(
                location=arguments["location"],
                units=arguments.get("units", "metric")
            )
            return [TextContent(type="text", text=result)]
            
        else:
            return [TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )]
            
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error calling tool '{name}': {str(e)}"
        )]

async def get_current_weather(location: str, units: str = "metric") -> str:
    """Get current weather for a location"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/weather",
            params={
                "q": location,
                "appid": API_KEY,
                "units": units
            }
        )
        
        if response.status_code != 200:
            return f"Error: Could not get weather for {location}. Status: {response.status_code}"
        
        data = response.json()
        
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        description = data["weather"][0]["description"]
        wind_speed = data["wind"]["speed"]
        
        unit_symbol = "°C" if units == "metric" else "°F" if units == "imperial" else "K"
        
        weather_info = f"""Current Weather for {data['name']}, {data['sys']['country']}:
        
🌡️ Temperature: {temp}{unit_symbol} (feels like {feels_like}{unit_symbol})
☁️ Conditions: {description.title()}
💧 Humidity: {humidity}%
🌪️ Wind Speed: {wind_speed} {'m/s' if units == 'metric' else 'mph'}
📊 Pressure: {pressure} hPa
"""
        
        return weather_info

async def get_weather_forecast(location: str, units: str = "metric") -> str:
    """Get 5-day weather forecast for a location"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/forecast",
            params={
                "q": location,
                "appid": API_KEY,
                "units": units
            }
        )
        
        if response.status_code != 200:
            return f"Error: Could not get forecast for {location}. Status: {response.status_code}"
        
        data = response.json()
        
        unit_symbol = "°C" if units == "metric" else "°F" if units == "imperial" else "K"
        
        forecast_info = f"5-Day Weather Forecast for {data['city']['name']}, {data['city']['country']}:\n\n"
        
        daily_forecasts = {}
        for item in data["list"]:
            date = item["dt_txt"].split()[0] 
            if date not in daily_forecasts:
                daily_forecasts[date] = []
            daily_forecasts[date].append(item)
        
        for date, forecasts in list(daily_forecasts.items())[:5]:
            midday_forecast = min(forecasts, key=lambda x: abs(12 - int(x["dt_txt"].split()[1].split(":")[0])))
            
            temp = midday_forecast["main"]["temp"]
            temp_min = min(f["main"]["temp_min"] for f in forecasts)
            temp_max = max(f["main"]["temp_max"] for f in forecasts)
            description = midday_forecast["weather"][0]["description"]
            
            forecast_info += f"📅 {date}: {description.title()}\n"
            forecast_info += f"   🌡️ {temp_min}{unit_symbol} - {temp_max}{unit_symbol}\n\n"
        
        return forecast_info

async def main():
    """Main entry point"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="weather-server",
                server_version="1.0.0",
                capabilities=app.get_capabilities()
            )
        )

if __name__ == "__main__":
    asyncio.run(main())