"""
Collecteur de données météorologiques pour Paris au moment des tirages (21h05 CET).
Utilise des APIs gratuites pour récupérer température, pression, humidité, etc.
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json
from pathlib import Path
from loguru import logger
import time


class WeatherDataCollector:
    """
    Collecte des données météorologiques pour Paris à l'heure du tirage.
    
    Sources:
    - Open-Meteo (gratuite, pas de clé API requise)
    - WeatherAPI (gratuite avec limite)
    """
    
    def __init__(self, cache_dir: str = "./data/weather"):
        """
        Initialise le collecteur avec cache.
        
        Args:
            cache_dir: Répertoire pour mettre en cache les données
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Coordonnées de Paris (FDJ - approximatif)
        self.paris_lat = 48.8566
        self.paris_lon = 2.3522
        
        # APIs météo gratuites
        self.open_meteo_archive = "https://archive-api.open-meteo.com/v1/archive"
        self.open_meteo_forecast = "https://api.open-meteo.com/v1/forecast"
        
    def _get_cache_path(self, date: datetime) -> Path:
        """Génère le chemin du fichier cache pour une date."""
        return self.cache_dir / f"weather_{date.strftime('%Y%m%d_%H%M')}.json"
    
    def _load_from_cache(self, date: datetime) -> Optional[Dict[str, Any]]:
        """Charge les données du cache si disponibles."""
        cache_path = self._get_cache_path(date)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.debug(f"Données météo chargées du cache pour {date}")
                    return data
            except Exception as e:
                logger.warning(f"Erreur lecture cache météo: {e}")
        return None
    
    def _save_to_cache(self, date: datetime, data: Dict[str, Any]) -> None:
        """Sauvegarde les données dans le cache."""
        cache_path = self._get_cache_path(date)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Données météo sauvegardées en cache pour {date}")
        except Exception as e:
            logger.warning(f"Erreur écriture cache météo: {e}")
    
    def get_historical_weather(self, date: datetime) -> Dict[str, Any]:
        """
        Récupère les données météo historiques pour une date passée.
        
        Args:
            date: Date et heure du tirage (ex: 2024-10-11 21:05)
            
        Returns:
            Dict avec température, pression, humidité, vent, etc.
        """
        try:
            # Open-Meteo Archive API (gratuite, données historiques depuis 1940)
            params = {
                'latitude': self.paris_lat,
                'longitude': self.paris_lon,
                'start_date': date.strftime('%Y-%m-%d'),
                'end_date': date.strftime('%Y-%m-%d'),
                'hourly': [
                    'temperature_2m',           # Température à 2m (°C)
                    'relative_humidity_2m',     # Humidité relative (%)
                    'dew_point_2m',             # Point de rosée (°C)
                    'apparent_temperature',     # Température ressentie (°C)
                    'pressure_msl',             # Pression au niveau de la mer (hPa)
                    'surface_pressure',         # Pression de surface (hPa)
                    'cloud_cover',              # Couverture nuageuse (%)
                    'wind_speed_10m',           # Vitesse du vent à 10m (km/h)
                    'wind_direction_10m',       # Direction du vent (°)
                    'wind_gusts_10m',           # Rafales de vent (km/h)
                ],
                'timezone': 'Europe/Paris'
            }
            
            response = requests.get(
                self.open_meteo_archive,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Trouver l'index horaire le plus proche de 21h05
                hourly = data.get('hourly', {})
                times = hourly.get('time', [])
                
                # Chercher 21:00 (l'heure la plus proche de 21:05)
                target_time = date.replace(minute=0, second=0).strftime('%Y-%m-%dT%H:%M')
                
                idx = None
                for i, t in enumerate(times):
                    if target_time in t:
                        idx = i
                        break
                
                if idx is not None:
                    weather_data = {
                        'timestamp': times[idx],
                        'temperature_celsius': hourly.get('temperature_2m', [])[idx],
                        'humidity_percent': hourly.get('relative_humidity_2m', [])[idx],
                        'pressure_hpa': hourly.get('pressure_msl', [])[idx],
                        'surface_pressure_hpa': hourly.get('surface_pressure', [])[idx],
                        'dew_point_celsius': hourly.get('dew_point_2m', [])[idx],
                        'apparent_temperature_celsius': hourly.get('apparent_temperature', [])[idx],
                        'cloud_cover_percent': hourly.get('cloud_cover', [])[idx],
                        'wind_speed_kmh': hourly.get('wind_speed_10m', [])[idx],
                        'wind_direction_degrees': hourly.get('wind_direction_10m', [])[idx],
                        'wind_gusts_kmh': hourly.get('wind_gusts_10m', [])[idx],
                        'source': 'Open-Meteo Archive API'
                    }
                    
                    # Calculer des métriques dérivées
                    weather_data['pressure_tendency'] = self._calculate_pressure_tendency(
                        hourly.get('pressure_msl', []), idx
                    )
                    weather_data['wind_category'] = self._categorize_wind_speed(
                        weather_data['wind_speed_kmh']
                    )
                    
                    return weather_data
                else:
                    logger.warning(f"Heure 21:00 non trouvée dans les données pour {date.date()}")
            
        except Exception as e:
            logger.error(f"Erreur récupération données météo historiques: {e}")
        
        return {}
    
    def _calculate_pressure_tendency(self, pressure_series: list, current_idx: int) -> str:
        """
        Calcule la tendance de la pression (montante/stable/descendante).
        
        Args:
            pressure_series: Série de pressions horaires
            current_idx: Index de l'heure actuelle
            
        Returns:
            'rising', 'steady', ou 'falling'
        """
        if current_idx < 3 or current_idx >= len(pressure_series):
            return 'unknown'
        
        # Comparer avec 3 heures avant
        current = pressure_series[current_idx]
        three_hours_before = pressure_series[current_idx - 3]
        
        if current is None or three_hours_before is None:
            return 'unknown'
        
        diff = current - three_hours_before
        
        if diff > 1.5:
            return 'rising'
        elif diff < -1.5:
            return 'falling'
        else:
            return 'steady'
    
    def _categorize_wind_speed(self, wind_speed_kmh: Optional[float]) -> str:
        """
        Catégorise la vitesse du vent selon l'échelle de Beaufort.
        
        Returns:
            Catégorie du vent
        """
        if wind_speed_kmh is None:
            return 'unknown'
        
        if wind_speed_kmh < 1:
            return 'calm'
        elif wind_speed_kmh < 6:
            return 'light_air'
        elif wind_speed_kmh < 12:
            return 'light_breeze'
        elif wind_speed_kmh < 20:
            return 'gentle_breeze'
        elif wind_speed_kmh < 29:
            return 'moderate_breeze'
        elif wind_speed_kmh < 39:
            return 'fresh_breeze'
        elif wind_speed_kmh < 50:
            return 'strong_breeze'
        elif wind_speed_kmh < 62:
            return 'near_gale'
        elif wind_speed_kmh < 75:
            return 'gale'
        elif wind_speed_kmh < 89:
            return 'strong_gale'
        elif wind_speed_kmh < 103:
            return 'storm'
        elif wind_speed_kmh < 118:
            return 'violent_storm'
        else:
            return 'hurricane'
    
    def get_atmospheric_electricity(self, date: datetime) -> Dict[str, Any]:
        """
        Estime l'électricité atmosphérique basée sur plusieurs facteurs.
        
        Note: Données réelles d'électricité atmosphérique difficiles à obtenir.
        On peut l'estimer avec humidité + nuages + pression.
        """
        # TODO: Intégrer données de foudre si disponibles
        # Peut-être via Blitzortung.org API
        
        return {
            'lightning_activity': 'N/A',
            'atmospheric_potential': 'N/A',
            'note': 'Données électricité atmosphérique à implémenter'
        }
    
    def collect_all_data(self, date: datetime) -> Dict[str, Any]:
        """
        Collecte toutes les données météorologiques pour une date donnée.
        
        Args:
            date: Date et heure du tirage (ex: 2024-10-11 21:05)
            
        Returns:
            Dict avec toutes les données météorologiques
        """
        # Vérifier le cache
        cached = self._load_from_cache(date)
        if cached:
            return cached
        
        logger.info(f"Collecte des données météo pour {date.strftime('%Y-%m-%d %H:%M')} (Paris)")
        
        data = {
            'date': date.isoformat(),
            'location': 'Paris, France',
            'latitude': self.paris_lat,
            'longitude': self.paris_lon,
            'collected_at': datetime.now().isoformat()
        }
        
        # Données météo historiques
        try:
            weather = self.get_historical_weather(date)
            data['weather'] = weather
            
            if weather:
                logger.info(f"✓ Météo: {weather.get('temperature_celsius')}°C, "
                          f"{weather.get('humidity_percent')}% humidité, "
                          f"{weather.get('pressure_hpa')} hPa")
        except Exception as e:
            logger.error(f"Erreur collecte météo: {e}")
            data['weather'] = {}
        
        # Électricité atmosphérique
        try:
            data['atmospheric'] = self.get_atmospheric_electricity(date)
        except Exception as e:
            logger.error(f"Erreur collecte électricité atmosphérique: {e}")
            data['atmospheric'] = {}
        
        # Sauvegarder en cache
        self._save_to_cache(date, data)
        
        logger.info("✓ Données météorologiques collectées avec succès")
        
        return data


def get_weather_data(date: datetime) -> Dict[str, Any]:
    """
    Fonction utilitaire pour récupérer les données météo d'une date.
    
    Args:
        date: Date et heure du tirage
        
    Returns:
        Dict avec toutes les données météorologiques
    """
    collector = WeatherDataCollector()
    return collector.collect_all_data(date)


if __name__ == "__main__":
    # Test du collecteur
    from datetime import datetime
    
    # Test avec la date d'un tirage (vendredi 21h05)
    test_date = datetime(2024, 10, 11, 21, 5)
    
    collector = WeatherDataCollector()
    data = collector.collect_all_data(test_date)
    
    print("\n=== DONNÉES MÉTÉOROLOGIQUES ===")
    print(json.dumps(data, indent=2, ensure_ascii=False))
