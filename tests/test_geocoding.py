"""
Tests for Geocoding Server
"""

import pytest
import asyncio
from servers.geocoding_server import GeocodingServer


@pytest.fixture
def server():
    """Create a geocoding server instance."""
    return GeocodingServer()


@pytest.mark.asyncio
async def test_geocode_famous_location(server):
    """Test geocoding a famous location."""
    results = await server.geocode("Eiffel Tower, Paris", limit=1)
    
    assert len(results) > 0
    assert 'latitude' in results[0]
    assert 'longitude' in results[0]
    
    # Eiffel Tower is approximately at these coordinates
    assert 48.8 < results[0]['latitude'] < 48.9
    assert 2.2 < results[0]['longitude'] < 2.4


@pytest.mark.asyncio
async def test_geocode_city(server):
    """Test geocoding a city."""
    results = await server.geocode("New York City", limit=5)
    
    assert len(results) > 0
    assert any('New York' in r.get('display_name', '') for r in results)


@pytest.mark.asyncio
async def test_reverse_geocode(server):
    """Test reverse geocoding."""
    # Times Square coordinates
    result = await server.reverse_geocode(40.7580, -73.9855)
    
    assert 'address' in result
    assert 'display_name' in result
    assert 'New York' in result['display_name']


@pytest.mark.asyncio
async def test_search_places(server):
    """Test searching for places."""
    # Search for coffee shops in Seattle area
    places = await server.search_places(
        "coffee shop",
        near_lat=47.6062,
        near_lon=-122.3321,
        limit=5
    )
    
    assert isinstance(places, list)
    # Some results may be found
    if len(places) > 0:
        assert 'latitude' in places[0]
        assert 'longitude' in places[0]


@pytest.mark.asyncio
async def test_search_places_without_location(server):
    """Test searching for places without specific location."""
    places = await server.search_places("museum", limit=3)
    
    assert isinstance(places, list)


@pytest.mark.asyncio
async def test_distance_calculation(server):
    """Test the distance calculation helper."""
    # Distance between NYC and Boston (approximately 300km)
    distance = server._calculate_distance(40.7128, -74.0060, 42.3601, -71.0589)
    
    assert 250 < distance < 350  # Roughly correct


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
        assert 'parameters' in tool['function']


@pytest.mark.asyncio
async def test_rate_limiting(server):
    """Test that rate limiting is working."""
    import time
    
    start_time = time.time()
    
    # Make two requests
    await server.geocode("Paris")
    await server.geocode("London")
    
    elapsed = time.time() - start_time
    
    # Should take at least 1 second due to rate limiting
    assert elapsed >= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
