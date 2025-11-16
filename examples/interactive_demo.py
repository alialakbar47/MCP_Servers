"""
Interactive Demo Script
Allows manual testing of individual servers without OpenAI integration.
"""

import asyncio
from servers.geocoding_server import GeocodingServer
from servers.routing_server import RoutingServer
from servers.weather_server import WeatherServer


async def test_geocoding_server():
    """Test the geocoding server."""
    print("\n" + "="*80)
    print("TESTING GEOCODING SERVER")
    print("="*80)
    
    server = GeocodingServer()
    
    # Test 1: Geocode a famous location
    print("\n1. Geocoding 'Statue of Liberty'...")
    results = await server.geocode("Statue of Liberty", limit=1)
    if results and 'error' not in results[0]:
        print(f"   ✓ Found: {results[0]['display_name']}")
        print(f"   ✓ Coordinates: ({results[0]['latitude']}, {results[0]['longitude']})")
    else:
        print(f"   ✗ Error: {results}")
    
    await asyncio.sleep(1.5)  # Rate limiting
    
    # Test 2: Reverse geocode
    print("\n2. Reverse geocoding coordinates (40.7589, -73.9851)...")
    result = await server.reverse_geocode(40.7589, -73.9851)
    if 'error' not in result:
        print(f"   ✓ Address: {result.get('display_name')}")
    else:
        print(f"   ✗ Error: {result}")
    
    await asyncio.sleep(1.5)  # Rate limiting
    
    # Test 3: Search for places
    print("\n3. Searching for 'coffee shop' near Central Park...")
    places = await server.search_places("coffee", near_lat=40.7829, near_lon=-73.9654, limit=3)
    if places and 'error' not in places[0]:
        print(f"   ✓ Found {len(places)} results:")
        for i, place in enumerate(places[:3], 1):
            dist = place.get('distance_km', 'N/A')
            print(f"      {i}. {place.get('name', 'Unknown')} ({dist} km away)")
    else:
        print(f"   ✗ Error: {places}")


async def test_routing_server():
    """Test the routing server."""
    print("\n" + "="*80)
    print("TESTING ROUTING SERVER")
    print("="*80)
    
    server = RoutingServer()
    
    # Test 1: Calculate route
    print("\n1. Calculating route from NYC to Boston (driving)...")
    route = await server.calculate_route(
        40.7128, -74.0060,  # NYC
        42.3601, -71.0589,  # Boston
        mode="driving"
    )
    print(f"   ✓ Distance: {route['distance_text']}")
    print(f"   ✓ Duration: {route['duration_text']}")
    print(f"   ✓ Direction: {route['direction']}")
    
    # Test 2: Distance matrix
    print("\n2. Calculating distance matrix...")
    matrix = await server.distance_matrix(
        [(40.7128, -74.0060)],  # NYC
        [(42.3601, -71.0589), (34.0522, -118.2437)]  # Boston, LA
    )
    print(f"   ✓ NYC to Boston: {matrix['matrix'][0][0]['distance_km']} km")
    print(f"   ✓ NYC to LA: {matrix['matrix'][0][1]['distance_km']} km")
    
    # Test 3: Find nearby
    print("\n3. Finding locations within 10km of Times Square...")
    test_locations = [
        {'name': 'Empire State Building', 'latitude': 40.7484, 'longitude': -73.9857},
        {'name': 'Statue of Liberty', 'latitude': 40.6892, 'longitude': -74.0445},
        {'name': 'Boston', 'latitude': 42.3601, 'longitude': -71.0589}
    ]
    nearby = await server.find_nearby(40.7580, -73.9855, test_locations, radius_km=10)
    print(f"   ✓ Found {len(nearby)} nearby locations:")
    for loc in nearby:
        print(f"      - {loc['name']}: {loc['distance_km']} km {loc['direction']}")


async def test_weather_server():
    """Test the weather server."""
    print("\n" + "="*80)
    print("TESTING WEATHER SERVER")
    print("="*80)
    
    server = WeatherServer()
    
    # Test 1: Current weather
    print("\n1. Getting current weather for Paris...")
    weather = await server.get_weather(48.8566, 2.3522, "Paris")
    if 'error' not in weather:
        print(f"   ✓ Temperature: {weather.get('temperature_f')}°F")
        print(f"   ✓ Conditions: {weather.get('weather_description')}")
        print(f"   ✓ Wind: {weather.get('windspeed_mph')} mph")
    else:
        print(f"   ✗ Error: {weather}")
    
    # Test 2: Weather forecast
    print("\n2. Getting 3-day forecast for Tokyo...")
    forecast = await server.weather_forecast(35.6762, 139.6503, days=3, location_name="Tokyo")
    if 'error' not in forecast:
        print(f"   ✓ 3-day forecast:")
        for day in forecast['forecast']:
            print(f"      {day['date']}: {day['temperature_min_f']}-{day['temperature_max_f']}°F - {day['weather_description']}")
    else:
        print(f"   ✗ Error: {forecast}")
    
    # Test 3: Combined location and weather
    print("\n3. Getting comprehensive weather info for London...")
    info = await server.location_weather_info(51.5074, -0.1278, "London", include_forecast=True)
    if 'error' not in info.get('current_weather', {}):
        print(f"   ✓ Current temp: {info['current_weather'].get('temperature_f')}°F")
        print(f"   ✓ Forecast days: {len(info.get('forecast', []))}")
    else:
        print(f"   ✗ Error: {info}")


async def run_all_tests():
    """Run all server tests."""
    try:
        await test_geocoding_server()
        await test_routing_server()
        await test_weather_server()
        
        print("\n" + "="*80)
        print("ALL TESTS COMPLETE")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()


async def interactive_menu():
    """Interactive menu for testing individual servers."""
    while True:
        print("\n" + "="*80)
        print("INTERACTIVE SERVER DEMO")
        print("="*80)
        print("\n1. Test Geocoding Server")
        print("2. Test Routing Server")
        print("3. Test Weather Server")
        print("4. Run all tests")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            await test_geocoding_server()
        elif choice == "2":
            await test_routing_server()
        elif choice == "3":
            await test_weather_server()
        elif choice == "4":
            await run_all_tests()
        elif choice == "5":
            print("\nGoodbye! 👋\n")
            break
        else:
            print("\nInvalid choice. Please try again.")


def main():
    """Main entry point."""
    print("\n🚀 Map Servers Interactive Demo")
    print("This script tests each server independently (no OpenAI API required)\n")
    
    asyncio.run(interactive_menu())


if __name__ == "__main__":
    main()
