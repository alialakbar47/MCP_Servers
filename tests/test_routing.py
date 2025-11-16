"""
Tests for Routing Server
"""

import pytest
import asyncio
from servers.routing_server import RoutingServer


@pytest.fixture
def server():
    """Create a routing server instance."""
    return RoutingServer()


@pytest.mark.asyncio
async def test_calculate_route_basic(server):
    """Test basic route calculation."""
    # Route from NYC to Boston
    route = await server.calculate_route(
        40.7128, -74.0060,  # New York
        42.3601, -71.0589,  # Boston
        mode="driving"
    )
    
    assert 'distance_km' in route
    assert 'duration_minutes' in route
    assert 'steps' in route
    
    # Distance should be reasonable (roughly 300-350km)
    assert 300 < route['distance_km'] < 500


@pytest.mark.asyncio
async def test_calculate_route_modes(server):
    """Test different transportation modes."""
    start_lat, start_lon = 37.7749, -122.4194  # San Francisco
    end_lat, end_lon = 37.8044, -122.2712      # Oakland
    
    driving = await server.calculate_route(start_lat, start_lon, end_lat, end_lon, mode="driving")
    walking = await server.calculate_route(start_lat, start_lon, end_lat, end_lon, mode="walking")
    cycling = await server.calculate_route(start_lat, start_lon, end_lat, end_lon, mode="cycling")
    
    # Walking should take longer than driving
    assert walking['duration_minutes'] > driving['duration_minutes']
    # Cycling should be between walking and driving
    assert walking['duration_minutes'] > cycling['duration_minutes'] > driving['duration_minutes']


@pytest.mark.asyncio
async def test_distance_matrix(server):
    """Test distance matrix calculation."""
    origins = [(40.7128, -74.0060), (41.8781, -87.6298)]  # NYC, Chicago
    destinations = [(42.3601, -71.0589), (34.0522, -118.2437)]  # Boston, LA
    
    matrix = await server.distance_matrix(origins, destinations)
    
    assert 'origins' in matrix
    assert 'destinations' in matrix
    assert 'matrix' in matrix
    
    # Check matrix dimensions
    assert len(matrix['matrix']) == 2  # 2 origins
    assert len(matrix['matrix'][0]) == 2  # 2 destinations
    
    # Check that all entries have required fields
    for row in matrix['matrix']:
        for entry in row:
            assert 'distance_km' in entry
            assert 'duration_minutes' in entry


@pytest.mark.asyncio
async def test_find_nearby(server):
    """Test finding nearby locations."""
    test_locations = [
        {'name': 'Close', 'latitude': 40.7580, 'longitude': -73.9855},  # Times Square
        {'name': 'Medium', 'latitude': 40.7128, 'longitude': -74.0060},  # Lower Manhattan
        {'name': 'Far', 'latitude': 41.8781, 'longitude': -87.6298}      # Chicago
    ]
    
    # Find locations within 10km of Times Square
    nearby = await server.find_nearby(40.7580, -73.9855, test_locations, radius_km=10)
    
    # Should find Close and Medium, but not Far
    assert len(nearby) == 2
    assert nearby[0]['name'] == 'Close'  # Should be sorted by distance


@pytest.mark.asyncio
async def test_bearing_calculation(server):
    """Test bearing calculation."""
    # North: from equator to north pole
    bearing = server._calculate_bearing(0, 0, 10, 0)
    assert 350 < bearing or bearing < 10  # Approximately 0 degrees (North)
    
    # East: eastward movement
    bearing = server._calculate_bearing(0, 0, 0, 10)
    assert 80 < bearing < 100  # Approximately 90 degrees (East)


@pytest.mark.asyncio
async def test_bearing_to_direction(server):
    """Test bearing to cardinal direction conversion."""
    assert server._bearing_to_direction(0) == 'North'
    assert server._bearing_to_direction(90) == 'East'
    assert server._bearing_to_direction(180) == 'South'
    assert server._bearing_to_direction(270) == 'West'
    assert server._bearing_to_direction(45) == 'Northeast'


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
async def test_route_has_steps(server):
    """Test that route contains navigation steps."""
    route = await server.calculate_route(40.0, -74.0, 41.0, -73.0)
    
    assert 'steps' in route
    assert len(route['steps']) > 0
    
    for step in route['steps']:
        assert 'instruction' in step
        assert 'distance_km' in step


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
