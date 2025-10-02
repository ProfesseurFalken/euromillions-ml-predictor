#!/usr/bin/env python3
"""
Re-entraînement avec les vraies données
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def retrain_with_real_data():
    """Re-entraîner le modèle avec les vraies données."""
    print('🧠 Re-entraînement du modèle avec les vraies données')
    print('=' * 55)
    
    try:
        from train_models import train_latest
        from repository import get_repository
        
        # Vérifier les données disponibles
        repo = get_repository()
        df = repo.all_draws_df()
        
        print(f'📊 Données disponibles: {len(df)} tirages réels')
        
        if len(df) < 30:
            print(f'⚠️  Peu de données ({len(df)} tirages)')
            print('   Les performances peuvent être limitées')
        
        # Re-entraîner avec un seuil adapté
        print('\n🏋️ Démarrage de l\'entraînement...')
        min_rows = min(30, len(df))  # Adapter au nombre de données disponibles
        
        result = train_latest(min_rows=min_rows)
        
        if result.get('success'):
            print('✅ RE-ENTRAÎNEMENT RÉUSSI!')
            
            # Afficher les nouvelles métriques
            perf = result.get('performance', {})
            data_range = result.get('data_range', {})
            
            print('\n📈 Nouvelles performances:')
            main_loss = perf.get('main_logloss', 'N/A')
            star_loss = perf.get('star_logloss', 'N/A')
            
            print(f'   🎱 Log-loss boules principales: {main_loss}')
            print(f'   ⭐ Log-loss étoiles: {star_loss}')
            
            if isinstance(main_loss, (int, float)) and main_loss < 0.70:
                print('   🔥 Excellentes performances!')
            elif isinstance(main_loss, (int, float)) and main_loss < 0.80:
                print('   ✅ Bonnes performances!')
            else:
                print('   🆗 Performances correctes')
            
            print(f'\n📊 Données d\'entraînement:')
            print(f'   📅 Période: {data_range.get("from", "N/A")} à {data_range.get("to", "N/A")}')
            print(f'   🎯 Échantillons: {data_range.get("n_samples", "N/A")} tirages')
            
            print('\n🎉 MODÈLE PRÊT!')
            print('   Vous pouvez maintenant générer des prédictions basées sur les vrais données!')
            
        else:
            print('❌ Entraînement échoué')
            print(f'   Raison: {result.get("message", "Erreur inconnue")}')
            
            # Suggestions
            print('\n💡 Suggestions:')
            print('   • Vérifiez que vous avez assez de données (minimum 30 tirages)')
            print('   • Essayez de récupérer plus d\'historique')
            
    except Exception as e:
        print(f'❌ Erreur: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    retrain_with_real_data()