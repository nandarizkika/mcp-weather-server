# MCP Weather Server

A Model Context Protocol (MCP) server that provides weather information and forecasts using the OpenWeatherMap API.

## Features

- 🌤️ Get current weather conditions for any city
- 📅 Get 5-day weather forecasts
- 🌡️ Temperature, humidity, wind speed, and atmospheric pressure
- ☁️ Weather descriptions and conditions
- 🌍 Works with cities worldwide

## Tools Available

### `get_weather`
Get current weather conditions for a specified location.

**Parameters:**
- `location` (required): City name (e.g., "London", "Jakarta", "New York")

**Example:** "What's the weather in Jakarta?"

### `get_weather_forecast` 
Get a 5-day weather forecast for a specified location.

**Parameters:**
- `location` (required): City name
- `days` (optional): Number of days to forecast (1-5, default: 5)

**Example:** "What's the 5-day forecast for London?"

## Prerequisites

- Python 3.7+
- OpenWeatherMap API key (free tier available)
- Claude Desktop application

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/mcp-weather-server.git
   cd mcp-weather-server
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # or
   source .venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Get an API key:**
   - Sign up at [OpenWeatherMap](https://openweathermap.org/api)
   - Get your free API key

5. **Set up environment variables:**
   - Copy `.env.example` to `.env`
   - Add your API key to the `.env` file:
     ```
     OPENWEATHER_API_KEY=your_api_key_here
     ```

## Configuration

### Claude Desktop Setup

1. **Locate your Claude Desktop config file:**
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux:** `~/.config/Claude/claude_desktop_config.json`

2. **Add the weather server configuration:**
   ```json
   {
     "mcpServers": {
       "weather": {
         "command": "path/to/your/project/.venv/Scripts/python.exe",
         "args": ["path/to/your/project/minimal_weather_server.py"],
         "env": {
           "OPENWEATHER_API_KEY": "your_api_key_here"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

## Testing

Test the server independently:

```bash
python test_minimal.py
```

Or test specific functionality:

```bash
python debug_server.py
```

## Usage Examples

Once configured with Claude Desktop, you can ask natural language questions:

- "What's the weather in Jakarta?"
- "Get me the current weather for London"
- "What's the 5-day forecast for Tokyo?"
- "How's the weather in Singapore today?"
- "Show me the weather forecast for Bandung"

## Project Structure

```
mcp-weather-server/
├── minimal_weather_server.py    # Main MCP server
├── simple_weather_server.py     # Alternative simple server
├── weather_server.py           # Original MCP library version
├── test_minimal.py             # Test script
├── debug_server.py             # Debug utilities
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .env                      # Environment variables (not in git)
├── .gitignore               # Git ignore rules
└── README.md               # This file
```

## API Reference

This server uses the [OpenWeatherMap API](https://openweathermap.org/api) to fetch weather data.

## Troubleshooting

### Common Issues

1. **"API key not found" error:**
   - Ensure your `.env` file contains `OPENWEATHER_API_KEY=your_actual_key`
   - Verify the API key is valid and active

2. **"Server disconnected" in Claude:**
   - Check that file paths in the config are correct
   - Ensure Python executable path is accurate
   - Restart Claude Desktop after config changes

3. **"Location not found" error:**
   - Try using different city name variations
   - Include country name for ambiguous cities (e.g., "London, UK")

### Debug Steps

1. Test the server independently:
   ```bash
   python test_minimal.py
   ```

2. Check server logs in Claude Desktop
3. Verify API key permissions at OpenWeatherMap

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OpenWeatherMap](https://openweathermap.org/) for providing the weather API
- [Anthropic](https://anthropic.com/) for Claude and the MCP specification
- MCP community for protocol documentation and examples

## Support

If you encounter any issues or have questions:

1. Check the [troubleshooting section](#troubleshooting)
2. Review [OpenWeatherMap API docs](https://openweathermap.org/api)
3. Open an issue on GitHub

---

Made with ❤️ for the MCP community