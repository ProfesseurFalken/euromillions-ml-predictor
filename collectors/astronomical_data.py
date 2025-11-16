"""
Collecteur de données astronomiques pour corrélation avec les tirages EuroMillions.
Utilise des APIs publiques pour récupérer phases lunaires, positions planétaires, etc.
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json
from pathlib import Path
from loguru import logger
import time


class AstronomicalDataCollector:
    """
    Collecte des données astronomiques pour une date donnée.
    
    Sources de données :
    - API Astronomy (gratuite) : phases lunaires, lever/coucher soleil/lune
    - API Open-Meteo (gratuite) : données solaires
    - Calculs internes : positions planétaires, cycles
    """
    
    def __init__(self, cache_dir: str = "./data/astronomical"):
        """
        Initialise le collecteur avec un système de cache.
        
        Args:
            cache_dir: Répertoire pour mettre en cache les données
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Coordonnées de Paris (lieu du tirage)
        self.paris_lat = 48.8566
        self.paris_lon = 2.3522
        
        # URLs des APIs
        self.astronomy_api = "https://api.sunrise-sunset.org/json"
        self.moon_api = "https://api.farmsense.net/v1/moonphases/"
        
    def _get_cache_path(self, date: datetime) -> Path:
        """Génère le chemin du fichier cache pour une date."""
        return self.cache_dir / f"astro_{date.strftime('%Y%m%d')}.json"
    
    def _load_from_cache(self, date: datetime) -> Optional[Dict[str, Any]]:
        """Charge les données du cache si disponibles."""
        cache_path = self._get_cache_path(date)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.debug(f"Données astronomiques chargées du cache pour {date.date()}")
                    return data
            except Exception as e:
                logger.warning(f"Erreur lecture cache: {e}")
        return None
    
    def _save_to_cache(self, date: datetime, data: Dict[str, Any]) -> None:
        """Sauvegarde les données dans le cache."""
        cache_path = self._get_cache_path(date)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Données astronomiques sauvegardées en cache pour {date.date()}")
        except Exception as e:
            logger.warning(f"Erreur écriture cache: {e}")
    
    def get_moon_phase(self, date: datetime) -> Dict[str, Any]:
        """
        Récupère la phase lunaire pour une date donnée.
        
        Returns:
            Dict contenant:
            - phase_name: Nouvelle lune, Premier quartier, Pleine lune, Dernier quartier
            - phase_percentage: 0-100 (0=nouvelle, 50=premier quartier, 100=pleine)
            - illumination: Pourcentage d'illumination
            - age_days: Age de la lune en jours (0-29.5)
        """
        try:
            # API gratuite pour phase lunaire
            response = requests.get(
                f"{self.moon_api}",
                params={
                    "d": date.strftime("%Y-%m-%d")
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    moon_data = data[0]
                    
                    # Calculer le pourcentage de phase (0-100)
                    # 0 = nouvelle lune, 50 = pleine lune, 100 = nouvelle lune suivante
                    phase_pct = (moon_data.get('Phase', 0) * 100) % 100
                    
                    return {
                        'phase_percentage': round(phase_pct, 2),
                        'illumination': moon_data.get('Illumination', 0) * 100,
                        'age_days': moon_data.get('Age', 0),
                        'phase_name': self._get_moon_phase_name(phase_pct),
                        'distance_km': moon_data.get('Distance', 384400)  # Distance Terre-Lune
                    }
        except Exception as e:
            logger.warning(f"Erreur récupération phase lunaire: {e}")
        
        # Calcul de secours basique (algorithme simplifié)
        return self._calculate_moon_phase_fallback(date)
    
    def _calculate_moon_phase_fallback(self, date: datetime) -> Dict[str, Any]:
        """Calcul de secours de la phase lunaire (algorithme simplifié)."""
        # Constantes pour le calcul lunaire
        # Nouvelle lune de référence: 6 janvier 2000, 18:14 UTC
        reference_new_moon = datetime(2000, 1, 6, 18, 14)
        synodic_month = 29.530588853  # Durée moyenne d'un cycle lunaire en jours
        
        # Calculer le nombre de jours depuis la nouvelle lune de référence
        days_since_ref = (date - reference_new_moon).total_seconds() / 86400
        
        # Calculer l'age de la lune dans le cycle actuel
        moon_age = days_since_ref % synodic_month
        
        # Calculer le pourcentage de phase (0-100)
        phase_percentage = (moon_age / synodic_month) * 100
        
        # Calculer l'illumination (approximation sinusoïdale)
        import math
        illumination = (1 - math.cos(2 * math.pi * moon_age / synodic_month)) * 50
        
        return {
            'phase_percentage': round(phase_percentage, 2),
            'illumination': round(illumination, 2),
            'age_days': round(moon_age, 2),
            'phase_name': self._get_moon_phase_name(phase_percentage),
            'distance_km': 384400,  # Distance moyenne
            'calculated': True  # Indique que c'est un calcul de secours
        }
    
    def _get_moon_phase_name(self, phase_pct: float) -> str:
        """Détermine le nom de la phase lunaire basé sur le pourcentage."""
        if phase_pct < 6.25 or phase_pct >= 93.75:
            return "Nouvelle Lune"
        elif phase_pct < 18.75:
            return "Premier Croissant"
        elif phase_pct < 31.25:
            return "Premier Quartier"
        elif phase_pct < 43.75:
            return "Gibbeuse Croissante"
        elif phase_pct < 56.25:
            return "Pleine Lune"
        elif phase_pct < 68.75:
            return "Gibbeuse Décroissante"
        elif phase_pct < 81.25:
            return "Dernier Quartier"
        else:
            return "Dernier Croissant"
    
    def get_sun_data(self, date: datetime) -> Dict[str, Any]:
        """
        Récupère les données solaires pour une date donnée.
        
        Returns:
            Dict contenant lever/coucher du soleil, durée du jour, etc.
        """
        try:
            response = requests.get(
                self.astronomy_api,
                params={
                    'lat': self.paris_lat,
                    'lng': self.paris_lon,
                    'date': date.strftime('%Y-%m-%d'),
                    'formatted': 0
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'OK':
                    results = data['results']
                    
                    sunrise = datetime.fromisoformat(results['sunrise'].replace('Z', '+00:00'))
                    sunset = datetime.fromisoformat(results['sunset'].replace('Z', '+00:00'))
                    
                    # Calculer la durée du jour
                    day_length_seconds = (sunset - sunrise).total_seconds()
                    
                    return {
                        'sunrise': sunrise.strftime('%H:%M:%S'),
                        'sunset': sunset.strftime('%H:%M:%S'),
                        'day_length_hours': round(day_length_seconds / 3600, 2),
                        'solar_noon': results.get('solar_noon', ''),
                        'civil_twilight_begin': results.get('civil_twilight_begin', ''),
                        'civil_twilight_end': results.get('civil_twilight_end', '')
                    }
        except Exception as e:
            logger.warning(f"Erreur récupération données solaires: {e}")
        
        return {}
    
    def get_solar_activity(self, date: datetime) -> Dict[str, Any]:
        """
        Récupère l'activité solaire (taches solaires, éruptions, etc.).
        
        Note: Nécessite API NOAA ou similaire. Implémentation simplifiée.
        """
        # TODO: Intégrer API NOAA Space Weather Prediction Center
        # https://services.swpc.noaa.gov/json/
        
        try:
            # API NOAA pour indice géomagnétique Kp
            response = requests.get(
                "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # Filtrer pour la date demandée (si disponible)
                # Pour l'instant, retourner les dernières données disponibles
                
                return {
                    'kp_index': 'N/A',  # Indice Kp (0-9, mesure de l'activité géomagnétique)
                    'solar_flux': 'N/A',  # Flux solaire à 10.7 cm
                    'sunspot_number': 'N/A',  # Nombre de taches solaires
                    'solar_wind_speed': 'N/A',  # Vitesse du vent solaire (km/s)
                    'note': 'Données temps réel uniquement pour dates récentes'
                }
        except Exception as e:
            logger.warning(f"Erreur récupération activité solaire: {e}")
        
        return {}
    
    def get_planetary_positions(self, date: datetime) -> Dict[str, Any]:
        """
        Calcule les positions approximatives des planètes.
        
        Note: Pour une précision maximale, utiliser une bibliothèque comme ephem ou skyfield.
        """
        # TODO: Intégrer skyfield ou ephem pour calculs précis
        # Pour l'instant, retourner une structure de base
        
        return {
            'mercury_longitude': 0.0,  # Longitude écliptique en degrés
            'venus_longitude': 0.0,
            'mars_longitude': 0.0,
            'jupiter_longitude': 0.0,
            'saturn_longitude': 0.0,
            'note': 'Calculs planétaires à implémenter avec skyfield'
        }
    
    def collect_all_data(self, date: datetime) -> Dict[str, Any]:
        """
        Collecte toutes les données astronomiques pour une date donnée.
        
        Args:
            date: Date du tirage (typiquement mardi ou vendredi à 21h05 CET)
            
        Returns:
            Dict avec toutes les données astronomiques
        """
        # Vérifier le cache d'abord
        cached = self._load_from_cache(date)
        if cached:
            return cached
        
        logger.info(f"Collecte des données astronomiques pour {date.strftime('%Y-%m-%d %H:%M')}")
        
        # Collecter toutes les données
        data = {
            'date': date.isoformat(),
            'location': 'Paris, France',
            'latitude': self.paris_lat,
            'longitude': self.paris_lon,
            'collected_at': datetime.now().isoformat()
        }
        
        # Phase lunaire
        try:
            data['moon'] = self.get_moon_phase(date)
            time.sleep(0.5)  # Pause pour ne pas surcharger l'API
        except Exception as e:
            logger.error(f"Erreur collecte phase lunaire: {e}")
            data['moon'] = {}
        
        # Données solaires
        try:
            data['sun'] = self.get_sun_data(date)
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"Erreur collecte données solaires: {e}")
            data['sun'] = {}
        
        # Activité solaire
        try:
            data['solar_activity'] = self.get_solar_activity(date)
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"Erreur collecte activité solaire: {e}")
            data['solar_activity'] = {}
        
        # Positions planétaires
        try:
            data['planets'] = self.get_planetary_positions(date)
        except Exception as e:
            logger.error(f"Erreur calcul positions planétaires: {e}")
            data['planets'] = {}
        
        # Sauvegarder en cache
        self._save_to_cache(date, data)
        
        logger.info(f"✓ Données astronomiques collectées avec succès")
        
        return data


# Fonction helper pour utilisation facile
def get_astronomical_data(date: datetime) -> Dict[str, Any]:
    """
    Fonction utilitaire pour récupérer les données astronomiques d'une date.
    
    Args:
        date: Date du tirage
        
    Returns:
        Dict avec toutes les données astronomiques
    """
    collector = AstronomicalDataCollector()
    return collector.collect_all_data(date)


if __name__ == "__main__":
    # Test du collecteur
    from datetime import datetime
    
    # Test avec la date d'un tirage (vendredi 21h05)
    test_date = datetime(2024, 10, 11, 21, 5)
    
    collector = AstronomicalDataCollector()
    data = collector.collect_all_data(test_date)
    
    print("\n=== DONNÉES ASTRONOMIQUES ===")
    print(json.dumps(data, indent=2, ensure_ascii=False))
