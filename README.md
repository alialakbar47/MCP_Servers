# HW5: Map Servers with Model Context Protocol

A complete implementation of three map-related servers using the Model Context Protocol (MCP) with OpenAI agent integration.

## 🚀 Quick Start (Docker - Recommended)

1. **Create `.env` file**:

   ```powershell
   [System.IO.File]::WriteAllText("$PWD\.env", "OPENAI_API_KEY=your-key-here`n", [System.Text.Encoding]::UTF8)
   ```

2. **Run automated demo** (6 pre-programmed queries):

   ```bash
   docker-compose up agent
   ```

3. **Run interactive mode** (type your own questions):
   ```bash
   docker-compose run --rm agent
   ```

That's it! The automated demo will show all server capabilities.

## 📁 Project Structure

```
HW5/
├── servers/
│   ├── geocoding_server.py    # Address ↔ coordinates, place search (3 operations)
│   ├── routing_server.py      # Routes, distances, nearby POIs (3 operations)
│   └── weather_server.py      # Current & forecast weather (3 operations)
├── tests/
│   ├── test_geocoding.py      # 9 tests
│   ├── test_routing.py        # 9 tests
│   └── test_weather.py        # 8 tests
├── agent_demo.py              # OpenAI agent integration
├── Dockerfile                 # Container definition
├── docker-compose.yml         # 4 services: agent, demo, test, dev
├── requirements.txt           # Python dependencies
├── .env                       # API keys (you create this)
├── summary.md                 # MCP concepts (required deliverable)
└── reflection.md              # Lessons learned (required deliverable)
```

## 🎯 What Each Server Does

| Server        | Operations                                                 | Examples                       |
| ------------- | ---------------------------------------------------------- | ------------------------------ |
| **Geocoding** | `geocode`, `reverse_geocode`, `search_places`              | "Where is the Eiffel Tower?"   |
| **Routing**   | `calculate_route`, `distance_matrix`, `find_nearby`        | "How far is NYC to LA?"        |
| **Weather**   | `get_weather`, `weather_forecast`, `location_weather_info` | "What's the weather in Tokyo?" |

**Total: 9 operations across 3 servers, 26 unit tests**

## 💻 Local Setup (Without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
echo OPENAI_API_KEY=your-key-here > .env

# Run demo
python agent_demo.py
```

## 🧪 Running Tests

**Docker**: `docker-compose run --rm test`  
**Local**: `pytest`

All 26 tests should pass (requires internet for API calls).

## 🐳 Docker Commands

```bash
# Automated demo (shows all features)
docker-compose up agent

# Interactive mode (type your questions)
docker-compose run --rm agent

# Run tests
docker-compose run --rm test

# Shell access
docker-compose run --rm dev

# Rebuild after changes
docker-compose build

# Cleanup
docker-compose down
```

## 💡 Example Queries to Try

- "What's the weather in Paris?"
- "How far is it from New York to Los Angeles?"
- "Find coffee shops near the Eiffel Tower"
- "What's the address of the Statue of Liberty?"
- "Show me a 7-day forecast for Tokyo"
- "Calculate the route from London to Manchester"

The automated demo (Option 1) runs these 6 queries:

1. Eiffel Tower geocoding
2. Reverse geocode Paris coordinates
3. NYC to LA distance
4. Paris weather
5. Tokyo 7-day forecast
6. Coffee shops near Eiffel Tower

## 🔧 Troubleshooting

**Can't type after `docker-compose up agent`?**
→ Use `docker-compose run --rm agent` for interactive input

**.env encoding errors?**
→ Recreate with UTF-8:

```powershell
[System.IO.File]::WriteAllText("$PWD\.env", "OPENAI_API_KEY=your-key-here`n", [System.Text.Encoding]::UTF8)
```

**Tests failing?**
→ Check internet connection (APIs need access)  
→ Verify Python 3.11+  
→ Reinstall: `pip install -r requirements.txt`

**Docker build fails?**
→ Ensure Docker Desktop is running  
→ Try: `docker-compose build --no-cache`

## 🛠️ Technologies

- **Python 3.11**: Async/await, aiohttp
- **OpenAI API**: Function calling (GPT-4)
- **Docker/Compose**: Multi-service containers
- **pytest**: Unit testing with pytest-asyncio
- **APIs**: OpenStreetMap Nominatim (geocoding), Open-Meteo (weather)

---

**For More Information**: See `summary.md` for MCP concepts and `reflection.md` for lessons learned during development.
