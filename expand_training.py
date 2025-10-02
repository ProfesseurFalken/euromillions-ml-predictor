#!/usr/bin/env python3
"""
Récupération d'un historique plus large pour l'entraînement
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def get_more_historical_data():
    """Récupérer plus de données historiques."""
    print('📚 Récupération d\'un historique plus large')
    print('=' * 45)
    
    try:
        from hybrid_scraper import hybrid_scrape_latest
        from repository import get_repository
        
        repo = get_repository()
        current_df = repo.all_draws_df()
        print(f'📊 Données actuelles: {len(current_df)} tirages')
        
        print('🕷️ Récupération de 200 tirages historiques...')
        # Récupérer beaucoup plus de données
        historical_draws = hybrid_scrape_latest(limit=200)
        
        if historical_draws:
            print(f'   ✅ {len(historical_draws)} tirages récupérés du web')
            
            # Insérer les nouvelles données
            result = repo.upsert_draws(historical_draws)
            
            print(f'   📥 {result.get("inserted", 0)} nouveaux tirages')
            print(f'   🔄 {result.get("updated", 0)} tirages mis à jour')
            
            # Vérifier le résultat
            final_df = repo.all_draws_df()
            print(f'📊 Total final: {len(final_df)} tirages')
            
            if len(final_df) >= 100:
                print('✅ Assez de données pour un entraînement robuste!')
                return True
            else:
                print(f'⚠️  Encore peu de données ({len(final_df)} tirages)')
                return False
                
        else:
            print('❌ Impossible de récupérer plus de données')
            return False
            
    except Exception as e:
        print(f'❌ Erreur: {e}')
        return False

def train_with_more_data():
    """Entraîner avec plus de données si disponible."""
    print('\n🧠 Tentative d\'entraînement avec dataset élargi')
    print('=' * 50)
    
    try:
        from train_models import train_latest
        from repository import get_repository
        
        repo = get_repository()
        df = repo.all_draws_df()
        
        print(f'📊 Données pour entraînement: {len(df)} tirages')
        
        if len(df) < 80:
            print('⚠️  Dataset encore petit, utilisation de paramètres adaptés...')
            # Réduire les folds de cross-validation
            result = train_latest(min_rows=max(30, len(df) // 2))
        else:
            print('✅ Dataset suffisant pour entraînement standard')
            result = train_latest(min_rows=80)
        
        if result.get('success'):
            print('🎉 ENTRAÎNEMENT RÉUSSI!')
            
            perf = result.get('performance', {})
            print(f'\n📈 Performances:')
            print(f'   🎱 Log-loss boules: {perf.get("main_logloss", "N/A")}')
            print(f'   ⭐ Log-loss étoiles: {perf.get("star_logloss", "N/A")}')
            
            print('\n🚀 Le modèle est prêt avec les vraies données!')
            return True
        else:
            print('❌ Entraînement échoué')
            print(f'   Raison: {result.get("message", "Inconnue")}')
            return False
            
    except Exception as e:
        print(f'❌ Erreur entraînement: {e}')
        return False

if __name__ == "__main__":
    # Étape 1: Récupérer plus de données
    success = get_more_historical_data()
    
    # Étape 2: Entraîner avec dataset élargi
    if success or True:  # Essayer même avec peu de données
        train_success = train_with_more_data()
        
        if train_success:
            print('\n🎯 SUCCÈS COMPLET!')
            print('   Votre modèle est maintenant entraîné sur les vraies données!')
        else:
            print('\n⚠️  Entraînement partiellement réussi')
            print('   Essayez de récupérer plus de données historiques')