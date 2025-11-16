"""
Geocoding & Places Server
This server provides geocoding, reverse geocoding, and place search functionality
using the OpenStreetMap Nominatim API.
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
import time


class GeocodingServer:
    """
    MCP-style server for geocoding and place search operations.
    
    Implements the following operations:
    - geocode: Convert an address to coordinates
    - reverse_geocode: Convert coordinates to an address
    - search_places: Search for points of interest
    """
    
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org"
        self.user_agent = "MCP-MapServer-Educational/1.0"
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Rate limiting: 1 request per second
        
    async def _rate_limit(self):
        """Ensure we respect the API rate limits."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last_request)
        self.last_request_time = time.time()
    
    async def geocode(self, address: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Convert an address to geographic coordinates.
        
        Args:
            address: The address to geocode
            limit: Maximum number of results to return
            
        Returns:
            List of geocoding results with coordinates and details
        """
        await self._rate_limit()
        
        params = {
            'q': address,
            'format': 'json',
            'limit': limit,
            'addressdetails': 1
        }
        
        headers = {
            'User-Agent': self.user_agent
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/search",
                    params=params,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        for item in data:
                            results.append({
                                'display_name': item.get('display_name'),
                                'latitude': float(item.get('lat')),
                                'longitude': float(item.get('lon')),
                                'type': item.get('type'),
                                'importance': item.get('importance'),
                                'address': item.get('address', {})
                            })
                        return results
                    else:
                        return [{'error': f"API returned status {response.status}"}]
        except Exception as e:
            return [{'error': str(e)}]
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Convert geographic coordinates to an address.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Address and location details
        """
        await self._rate_limit()
        
        params = {
            'lat': latitude,
            'lon': longitude,
            'format': 'json',
            'addressdetails': 1
        }
        
        headers = {
            'User-Agent': self.user_agent
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/reverse",
                    params=params,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'display_name': data.get('display_name'),
                            'address': data.get('address', {}),
                            'type': data.get('type'),
                            'latitude': latitude,
                            'longitude': longitude
                        }
                    else:
                        return {'error': f"API returned status {response.status}"}
        except Exception as e:
            return {'error': str(e)}
    
    async def search_places(
        self,
        query: str,
        near_lat: Optional[float] = None,
        near_lon: Optional[float] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for points of interest (POIs) by category or name.
        
        Args:
            query: Search query (e.g., "coffee shop", "restaurant", "museum")
            near_lat: Optional latitude to search near
            near_lon: Optional longitude to search near
            limit: Maximum number of results
            
        Returns:
            List of matching places with details
        """
        await self._rate_limit()
        
        # If coordinates provided, search near that location
        if near_lat is not None and near_lon is not None:
            # Create a bounding box around the point (approximately 5km radius)
            lat_delta = 0.045  # roughly 5km
            lon_delta = 0.045
            
            params = {
                'q': query,
                'format': 'json',
                'limit': limit,
                'viewbox': f"{near_lon - lon_delta},{near_lat + lat_delta},{near_lon + lon_delta},{near_lat - lat_delta}",
                'bounded': 1,
                'addressdetails': 1
            }
        else:
            params = {
                'q': query,
                'format': 'json',
                'limit': limit,
                'addressdetails': 1
            }
        
        headers = {
            'User-Agent': self.user_agent
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/search",
                    params=params,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        for item in data:
                            result = {
                                'name': item.get('display_name'),
                                'latitude': float(item.get('lat')),
                                'longitude': float(item.get('lon')),
                                'type': item.get('type'),
                                'category': item.get('class'),
                                'address': item.get('address', {})
                            }
                            
                            # Calculate distance if reference point provided
                            if near_lat is not None and near_lon is not None:
                                result['distance_km'] = self._calculate_distance(
                                    near_lat, near_lon,
                                    float(item.get('lat')),
                                    float(item.get('lon'))
                                )
                            
                            results.append(result)
                        
                        # Sort by distance if available
                        if near_lat is not None and near_lon is not None:
                            results.sort(key=lambda x: x.get('distance_km', float('inf')))
                        
                        return results
                    else:
                        return [{'error': f"API returned status {response.status}"}]
        except Exception as e:
            return [{'error': str(e)}]
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula.
        
        Returns:
            Distance in kilometers
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return R * c
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Return OpenAI function definitions for this server's operations.
        This follows the MCP pattern of exposing server capabilities.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "geocode",
                    "description": "Convert an address or place name to geographic coordinates (latitude/longitude)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "address": {
                                "type": "string",
                                "description": "The address or place name to geocode (e.g., 'Eiffel Tower, Paris' or '123 Main St, New York, NY')"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 5
                            }
                        },
                        "required": ["address"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "reverse_geocode",
                    "description": "Convert geographic coordinates to an address",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "latitude": {
                                "type": "number",
                                "description": "Latitude coordinate"
                            },
                            "longitude": {
                                "type": "number",
                                "description": "Longitude coordinate"
                            }
                        },
                        "required": ["latitude", "longitude"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_places",
                    "description": "Search for points of interest (POIs) like restaurants, museums, coffee shops, etc.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "What to search for (e.g., 'coffee shop', 'museum', 'restaurant')"
                            },
                            "near_lat": {
                                "type": "number",
                                "description": "Optional: latitude to search near"
                            },
                            "near_lon": {
                                "type": "number",
                                "description": "Optional: longitude to search near"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]


# Example usage
async def main():
    server = GeocodingServer()
    
    # Test geocoding
    print("Testing geocoding...")
    results = await server.geocode("Eiffel Tower, Paris")
    print(f"Found {len(results)} results for Eiffel Tower")
    if results:
        print(f"Top result: {results[0]['display_name']}")
        print(f"Coordinates: {results[0]['latitude']}, {results[0]['longitude']}")
    
    # Test reverse geocoding
    print("\nTesting reverse geocoding...")
    result = await server.reverse_geocode(48.8584, 2.2945)
    print(f"Address: {result.get('display_name')}")
    
    # Test place search
    print("\nTesting place search...")
    places = await server.search_places("coffee shop", near_lat=40.7589, near_lon=-73.9851)
    print(f"Found {len(places)} coffee shops")


if __name__ == "__main__":
    asyncio.run(main())
