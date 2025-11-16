"""
Tests for Weather Server
"""

import pytest
import asyncio
from servers.weather_server import WeatherServer


@pytest.fixture
def server():
    """Create a weather server instance."""
    return WeatherServer()


@pytest.mark.asyncio
async def test_get_weather(server):
    """Test getting current weather."""
    # Get weather for New York City
    weather = await server.get_weather(40.7128, -74.0060, "New York City")
    
    assert 'location' in weather
    assert weather['location'] == "New York City"
    assert 'temperature_f' in weather
    assert 'weather_description' in weather
    assert 'windspeed_mph' in weather


@pytest.mark.asyncio
async def test_weather_forecast(server):
    """Test weather forecast."""
    # Get 5-day forecast for San Francisco
    forecast = await server.weather_forecast(37.7749, -122.4194, days=5, location_name="San Francisco")
    
    assert 'forecast' in forecast
    assert 'location' in forecast
    assert len(forecast['forecast']) == 5
    
    # Check first day's forecast
    day = forecast['forecast'][0]
    assert 'date' in day
    assert 'temperature_max_f' in day
    assert 'temperature_min_f' in day
    assert 'weather_description' in day


@pytest.mark.asyncio
async def test_location_weather_info(server):
    """Test combined location and weather info."""
    info = await server.location_weather_info(
        51.5074, -0.1278,
        "London",
        include_forecast=True
    )
    
    assert 'location' in info
    assert 'current_weather' in info
    assert 'forecast' in info
    
    assert info['location']['name'] == "London"
    assert len(info['forecast']) > 0


@pytest.mark.asyncio
async def test_location_weather_info_no_forecast(server):
    """Test location weather info without forecast."""
    info = await server.location_weather_info(
        48.8566, 2.3522,
        "Paris",
        include_forecast=False
    )
    
    assert 'location' in info
    assert 'current_weather' in info
    assert 'forecast' not in info


@pytest.mark.asyncio
async def test_weather_code_interpretation(server):
    """Test weather code interpretation."""
    assert server._interpret_weather_code(0) == "Clear sky"
    assert server._interpret_weather_code(61) == "Slight rain"
    assert server._interpret_weather_code(95) == "Thunderstorm"
    assert "Unknown" in server._interpret_weather_code(999)


@pytest.mark.asyncio
async def test_forecast_day_limits(server):
    """Test that forecast respects day limits."""
    # Request 20 days (should be capped at 16)
    forecast = await server.weather_forecast(40.7128, -74.0060, days=20)
    assert len(forecast.get('forecast', [])) <= 16
    
    # Request 0 days (should be at least 1)
    forecast = await server.weather_forecast(40.7128, -74.0060, days=0)
    assert len(forecast.get('forecast', [])) >= 1


@pytest.mark.asyncio
async def test_tool_definitions(server):
    """Test that tool definitions are properly formatted."""
    tools = server.get_tool_definitions()
    
    assert len(tools) == 3
    
    # Check that all tools have required fields
    for tool in tools:
        assert 'type' in tool
        assert tool['type'] == 'function'
        assert 'function' in tool
        assert 'name' in tool['function']
        assert 'description' in tool['function']


@pytest.mark.asyncio
async def test_weather_without_location_name(server):
    """Test weather request without location name."""
    weather = await server.get_weather(35.6762, 139.6503)
    
    assert 'location' in weather
    # Should use coordinates as location name
    assert '35.6762' in weather['location']
    assert '139.6503' in weather['location']


@pytest.mark.asyncio
async def test_temperature_range(server):
    """Test that temperatures are in reasonable range."""
    weather = await server.get_weather(40.7128, -74.0060)
    
    # Temperature should be between -50F and 130F (reasonable Earth range)
    temp = weather.get('temperature_f')
    if temp is not None:
        assert -50 < temp < 130


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
