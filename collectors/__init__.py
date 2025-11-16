"""
Package de collecteurs de données externes pour EuroMillions.
"""

from .astronomical_data import AstronomicalDataCollector, get_astronomical_data
from .weather_data import WeatherDataCollector, get_weather_data
from .geophysical_data import GeophysicalDataCollector, get_geophysical_data

__all__ = [
    'AstronomicalDataCollector',
    'get_astronomical_data',
    'WeatherDataCollector',
    'get_weather_data',
    'GeophysicalDataCollector',
    'get_geophysical_data',
]
