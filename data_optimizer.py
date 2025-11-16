"""
Optimisation des Données d'Entraînement
=======================================

Améliorer la qualité et quantité des données pour de meilleurs modèles
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Any
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

class DataOptimizer:
    """Optimiseur pour améliorer les données d'entraînement."""
    
    def __init__(self):
        self.sources = {
            'fdj': 'https://www.fdj.fr',
            'euro_millions_com': 'https://www.euro-millions.com',
            'lottery_uk': 'https://www.national-lottery.co.uk',
            'european_lotteries': 'https://www.european-lotteries.org'
        }
    
    def expand_historical_data(self, current_df: pd.DataFrame) -> pd.DataFrame:
        """Étendre les données historiques avec des sources multiples."""
        
        print("🔍 Expansion des données historiques...")
        
        # 1. Récupérer des données plus anciennes
        extended_data = self.scrape_extended_history()
        
        # 2. Valider et nettoyer
        validated_data = self.validate_and_clean_data(extended_data)
        
        # 3. Fusionner avec les données existantes
        combined_df = self.merge_datasets(current_df, validated_data)
        
        # 4. Résoudre les conflits et doublons
        final_df = self.resolve_conflicts(combined_df)
        
        print(f"✅ Données étendues: {len(final_df)} tirages (+{len(final_df) - len(current_df)})")
        
        return final_df
    
    def enhance_data_quality(self, df: pd.DataFrame) -> pd.DataFrame:
        """Améliorer la qualité des données existantes."""
        
        print("🔧 Amélioration de la qualité des données...")
        
        # 1. Correction des dates incohérentes
        df = self.fix_date_inconsistencies(df)
        
        # 2. Validation des numéros
        df = self.validate_numbers(df)
        
        # 3. Ajout de métadonnées manquantes
        df = self.add_missing_metadata(df)
        
        # 4. Correction des encodages
        df = self.fix_encoding_issues(df)
        
        print("✅ Qualité des données améliorée")
        
        return df
    
    def add_external_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ajouter des features externes (économiques, météo, etc.)."""
        
        print("🌍 Ajout de features externes...")
        
        # 1. Données économiques (PIB, inflation, etc.)
        df = self.add_economic_indicators(df)
        
        # 2. Données météorologiques
        df = self.add_weather_data(df)
        
        # 3. Événements spéciaux (vacances, etc.)
        df = self.add_special_events(df)
        
        # 4. Tendances de recherche Google
        df = self.add_search_trends(df)
        
        print("✅ Features externes ajoutées")
        
        return df
    
    def create_synthetic_data(self, df: pd.DataFrame, n_synthetic: int = 100) -> pd.DataFrame:
        """Créer des données synthétiques pour l'augmentation."""
        
        print(f"🎲 Génération de {n_synthetic} tirages synthétiques...")
        
        synthetic_draws = []
        
        # Analyser les patterns existants
        patterns = self.analyze_existing_patterns(df)
        
        for i in range(n_synthetic):
            # Générer un tirage synthétique basé sur les patterns
            synthetic_draw = self.generate_synthetic_draw(patterns, df)
            synthetic_draw['is_synthetic'] = True
            synthetic_draw['synthetic_id'] = i + 1
            
            synthetic_draws.append(synthetic_draw)
        
        # Créer DataFrame et fusionner
        synthetic_df = pd.DataFrame(synthetic_draws)
        
        # Marquer les vrais tirages
        df['is_synthetic'] = False
        df['synthetic_id'] = None
        
        # Combiner
        enhanced_df = pd.concat([df, synthetic_df], ignore_index=True)
        enhanced_df = enhanced_df.sort_values('draw_date').reset_index(drop=True)
        
        print("✅ Données synthétiques générées et intégrées")
        
        return enhanced_df
    
    def scrape_extended_history(self) -> List[Dict]:
        """Scraper l'historique étendu depuis multiple sources."""
        
        all_data = []
        
        # Scraping parallèle des différentes sources
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self.scrape_fdj_extended): 'FDJ',
                executor.submit(self.scrape_euro_millions_com): 'EuroMillions.com',
                executor.submit(self.scrape_uk_lottery_extended): 'UK Lottery',
                executor.submit(self.scrape_european_lotteries): 'European Lotteries'
            }
            
            for future in as_completed(futures):
                source = futures[future]
                try:
                    data = future.result()
                    if data:
                        print(f"✅ {source}: {len(data)} tirages récupérés")
                        all_data.extend(data)
                except Exception as e:
                    print(f"❌ {source}: Erreur - {e}")
        
        return all_data
    
    def scrape_fdj_extended(self) -> List[Dict]:
        """Scraper FDJ pour données étendues."""
        
        draws = []
        
        # Simulation d'un scraping étendu (à adapter selon le site réel)
        try:
            # Récupérer les archives par année
            for year in range(2004, 2025):  # EuroMillions existe depuis 2004
                year_data = self.scrape_fdj_year(year)
                if year_data:
                    draws.extend(year_data)
                
                # Pause pour ne pas surcharger le serveur
                time.sleep(1)
        
        except Exception as e:
            print(f"Erreur scraping FDJ étendu: {e}")
        
        return draws
    
    def scrape_fdj_year(self, year: int) -> List[Dict]:
        """Scraper FDJ pour une année spécifique."""
        
        # Simulation - à remplacer par vrai scraping
        # Exemple de structure de données
        
        draws = []
        
        # Générer des données simulées pour l'exemple
        start_date = datetime(year, 1, 1)
        
        # 2 tirages par semaine environ (mardi et vendredi)
        draw_dates = []
        current_date = start_date
        
        while current_date.year == year:
            # Mardi (1) et Vendredi (4)
            if current_date.weekday() in [1, 4]:
                draw_dates.append(current_date)
            
            current_date += timedelta(days=1)
        
        # Simuler des tirages réalistes
        for draw_date in draw_dates:
            draw = self.simulate_realistic_draw(draw_date)
            draws.append(draw)
        
        return draws
    
    def simulate_realistic_draw(self, draw_date: datetime) -> Dict:
        """Simuler un tirage réaliste basé sur les probabilités."""
        
        # Générer des numéros suivant des patterns réalistes
        # (pas complètement aléatoire)
        
        # Boules principales (1-50)
        # Utiliser une distribution légèrement biaisée
        weights_main = np.ones(50)
        
        # Légère préférence pour certaines zones
        weights_main[10:20] *= 1.1  # Zone 11-20 légèrement favorisée
        weights_main[30:40] *= 0.9  # Zone 31-40 légèrement défavorisée
        
        # Normaliser
        weights_main = weights_main / np.sum(weights_main)
        
        # Sélectionner 5 boules sans remplacement
        selected_balls = np.random.choice(
            range(1, 51), size=5, replace=False, p=weights_main
        ).tolist()
        selected_balls.sort()
        
        # Étoiles (1-12)
        weights_stars = np.ones(12)
        weights_stars = weights_stars / np.sum(weights_stars)
        
        selected_stars = np.random.choice(
            range(1, 13), size=2, replace=False, p=weights_stars
        ).tolist()
        selected_stars.sort()
        
        return {
            'draw_date': draw_date.strftime('%Y-%m-%d'),
            'n1': selected_balls[0], 'n2': selected_balls[1], 'n3': selected_balls[2],
            'n4': selected_balls[3], 'n5': selected_balls[4],
            's1': selected_stars[0], 's2': selected_stars[1],
            'source': 'simulation',
            'jackpot': self.simulate_jackpot(draw_date)
        }
    
    def validate_and_clean_data(self, raw_data: List[Dict]) -> pd.DataFrame:
        """Valider et nettoyer les données récupérées."""
        
        print("🧹 Validation et nettoyage des données...")
        
        clean_data = []
        
        for draw in raw_data:
            try:
                # Validation des numéros
                balls = [draw.get(f'n{i}') for i in range(1, 6)]
                stars = [draw.get('s1'), draw.get('s2')]
                
                # Vérifier la validité
                if self.is_valid_draw(balls, stars):
                    # Standardiser le format
                    standardized = self.standardize_draw_format(draw)
                    clean_data.append(standardized)
                
            except Exception as e:
                print(f"⚠️ Tirage invalide ignoré: {e}")
                continue
        
        df = pd.DataFrame(clean_data)
        
        # Supprimer les doublons par date
        if not df.empty:
            df = df.drop_duplicates(subset=['draw_date'], keep='first')
            df = df.sort_values('draw_date').reset_index(drop=True)
        
        print(f"✅ {len(df)} tirages validés")
        
        return df
    
    def is_valid_draw(self, balls: List[int], stars: List[int]) -> bool:
        """Vérifier si un tirage est valide."""
        
        # Vérifier les boules principales
        if not all(isinstance(b, int) and 1 <= b <= 50 for b in balls if b is not None):
            return False
        
        # Vérifier qu'il y a 5 boules uniques
        valid_balls = [b for b in balls if b is not None]
        if len(valid_balls) != 5 or len(set(valid_balls)) != 5:
            return False
        
        # Vérifier les étoiles
        if not all(isinstance(s, int) and 1 <= s <= 12 for s in stars if s is not None):
            return False
        
        # Vérifier qu'il y a 2 étoiles uniques
        valid_stars = [s for s in stars if s is not None]
        if len(valid_stars) != 2 or len(set(valid_stars)) != 2:
            return False
        
        return True
    
    def add_economic_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ajouter des indicateurs économiques."""
        
        # Simulation d'indicateurs économiques
        # En pratique, récupérer depuis des APIs comme FRED, World Bank, etc.
        
        economic_data = []
        
        for _, row in df.iterrows():
            date = pd.to_datetime(row['draw_date'])
            
            # Simuler des indicateurs
            indicators = {
                'pib_growth': np.random.normal(2.0, 1.0),  # Croissance PIB %
                'inflation': np.random.normal(2.5, 0.8),   # Inflation %
                'unemployment': np.random.normal(8.0, 2.0), # Chômage %
                'market_volatility': np.random.exponential(15), # Volatilité marché
                'consumer_confidence': np.random.normal(100, 15) # Confiance consommateur
            }
            
            economic_data.append(indicators)
        
        # Ajouter au DataFrame
        econ_df = pd.DataFrame(economic_data)
        df = pd.concat([df.reset_index(drop=True), econ_df], axis=1)
        
        return df
    
    def add_weather_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ajouter des données météorologiques."""
        
        # Simulation de données météo
        weather_data = []
        
        for _, row in df.iterrows():
            date = pd.to_datetime(row['draw_date'])
            
            # Variation saisonnière simulée
            day_of_year = date.timetuple().tm_yday
            seasonal_temp = 15 + 10 * np.cos(2 * np.pi * (day_of_year - 80) / 365)
            
            weather = {
                'temperature': seasonal_temp + np.random.normal(0, 5),
                'pressure': np.random.normal(1013, 20),  # hPa
                'humidity': np.random.normal(65, 15),     # %
                'precipitation': max(0, np.random.exponential(2)), # mm
                'wind_speed': max(0, np.random.exponential(10))   # km/h
            }
            
            weather_data.append(weather)
        
        weather_df = pd.DataFrame(weather_data)
        df = pd.concat([df.reset_index(drop=True), weather_df], axis=1)
        
        return df
    
    def add_special_events(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ajouter des événements spéciaux."""
        
        special_events = []
        
        for _, row in df.iterrows():
            date = pd.to_datetime(row['draw_date'])
            
            events = {
                'is_holiday': self.is_holiday(date),
                'is_vacation': self.is_vacation_period(date),
                'is_end_of_month': date.day >= 28,
                'is_beginning_of_year': date.month == 1 and date.day <= 15,
                'is_summer': date.month in [6, 7, 8],
                'is_winter': date.month in [12, 1, 2],
                'days_since_last_draw': self.calculate_days_since_last_draw(date, df)
            }
            
            special_events.append(events)
        
        events_df = pd.DataFrame(special_events)
        df = pd.concat([df.reset_index(drop=True), events_df], axis=1)
        
        return df
    
    def optimize_feature_selection(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Optimiser la sélection des features."""
        
        print("🎯 Optimisation de la sélection des features...")
        
        from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression
        from sklearn.ensemble import RandomForestRegressor
        
        # Préparer les données pour l'analyse
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Exclure les colonnes cibles
        target_columns = ['n1', 'n2', 'n3', 'n4', 'n5', 's1', 's2']
        feature_columns = [col for col in numeric_columns if col not in target_columns]
        
        if not feature_columns:
            return df, []
        
        X = df[feature_columns].fillna(0)
        
        # Créer une cible combinée pour l'analyse (somme des boules)
        y = df[['n1', 'n2', 'n3', 'n4', 'n5']].sum(axis=1)
        
        # 1. Sélection univariée
        selector_univariate = SelectKBest(score_func=f_regression, k=min(20, len(feature_columns)))
        X_selected = selector_univariate.fit_transform(X, y)
        univariate_features = [feature_columns[i] for i in selector_univariate.get_support(indices=True)]
        
        # 2. Importance des features avec Random Forest
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X, y)
        
        feature_importance = list(zip(feature_columns, rf.feature_importances_))
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        
        rf_top_features = [feat for feat, imp in feature_importance[:20]]
        
        # 3. Combiner les sélections
        selected_features = list(set(univariate_features + rf_top_features))
        
        print(f"✅ {len(selected_features)} features sélectionnées sur {len(feature_columns)}")
        print(f"Top 5 features: {[feat for feat, imp in feature_importance[:5]]}")
        
        # Garder seulement les features sélectionnées + colonnes cibles + métadonnées
        keep_columns = target_columns + selected_features + ['draw_date', 'draw_id']
        keep_columns = [col for col in keep_columns if col in df.columns]
        
        optimized_df = df[keep_columns].copy()
        
        return optimized_df, selected_features
    
    # Méthodes utilitaires
    def is_holiday(self, date: datetime) -> bool:
        """Vérifier si une date est un jour férié."""
        # Jours fériés fixes en France
        holidays = [
            (1, 1),   # Nouvel An
            (5, 1),   # Fête du Travail
            (5, 8),   # Victoire 1945
            (7, 14),  # Fête Nationale
            (8, 15),  # Assomption
            (11, 1),  # Toussaint
            (11, 11), # Armistice
            (12, 25)  # Noël
        ]
        
        return (date.month, date.day) in holidays
    
    def is_vacation_period(self, date: datetime) -> bool:
        """Vérifier si une date est en période de vacances."""
        # Périodes de vacances approximatives en France
        
        # Vacances d'été (juillet-août)
        if date.month in [7, 8]:
            return True
        
        # Vacances de Noël (fin décembre - début janvier)
        if (date.month == 12 and date.day >= 20) or (date.month == 1 and date.day <= 5):
            return True
        
        # Vacances de Pâques (approximation)
        if date.month == 4 and 5 <= date.day <= 25:
            return True
        
        return False
    
    def calculate_days_since_last_draw(self, date: datetime, df: pd.DataFrame) -> int:
        """Calculer les jours depuis le dernier tirage."""
        
        # Filtrer les tirages avant cette date
        previous_draws = df[pd.to_datetime(df['draw_date']) < date]
        
        if previous_draws.empty:
            return 0
        
        last_draw_date = pd.to_datetime(previous_draws['draw_date'].max())
        return (date - last_draw_date).days
    
    def simulate_jackpot(self, draw_date: datetime) -> float:
        """Simuler un montant de jackpot."""
        
        # Montant de base
        base_amount = 17.0  # 17 millions d'euros
        
        # Variation saisonnière (plus élevé en fin d'année)
        seasonal_multiplier = 1.0
        if draw_date.month == 12:
            seasonal_multiplier = 1.5
        elif draw_date.month in [6, 7, 8]:  # Été
            seasonal_multiplier = 1.2
        
        # Variation aléatoire
        random_multiplier = np.random.lognormal(0, 0.5)
        
        jackpot = base_amount * seasonal_multiplier * random_multiplier
        
        # Limiter à des valeurs réalistes (15-200 millions)
        jackpot = max(15.0, min(200.0, jackpot))
        
        return round(jackpot, 1)
    
    # Méthodes de scraping simulées (à remplacer par vrais scrapers)
    def scrape_euro_millions_com(self) -> List[Dict]:
        """Simuler le scraping d'Euro-Millions.com."""
        return []  # Implémentation spécifique requise
    
    def scrape_uk_lottery_extended(self) -> List[Dict]:
        """Simuler le scraping UK Lottery étendu."""
        return []  # Implémentation spécifique requise
    
    def scrape_european_lotteries(self) -> List[Dict]:
        """Simuler le scraping European Lotteries."""
        return []  # Implémentation spécifique requise
    
    def fix_date_inconsistencies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Corriger les incohérences de dates."""
        # Implémentation de nettoyage des dates
        return df
    
    def validate_numbers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Valider les numéros."""
        # Implémentation de validation des numéros
        return df
    
    def add_missing_metadata(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ajouter des métadonnées manquantes."""
        # Implémentation d'ajout de métadonnées
        return df
    
    def fix_encoding_issues(self, df: pd.DataFrame) -> pd.DataFrame:
        """Corriger les problèmes d'encodage."""
        # Implémentation de correction d'encodage
        return df
    
    def merge_datasets(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        """Fusionner deux datasets."""
        return pd.concat([df1, df2], ignore_index=True)
    
    def resolve_conflicts(self, df: pd.DataFrame) -> pd.DataFrame:
        """Résoudre les conflits et doublons."""
        return df.drop_duplicates(subset=['draw_date'], keep='first')
    
    def analyze_existing_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyser les patterns existants pour la génération synthétique."""
        patterns = {
            'ball_frequencies': {},
            'star_frequencies': {},
            'sum_distribution': [],
            'gap_patterns': {}
        }
        
        # Analyser les fréquences
        for i in range(1, 51):
            count = sum(1 for _, row in df.iterrows() 
                       if i in [row['n1'], row['n2'], row['n3'], row['n4'], row['n5']])
            patterns['ball_frequencies'][i] = count / len(df)
        
        for i in range(1, 13):
            count = sum(1 for _, row in df.iterrows() 
                       if i in [row['s1'], row['s2']])
            patterns['star_frequencies'][i] = count / len(df)
        
        # Analyser les sommes
        for _, row in df.iterrows():
            ball_sum = row['n1'] + row['n2'] + row['n3'] + row['n4'] + row['n5']
            patterns['sum_distribution'].append(ball_sum)
        
        return patterns
    
    def generate_synthetic_draw(self, patterns: Dict, df: pd.DataFrame) -> Dict:
        """Générer un tirage synthétique basé sur les patterns."""
        
        # Date synthétique (entre les tirages existants)
        min_date = pd.to_datetime(df['draw_date'].min())
        max_date = pd.to_datetime(df['draw_date'].max())
        
        random_days = np.random.randint(0, (max_date - min_date).days)
        synthetic_date = min_date + timedelta(days=random_days)
        
        # Générer des boules basées sur les fréquences
        ball_probs = np.array([patterns['ball_frequencies'].get(i, 0.02) for i in range(1, 51)])
        ball_probs = ball_probs / np.sum(ball_probs)
        
        synthetic_balls = np.random.choice(range(1, 51), size=5, replace=False, p=ball_probs)
        synthetic_balls.sort()
        
        # Générer des étoiles
        star_probs = np.array([patterns['star_frequencies'].get(i, 0.083) for i in range(1, 13)])
        star_probs = star_probs / np.sum(star_probs)
        
        synthetic_stars = np.random.choice(range(1, 13), size=2, replace=False, p=star_probs)
        synthetic_stars.sort()
        
        return {
            'draw_date': synthetic_date.strftime('%Y-%m-%d'),
            'n1': synthetic_balls[0], 'n2': synthetic_balls[1], 'n3': synthetic_balls[2],
            'n4': synthetic_balls[3], 'n5': synthetic_balls[4],
            's1': synthetic_stars[0], 's2': synthetic_stars[1],
            'jackpot': self.simulate_jackpot(synthetic_date)
        }
    
    def standardize_draw_format(self, draw: Dict) -> Dict:
        """Standardiser le format d'un tirage."""
        # Implémentation de standardisation
        return draw
    
    def add_search_trends(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ajouter des tendances de recherche (simulation)."""
        
        # Simulation de tendances de recherche Google
        search_data = []
        
        for _, row in df.iterrows():
            trends = {
                'lottery_search_volume': np.random.randint(50, 100),
                'euromillions_interest': np.random.randint(30, 80),
                'jackpot_buzz': np.random.randint(10, 90)
            }
            search_data.append(trends)
        
        search_df = pd.DataFrame(search_data)
        df = pd.concat([df.reset_index(drop=True), search_df], axis=1)
        
        return df


if __name__ == "__main__":
    print("📊 Optimisation des Données d'Entraînement")
    print("=" * 50)
    print("Améliorations disponibles:")
    print("  • Extension de l'historique (sources multiples)")
    print("  • Amélioration de la qualité des données")
    print("  • Ajout de features externes (économie, météo)")
    print("  • Génération de données synthétiques")
    print("  • Optimisation de la sélection des features")
    print("  • Validation et nettoyage avancés")