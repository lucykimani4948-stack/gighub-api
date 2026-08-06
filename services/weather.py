import httpx
import os
from datetime import datetime
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_URL = os.getenv("WEATHER_API_URL", "https://api.open-meteo.com/v1/forecast")
GEOCODING_API_URL = os.getenv("GEOCODING_API_URL", "https://geocoding-api.open-meteo.com/v1/search")

async def get_coordinates(city: str, country: str = "Kenya") -> Optional[tuple]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                GEOCODING_API_URL,
                params={
                    "name": city,
                    "count": 1,
                    "language": "en",
                    "format": "json"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("results"):
                result = data["results"][0]
                return (result["latitude"], result["longitude"])
                
        except httpx.TimeoutException:
            print(f"Geocoding timeout for {city}")
        except Exception as e:
            print(f"Geocoding error: {e}")
            
    return None

async def get_weather(city: str, country: str = "Kenya") -> Optional[Dict]:
    coordinates = await get_coordinates(city, country)
    if not coordinates:
        return {"error": "Could not find city coordinates"}
    
    lat, lon = coordinates
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                WEATHER_API_URL,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current_weather": True,
                    "temperature_unit": "celsius",
                    "timezone": "Africa/Nairobi"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            current = data.get("current_weather", {})
            
            weather_codes = {
                0: "Clear sky",
                1: "Mainly clear",
                2: "Partly cloudy",
                3: "Overcast",
                45: "Fog",
                48: "Depositing rime fog",
                51: "Light drizzle",
                53: "Moderate drizzle",
                55: "Dense drizzle",
                61: "Slight rain",
                63: "Moderate rain",
                65: "Heavy rain",
                71: "Slight snow fall",
                73: "Moderate snow fall",
                75: "Heavy snow fall",
                80: "Slight rain showers",
                81: "Moderate rain showers",
                82: "Violent rain showers",
                95: "Thunderstorm",
                96: "Thunderstorm with slight hail",
                99: "Thunderstorm with heavy hail"
            }
            
            weather_code = current.get("weathercode")
            weather_description = weather_codes.get(weather_code, "Unknown weather condition")
            
            return {
                "city": city,
                "country": country,
                "temperature": current.get("temperature"),
                "windspeed": current.get("windspeed"),
                "weathercode": weather_code,
                "weather_description": weather_description,
                "time": current.get("time"),
                "source": "Open-Meteo",
                "coordinates": {"latitude": lat, "longitude": lon}
            }
            
        except httpx.TimeoutException:
            print(f"Weather API timeout for {city}")
            return {"error": "Weather API timeout"}
        except Exception as e:
            print(f"Weather API error: {e}")
            return {"error": str(e)}