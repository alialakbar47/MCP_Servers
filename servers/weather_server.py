"""
Weather & Location Server
This server provides weather information combined with location data.
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


class WeatherServer:
    """
    MCP-style server for weather and location-based weather operations.
    
    Implements the following operations:
    - get_weather: Get current weather for a location
    - weather_forecast: Get weather forecast
    - location_weather_info: Combined location and weather data
    """
    
    def __init__(self):
        self.weather_api_base = "https://api.open-meteo.com/v1"
        
    async def get_weather(
        self,
        latitude: float,
        longitude: float,
        location_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get current weather for a specific location.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            location_name: Optional name of the location for display
            
        Returns:
            Current weather information
        """
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'current_weather': 'true',
            'temperature_unit': 'fahrenheit',
            'windspeed_unit': 'mph'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.weather_api_base}/forecast",
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        current = data.get('current_weather', {})
                        
                        # Interpret weather code
                        weather_code = current.get('weathercode', 0)
                        weather_description = self._interpret_weather_code(weather_code)
                        
                        return {
                            'location': location_name or f"{latitude}, {longitude}",
                            'latitude': latitude,
                            'longitude': longitude,
                            'temperature_f': current.get('temperature'),
                            'windspeed_mph': current.get('windspeed'),
                            'wind_direction': current.get('winddirection'),
                            'weather_code': weather_code,
                            'weather_description': weather_description,
                            'time': current.get('time'),
                            'is_day': current.get('is_day') == 1
                        }
                    else:
                        return {'error': f"API returned status {response.status}"}
        except Exception as e:
            return {'error': str(e)}
    
    async def weather_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7,
        location_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get weather forecast for a location.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            days: Number of days to forecast (1-16)
            location_name: Optional name of the location
            
        Returns:
            Weather forecast information
        """
        days = min(max(days, 1), 16)  # Limit to 1-16 days
        
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode',
            'temperature_unit': 'fahrenheit',
            'precipitation_unit': 'inch',
            'forecast_days': days
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.weather_api_base}/forecast",
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        daily = data.get('daily', {})
                        
                        forecast_days = []
                        dates = daily.get('time', [])
                        max_temps = daily.get('temperature_2m_max', [])
                        min_temps = daily.get('temperature_2m_min', [])
                        precipitation = daily.get('precipitation_sum', [])
                        weather_codes = daily.get('weathercode', [])
                        
                        for i in range(len(dates)):
                            forecast_days.append({
                                'date': dates[i],
                                'temperature_max_f': max_temps[i],
                                'temperature_min_f': min_temps[i],
                                'precipitation_in': precipitation[i],
                                'weather_code': weather_codes[i],
                                'weather_description': self._interpret_weather_code(weather_codes[i])
                            })
                        
                        return {
                            'location': location_name or f"{latitude}, {longitude}",
                            'latitude': latitude,
                            'longitude': longitude,
                            'forecast': forecast_days,
                            'days_count': len(forecast_days)
                        }
                    else:
                        return {'error': f"API returned status {response.status}"}
        except Exception as e:
            return {'error': str(e)}
    
    async def location_weather_info(
        self,
        latitude: float,
        longitude: float,
        location_name: str,
        include_forecast: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive location and weather information.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            location_name: Name of the location
            include_forecast: Whether to include forecast data
            
        Returns:
            Combined location and weather information
        """
        # Get current weather
        current_weather = await self.get_weather(latitude, longitude, location_name)
        
        result = {
            'location': {
                'name': location_name,
                'latitude': latitude,
                'longitude': longitude
            },
            'current_weather': current_weather
        }
        
        # Optionally include forecast
        if include_forecast:
            forecast = await self.weather_forecast(latitude, longitude, days=5, location_name=location_name)
            result['forecast'] = forecast.get('forecast', [])
        
        return result
    
    def _interpret_weather_code(self, code: int) -> str:
        """
        Interpret WMO weather code into human-readable description.
        
        Based on WMO Weather interpretation codes (WW)
        """
        code_map = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        
        return code_map.get(code, f"Unknown weather (code {code})")
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Return OpenAI function definitions for this server's operations.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get current weather conditions for a specific location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "latitude": {
                                "type": "number",
                                "description": "Location latitude"
                            },
                            "longitude": {
                                "type": "number",
                                "description": "Location longitude"
                            },
                            "location_name": {
                                "type": "string",
                                "description": "Optional name of the location for display"
                            }
                        },
                        "required": ["latitude", "longitude"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "weather_forecast",
                    "description": "Get weather forecast for a location for the specified number of days",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "latitude": {
                                "type": "number",
                                "description": "Location latitude"
                            },
                            "longitude": {
                                "type": "number",
                                "description": "Location longitude"
                            },
                            "days": {
                                "type": "integer",
                                "description": "Number of days to forecast (1-16)",
                                "default": 7
                            },
                            "location_name": {
                                "type": "string",
                                "description": "Optional name of the location"
                            }
                        },
                        "required": ["latitude", "longitude"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "location_weather_info",
                    "description": "Get comprehensive location and weather information including current conditions and forecast",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "latitude": {
                                "type": "number",
                                "description": "Location latitude"
                            },
                            "longitude": {
                                "type": "number",
                                "description": "Location longitude"
                            },
                            "location_name": {
                                "type": "string",
                                "description": "Name of the location"
                            },
                            "include_forecast": {
                                "type": "boolean",
                                "description": "Whether to include 5-day forecast",
                                "default": True
                            }
                        },
                        "required": ["latitude", "longitude", "location_name"]
                    }
                }
            }
        ]


# Example usage
async def main():
    server = WeatherServer()
    
    # Test current weather
    print("Testing current weather...")
    weather = await server.get_weather(40.7128, -74.0060, "New York City")
    print(f"Weather in {weather['location']}:")
    print(f"Temperature: {weather.get('temperature_f')}°F")
    print(f"Conditions: {weather.get('weather_description')}")
    
    # Test forecast
    print("\nTesting weather forecast...")
    forecast = await server.weather_forecast(37.7749, -122.4194, days=3, location_name="San Francisco")
    print(f"3-day forecast for {forecast['location']}:")
    for day in forecast['forecast'][:3]:
        print(f"  {day['date']}: {day['temperature_min_f']}-{day['temperature_max_f']}°F - {day['weather_description']}")
    
    # Test combined info
    print("\nTesting location weather info...")
    info = await server.location_weather_info(51.5074, -0.1278, "London", include_forecast=True)
    print(f"Location: {info['location']['name']}")
    print(f"Current: {info['current_weather'].get('temperature_f')}°F")


if __name__ == "__main__":
    asyncio.run(main())
