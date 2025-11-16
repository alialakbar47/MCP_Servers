"""
Main Agent Demo
Demonstrates the integration of all three map servers with OpenAI Agents SDK.
"""

import asyncio
import json
import os
from typing import Any, Dict
from openai import OpenAI

# Import our custom servers
from servers.geocoding_server import GeocodingServer
from servers.routing_server import RoutingServer
from servers.weather_server import WeatherServer


class MapAgentDemo:
    """
    Demonstration of MCP-style map servers integrated with OpenAI.
    """
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
        # Initialize our three map servers
        self.geocoding_server = GeocodingServer()
        self.routing_server = RoutingServer()
        self.weather_server = WeatherServer()
        
        # Collect all tool definitions
        self.tools = []
        self.tools.extend(self.geocoding_server.get_tool_definitions())
        self.tools.extend(self.routing_server.get_tool_definitions())
        self.tools.extend(self.weather_server.get_tool_definitions())
        
        print(f"Initialized agent with {len(self.tools)} tools from 3 servers")
    
    async def execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Route function calls to the appropriate server.
        """
        # Geocoding server functions
        if function_name == "geocode":
            return await self.geocoding_server.geocode(**arguments)
        elif function_name == "reverse_geocode":
            return await self.geocoding_server.reverse_geocode(**arguments)
        elif function_name == "search_places":
            return await self.geocoding_server.search_places(**arguments)
        
        # Routing server functions
        elif function_name == "calculate_route":
            return await self.routing_server.calculate_route(**arguments)
        elif function_name == "distance_matrix":
            # Convert list of lists to list of tuples
            if 'origins' in arguments:
                arguments['origins'] = [tuple(coord) for coord in arguments['origins']]
            if 'destinations' in arguments:
                arguments['destinations'] = [tuple(coord) for coord in arguments['destinations']]
            return await self.routing_server.distance_matrix(**arguments)
        elif function_name == "find_nearby":
            return await self.routing_server.find_nearby(**arguments)
        
        # Weather server functions
        elif function_name == "get_weather":
            return await self.weather_server.get_weather(**arguments)
        elif function_name == "weather_forecast":
            return await self.weather_server.weather_forecast(**arguments)
        elif function_name == "location_weather_info":
            return await self.weather_server.location_weather_info(**arguments)
        
        else:
            return {"error": f"Unknown function: {function_name}"}
    
    async def chat(self, user_message: str, max_iterations: int = 5) -> str:
        """
        Process a user message and handle tool calls.
        """
        messages = [
            {
                "role": "system",
                "content": """You are a helpful assistant with access to map and location services.
You can help users with:
- Finding locations and their coordinates (geocoding)
- Searching for places like restaurants, museums, coffee shops
- Calculating routes and distances between locations
- Getting weather information for any location
- Providing travel directions and navigation assistance

Always provide clear, helpful responses and use the available tools to give accurate information."""
            },
            {"role": "user", "content": user_message}
        ]
        
        for iteration in range(max_iterations):
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            # If no tool calls, we're done
            if not message.tool_calls:
                return message.content
            
            # Add assistant's message to conversation
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            })
            
            # Execute tool calls
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                print(f"\n🔧 Calling {function_name} with {arguments}")
                
                # Execute the function
                result = await self.execute_function(function_name, arguments)
                
                # Add tool response to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })
        
        return "Maximum iterations reached. Please try a simpler query."
    
    async def run_demo_queries(self):
        """
        Run a set of demonstration queries showcasing all servers.
        """
        demo_queries = [
            "What are the coordinates of the Eiffel Tower in Paris?",
            "Find me coffee shops near Times Square in New York",
            "How far is it from San Francisco to Los Angeles by car?",
            "What's the weather like in Tokyo right now?",
            "I want to visit the Grand Canyon. Can you tell me the weather forecast for the next 5 days?",
            "Find museums in London and tell me the weather there"
        ]
        
        print("\n" + "="*80)
        print("MAP AGENT DEMONSTRATION")
        print("="*80)
        
        for i, query in enumerate(demo_queries, 1):
            print(f"\n{'─'*80}")
            print(f"Query {i}: {query}")
            print(f"{'─'*80}")
            
            try:
                response = await self.chat(query)
                print(f"\n✨ Response:\n{response}")
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
            
            # Small delay between queries
            await asyncio.sleep(1)
        
        print(f"\n{'='*80}")
        print("DEMONSTRATION COMPLETE")
        print(f"{'='*80}\n")


async def interactive_mode(agent: MapAgentDemo):
    """
    Interactive mode for testing the agent.
    """
    print("\n" + "="*80)
    print("INTERACTIVE MAP AGENT MODE")
    print("="*80)
    print("\nAvailable capabilities:")
    print("  • Geocoding and location search")
    print("  • Place and POI search")
    print("  • Route calculation and navigation")
    print("  • Weather information and forecasts")
    print("\nType 'quit' or 'exit' to stop.\n")
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! 👋\n")
                break
            
            if not user_input:
                continue
            
            print("\n🤖 Assistant: ", end="", flush=True)
            response = await agent.chat(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


async def main():
    """
    Main entry point for the demo.
    """
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("\nPlease set your OpenAI API key:")
        print("  Windows PowerShell: $env:OPENAI_API_KEY='your-key-here'")
        print("  Or create a .env file with: OPENAI_API_KEY=your-key-here")
        return
    
    # Initialize the agent
    print("\n🚀 Initializing Map Agent with OpenAI...")
    agent = MapAgentDemo(api_key)
    
    # Show menu
    print("\nChoose a mode:")
    print("  1. Run demo queries (automated)")
    print("  2. Interactive mode (manual queries)")
    print("  3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        await agent.run_demo_queries()
    elif choice == "2":
        await interactive_mode(agent)
    elif choice == "3":
        await agent.run_demo_queries()
        await interactive_mode(agent)
    else:
        print("Invalid choice. Running demo queries...")
        await agent.run_demo_queries()


if __name__ == "__main__":
    # Load environment variables from .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    asyncio.run(main())
