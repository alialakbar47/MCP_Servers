"""
Routing & Directions Server
This server provides routing, distance calculation, and navigation functionality.
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from math import radians, sin, cos, sqrt, atan2, degrees, atan


class RoutingServer:
    """
    MCP-style server for routing and navigation operations.
    
    Implements the following operations:
    - calculate_route: Get directions between two points
    - distance_matrix: Calculate distances between multiple locations
    - find_nearby: Find locations within a radius
    """
    
    def __init__(self):
        self.earth_radius_km = 6371
        
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula.
        
        Returns:
            Distance in kilometers
        """
        R = self.earth_radius_km
        
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return R * c
    
    def _calculate_bearing(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the initial bearing from point 1 to point 2.
        
        Returns:
            Bearing in degrees (0-360)
        """
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lon = radians(lon2 - lon1)
        
        x = sin(delta_lon) * cos(lat2_rad)
        y = cos(lat1_rad) * sin(lat2_rad) - sin(lat1_rad) * cos(lat2_rad) * cos(delta_lon)
        
        bearing = atan2(x, y)
        bearing_degrees = (degrees(bearing) + 360) % 360
        
        return bearing_degrees
    
    def _bearing_to_direction(self, bearing: float) -> str:
        """Convert bearing to cardinal direction."""
        directions = ['North', 'Northeast', 'East', 'Southeast', 'South', 'Southwest', 'West', 'Northwest']
        index = round(bearing / 45) % 8
        return directions[index]
    
    async def calculate_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        mode: str = "driving"
    ) -> Dict[str, Any]:
        """
        Calculate a route between two points.
        
        Args:
            start_lat: Starting latitude
            start_lon: Starting longitude
            end_lat: Destination latitude
            end_lon: Destination longitude
            mode: Transportation mode (driving, walking, cycling)
            
        Returns:
            Route information including distance, estimated time, and directions
        """
        # Calculate direct distance
        distance_km = self._calculate_distance(start_lat, start_lon, end_lat, end_lon)
        
        # Calculate bearing
        bearing = self._calculate_bearing(start_lat, start_lon, end_lat, end_lon)
        direction = self._bearing_to_direction(bearing)
        
        # Estimate route distance (account for roads, typically 1.2-1.4x direct distance)
        route_factor = {
            'driving': 1.3,
            'walking': 1.2,
            'cycling': 1.25
        }
        estimated_distance = distance_km * route_factor.get(mode, 1.3)
        
        # Estimate travel time based on mode
        avg_speeds = {
            'driving': 60,  # km/h
            'walking': 5,   # km/h
            'cycling': 20   # km/h
        }
        speed = avg_speeds.get(mode, 60)
        estimated_time_hours = estimated_distance / speed
        estimated_time_minutes = estimated_time_hours * 60
        
        # Generate simple step-by-step directions
        steps = [
            {
                'instruction': f'Head {direction}',
                'distance_km': estimated_distance * 0.1,
                'distance_text': f'{estimated_distance * 0.1:.1f} km'
            },
            {
                'instruction': f'Continue {direction}',
                'distance_km': estimated_distance * 0.8,
                'distance_text': f'{estimated_distance * 0.8:.1f} km'
            },
            {
                'instruction': 'Arrive at destination',
                'distance_km': estimated_distance * 0.1,
                'distance_text': f'{estimated_distance * 0.1:.1f} km'
            }
        ]
        
        return {
            'distance_km': round(estimated_distance, 2),
            'distance_text': f'{estimated_distance:.1f} km',
            'duration_minutes': round(estimated_time_minutes, 1),
            'duration_text': f'{int(estimated_time_minutes // 60)}h {int(estimated_time_minutes % 60)}m' if estimated_time_minutes >= 60 else f'{int(estimated_time_minutes)} min',
            'mode': mode,
            'steps': steps,
            'start_coordinates': {'latitude': start_lat, 'longitude': start_lon},
            'end_coordinates': {'latitude': end_lat, 'longitude': end_lon},
            'bearing': round(bearing, 1),
            'direction': direction
        }
    
    async def distance_matrix(
        self,
        origins: List[Tuple[float, float]],
        destinations: List[Tuple[float, float]]
    ) -> Dict[str, Any]:
        """
        Calculate distances between multiple origin and destination points.
        
        Args:
            origins: List of (latitude, longitude) tuples for origins
            destinations: List of (latitude, longitude) tuples for destinations
            
        Returns:
            Matrix of distances and travel times
        """
        matrix = []
        
        for i, (origin_lat, origin_lon) in enumerate(origins):
            row = []
            for j, (dest_lat, dest_lon) in enumerate(destinations):
                distance = self._calculate_distance(origin_lat, origin_lon, dest_lat, dest_lon)
                
                # Estimate driving time (assuming 60 km/h average speed with 1.3x road factor)
                route_distance = distance * 1.3
                time_minutes = (route_distance / 60) * 60
                
                row.append({
                    'distance_km': round(distance, 2),
                    'route_distance_km': round(route_distance, 2),
                    'duration_minutes': round(time_minutes, 1),
                    'origin_index': i,
                    'destination_index': j
                })
            matrix.append(row)
        
        return {
            'origins': [{'latitude': lat, 'longitude': lon} for lat, lon in origins],
            'destinations': [{'latitude': lat, 'longitude': lon} for lat, lon in destinations],
            'matrix': matrix
        }
    
    async def find_nearby(
        self,
        center_lat: float,
        center_lon: float,
        locations: List[Dict[str, Any]],
        radius_km: float = 5.0
    ) -> List[Dict[str, Any]]:
        """
        Find locations within a specified radius of a center point.
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            locations: List of locations with 'latitude' and 'longitude' keys
            radius_km: Search radius in kilometers
            
        Returns:
            List of nearby locations with distances, sorted by proximity
        """
        nearby = []
        
        for location in locations:
            lat = location.get('latitude')
            lon = location.get('longitude')
            
            if lat is None or lon is None:
                continue
            
            distance = self._calculate_distance(center_lat, center_lon, lat, lon)
            
            if distance <= radius_km:
                bearing = self._calculate_bearing(center_lat, center_lon, lat, lon)
                direction = self._bearing_to_direction(bearing)
                
                result = {
                    **location,
                    'distance_km': round(distance, 2),
                    'bearing': round(bearing, 1),
                    'direction': direction
                }
                nearby.append(result)
        
        # Sort by distance
        nearby.sort(key=lambda x: x['distance_km'])
        
        return nearby
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Return OpenAI function definitions for this server's operations.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "calculate_route",
                    "description": "Calculate a route between two geographic points with turn-by-turn directions",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_lat": {
                                "type": "number",
                                "description": "Starting point latitude"
                            },
                            "start_lon": {
                                "type": "number",
                                "description": "Starting point longitude"
                            },
                            "end_lat": {
                                "type": "number",
                                "description": "Destination latitude"
                            },
                            "end_lon": {
                                "type": "number",
                                "description": "Destination longitude"
                            },
                            "mode": {
                                "type": "string",
                                "enum": ["driving", "walking", "cycling"],
                                "description": "Transportation mode",
                                "default": "driving"
                            }
                        },
                        "required": ["start_lat", "start_lon", "end_lat", "end_lon"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "distance_matrix",
                    "description": "Calculate distances and travel times between multiple origin and destination points",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "origins": {
                                "type": "array",
                                "description": "List of origin coordinates as [latitude, longitude] pairs",
                                "items": {
                                    "type": "array",
                                    "items": {"type": "number"},
                                    "minItems": 2,
                                    "maxItems": 2
                                }
                            },
                            "destinations": {
                                "type": "array",
                                "description": "List of destination coordinates as [latitude, longitude] pairs",
                                "items": {
                                    "type": "array",
                                    "items": {"type": "number"},
                                    "minItems": 2,
                                    "maxItems": 2
                                }
                            }
                        },
                        "required": ["origins", "destinations"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "find_nearby",
                    "description": "Find locations within a specified radius of a center point",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "center_lat": {
                                "type": "number",
                                "description": "Center point latitude"
                            },
                            "center_lon": {
                                "type": "number",
                                "description": "Center point longitude"
                            },
                            "locations": {
                                "type": "array",
                                "description": "List of locations to check (each must have 'latitude' and 'longitude')",
                                "items": {
                                    "type": "object"
                                }
                            },
                            "radius_km": {
                                "type": "number",
                                "description": "Search radius in kilometers",
                                "default": 5.0
                            }
                        },
                        "required": ["center_lat", "center_lon", "locations"]
                    }
                }
            }
        ]


# Example usage
async def main():
    server = RoutingServer()
    
    # Test route calculation
    print("Testing route calculation...")
    route = await server.calculate_route(
        40.7128, -74.0060,  # New York
        42.3601, -71.0589,  # Boston
        mode="driving"
    )
    print(f"Route from New York to Boston:")
    print(f"Distance: {route['distance_text']}")
    print(f"Duration: {route['duration_text']}")
    print(f"Direction: {route['direction']}")
    
    # Test distance matrix
    print("\nTesting distance matrix...")
    matrix = await server.distance_matrix(
        [(40.7128, -74.0060), (41.8781, -87.6298)],  # NYC, Chicago
        [(42.3601, -71.0589), (34.0522, -118.2437)]  # Boston, LA
    )
    print(f"Distance from NYC to Boston: {matrix['matrix'][0][0]['distance_km']} km")
    
    # Test find nearby
    print("\nTesting find nearby...")
    test_locations = [
        {'name': 'Location A', 'latitude': 40.7589, 'longitude': -73.9851},
        {'name': 'Location B', 'latitude': 40.7128, 'longitude': -74.0060},
        {'name': 'Location C', 'latitude': 41.8781, 'longitude': -87.6298}
    ]
    nearby = await server.find_nearby(40.7580, -73.9855, test_locations, radius_km=10)
    print(f"Found {len(nearby)} locations within 10km")


if __name__ == "__main__":
    asyncio.run(main())
