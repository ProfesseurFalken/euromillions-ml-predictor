"""
Collecteur de données géophysiques: activité solaire, géomagnétisme, séismes.
Utilise des APIs publiques NOAA, USGS, etc.
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import json
from pathlib import Path
from loguru import logger
import time


class GeophysicalDataCollector:
    """
    Collecte des données géophysiques pouvant influencer l'environnement.
    
    Sources:
    - NOAA Space Weather Prediction Center (activité solaire)
    - USGS Earthquake API (activité sismique)
    - British Geological Survey (indice géomagnétique)
    """
    
    def __init__(self, cache_dir: str = "./data/geophysical"):
        """
        Initialise le collecteur avec cache.
        
        Args:
            cache_dir: Répertoire pour mettre en cache les données
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Coordonnées de Paris pour recherche sismique locale
        self.paris_lat = 48.8566
        self.paris_lon = 2.3522
        
        # URLs des APIs
        self.noaa_kp_url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
        self.noaa_solar_url = "https://services.swpc.noaa.gov/json/f107_cm_flux.json"
        self.usgs_earthquake_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        
    def _get_cache_path(self, date: datetime) -> Path:
        """Génère le chemin du fichier cache pour une date."""
        return self.cache_dir / f"geophys_{date.strftime('%Y%m%d')}.json"
    
    def _load_from_cache(self, date: datetime) -> Optional[Dict[str, Any]]:
        """Charge les données du cache si disponibles."""
        cache_path = self._get_cache_path(date)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.debug(f"Données géophysiques chargées du cache pour {date.date()}")
                    return data
            except Exception as e:
                logger.warning(f"Erreur lecture cache géophysique: {e}")
        return None
    
    def _save_to_cache(self, date: datetime, data: Dict[str, Any]) -> None:
        """Sauvegarde les données dans le cache."""
        cache_path = self._get_cache_path(date)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Données géophysiques sauvegardées en cache pour {date.date()}")
        except Exception as e:
            logger.warning(f"Erreur écriture cache géophysique: {e}")
    
    def get_geomagnetic_index(self, date: datetime) -> Dict[str, Any]:
        """
        Récupère l'indice Kp (indice géomagnétique planétaire).
        
        L'indice Kp mesure l'activité géomagnétique (0-9):
        - 0-4: Calme à actif
        - 5-6: Tempête géomagnétique mineure
        - 7-8: Tempête géomagnétique forte
        - 9: Tempête géomagnétique extrême
        
        Returns:
            Dict avec indice Kp et niveau d'activité
        """
        try:
            response = requests.get(self.noaa_kp_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Les données sont dans un format avec time_tag et Kp
                # Chercher la date la plus proche
                target_date_str = date.strftime('%Y-%m-%d')
                
                matching_entries = []
                for entry in data[1:]:  # Skip header
                    if len(entry) >= 2:
                        entry_time = entry[0]
                        if target_date_str in entry_time:
                            try:
                                kp_value = float(entry[1])
                                matching_entries.append({
                                    'time': entry_time,
                                    'kp': kp_value
                                })
                            except (ValueError, TypeError):
                                continue
                
                if matching_entries:
                    # Calculer la moyenne pour la journée
                    avg_kp = sum(e['kp'] for e in matching_entries) / len(matching_entries)
                    max_kp = max(e['kp'] for e in matching_entries)
                    
                    return {
                        'kp_average': round(avg_kp, 2),
                        'kp_maximum': max_kp,
                        'activity_level': self._categorize_kp(avg_kp),
                        'storm_level': self._categorize_storm(max_kp),
                        'measurements_count': len(matching_entries),
                        'source': 'NOAA SWPC'
                    }
                else:
                    logger.warning(f"Aucune donnée Kp trouvée pour {target_date_str}")
            
        except Exception as e:
            logger.warning(f"Erreur récupération indice Kp: {e}")
        
        # Valeurs par défaut si pas de données
        return {
            'kp_average': None,
            'kp_maximum': None,
            'activity_level': 'unknown',
            'storm_level': 'unknown',
            'note': 'Données non disponibles pour cette date'
        }
    
    def _categorize_kp(self, kp: float) -> str:
        """Catégorise le niveau d'activité géomagnétique."""
        if kp < 2:
            return 'quiet'
        elif kp < 3:
            return 'unsettled'
        elif kp < 4:
            return 'active'
        elif kp < 5:
            return 'minor_storm'
        elif kp < 6:
            return 'moderate_storm'
        elif kp < 7:
            return 'strong_storm'
        elif kp < 8:
            return 'severe_storm'
        else:
            return 'extreme_storm'
    
    def _categorize_storm(self, kp: float) -> str:
        """Catégorise le niveau de tempête géomagnétique (échelle NOAA)."""
        if kp < 5:
            return 'G0_no_storm'
        elif kp < 6:
            return 'G1_minor'
        elif kp < 7:
            return 'G2_moderate'
        elif kp < 8:
            return 'G3_strong'
        elif kp < 9:
            return 'G4_severe'
        else:
            return 'G5_extreme'
    
    def get_solar_flux(self, date: datetime) -> Dict[str, Any]:
        """
        Récupère le flux solaire à 10.7 cm (F10.7).
        
        Le flux F10.7 est un indicateur de l'activité solaire (en SFU):
        - < 80: Minimum solaire
        - 80-120: Activité faible
        - 120-180: Activité modérée
        - > 180: Activité élevée
        
        Returns:
            Dict avec flux solaire et niveau d'activité
        """
        try:
            response = requests.get(self.noaa_solar_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Chercher la date correspondante
                target_date_str = date.strftime('%Y-%m-%d')
                
                for entry in data:
                    if entry.get('time_tag', '').startswith(target_date_str):
                        flux = entry.get('flux', None)
                        if flux:
                            return {
                                'f107_flux': flux,
                                'activity_level': self._categorize_solar_flux(flux),
                                'time': entry.get('time_tag'),
                                'source': 'NOAA SWPC'
                            }
        
        except Exception as e:
            logger.warning(f"Erreur récupération flux solaire: {e}")
        
        return {
            'f107_flux': None,
            'activity_level': 'unknown',
            'note': 'Données non disponibles pour cette date'
        }
    
    def _categorize_solar_flux(self, flux: float) -> str:
        """Catégorise le niveau d'activité solaire basé sur F10.7."""
        if flux < 80:
            return 'solar_minimum'
        elif flux < 120:
            return 'low_activity'
        elif flux < 180:
            return 'moderate_activity'
        elif flux < 250:
            return 'high_activity'
        else:
            return 'very_high_activity'
    
    def get_earthquake_activity(self, date: datetime, radius_km: float = 500) -> Dict[str, Any]:
        """
        Récupère l'activité sismique autour de Paris pour une date donnée.
        
        Args:
            date: Date du tirage
            radius_km: Rayon de recherche autour de Paris (défaut: 500 km)
            
        Returns:
            Dict avec activité sismique
        """
        try:
            # Rechercher séismes dans un rayon autour de Paris
            # pour la journée du tirage (±12 heures)
            start_time = (date - timedelta(hours=12)).strftime('%Y-%m-%dT%H:%M:%S')
            end_time = (date + timedelta(hours=12)).strftime('%Y-%m-%dT%H:%M:%S')
            
            params = {
                'format': 'geojson',
                'starttime': start_time,
                'endtime': end_time,
                'latitude': self.paris_lat,
                'longitude': self.paris_lon,
                'maxradiuskm': radius_km,
                'minmagnitude': 2.0  # Minimum magnitude 2.0
            }
            
            response = requests.get(
                self.usgs_earthquake_url,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                earthquakes = data.get('features', [])
                
                if earthquakes:
                    # Analyser les séismes
                    magnitudes = [eq['properties']['mag'] for eq in earthquakes]
                    max_magnitude = max(magnitudes)
                    avg_magnitude = sum(magnitudes) / len(magnitudes)
                    
                    return {
                        'earthquake_count': len(earthquakes),
                        'max_magnitude': round(max_magnitude, 2),
                        'average_magnitude': round(avg_magnitude, 2),
                        'search_radius_km': radius_km,
                        'activity_level': self._categorize_seismic_activity(len(earthquakes)),
                        'source': 'USGS Earthquake API'
                    }
                else:
                    return {
                        'earthquake_count': 0,
                        'max_magnitude': 0,
                        'average_magnitude': 0,
                        'search_radius_km': radius_km,
                        'activity_level': 'quiet',
                        'source': 'USGS Earthquake API'
                    }
        
        except Exception as e:
            logger.warning(f"Erreur récupération activité sismique: {e}")
        
        return {
            'earthquake_count': None,
            'note': 'Données non disponibles'
        }
    
    def _categorize_seismic_activity(self, count: int) -> str:
        """Catégorise le niveau d'activité sismique."""
        if count == 0:
            return 'quiet'
        elif count <= 2:
            return 'low'
        elif count <= 5:
            return 'moderate'
        elif count <= 10:
            return 'active'
        else:
            return 'very_active'
    
    def get_earth_magnetic_field(self, date: datetime) -> Dict[str, Any]:
        """
        Informations sur le champ magnétique terrestre.
        
        Note: Données détaillées difficiles à obtenir en temps réel.
        On peut estimer avec l'indice Kp.
        """
        return {
            'field_intensity': 'N/A',
            'declination': 'N/A',
            'inclination': 'N/A',
            'note': 'Calculs détaillés du champ magnétique à implémenter'
        }
    
    def collect_all_data(self, date: datetime) -> Dict[str, Any]:
        """
        Collecte toutes les données géophysiques pour une date donnée.
        
        Args:
            date: Date du tirage
            
        Returns:
            Dict avec toutes les données géophysiques
        """
        # Vérifier le cache
        cached = self._load_from_cache(date)
        if cached:
            return cached
        
        logger.info(f"Collecte des données géophysiques pour {date.strftime('%Y-%m-%d')}")
        
        data = {
            'date': date.isoformat(),
            'collected_at': datetime.now().isoformat()
        }
        
        # Indice géomagnétique Kp
        try:
            data['geomagnetic'] = self.get_geomagnetic_index(date)
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"Erreur collecte indice Kp: {e}")
            data['geomagnetic'] = {}
        
        # Flux solaire
        try:
            data['solar_flux'] = self.get_solar_flux(date)
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"Erreur collecte flux solaire: {e}")
            data['solar_flux'] = {}
        
        # Activité sismique
        try:
            data['seismic'] = self.get_earthquake_activity(date)
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"Erreur collecte activité sismique: {e}")
            data['seismic'] = {}
        
        # Champ magnétique terrestre
        try:
            data['magnetic_field'] = self.get_earth_magnetic_field(date)
        except Exception as e:
            logger.error(f"Erreur champ magnétique: {e}")
            data['magnetic_field'] = {}
        
        # Sauvegarder en cache
        self._save_to_cache(date, data)
        
        logger.info("✓ Données géophysiques collectées avec succès")
        
        return data


def get_geophysical_data(date: datetime) -> Dict[str, Any]:
    """
    Fonction utilitaire pour récupérer les données géophysiques d'une date.
    
    Args:
        date: Date du tirage
        
    Returns:
        Dict avec toutes les données géophysiques
    """
    collector = GeophysicalDataCollector()
    return collector.collect_all_data(date)


if __name__ == "__main__":
    # Test du collecteur
    from datetime import datetime
    
    # Test avec la date d'un tirage
    test_date = datetime(2024, 10, 11, 21, 5)
    
    collector = GeophysicalDataCollector()
    data = collector.collect_all_data(test_date)
    
    print("\n=== DONNÉES GÉOPHYSIQUES ===")
    print(json.dumps(data, indent=2, ensure_ascii=False))
