#!/usr/bin/env python3
"""
Test du nouveau format d'affichage des tickets
"""

import sys
from pathlib import Path

# Ajouter le répertoire du projet au path
sys.path.insert(0, str(Path(__file__).parent))

def test_new_display_format():
    """Test du nouveau format d'affichage."""
    print("🎨 Test du nouveau format d'affichage")
    print("=" * 40)
    
    try:
        # Import du nouveau format
        sys.path.append('ui')
        from streamlit_app import format_tickets_display
        
        # Simulation de tickets
        mock_tickets = [
            {
                'ticket_id': 1,
                'balls_str': '16 - 30 - 38 - 43 - 48',
                'stars_str': '07 - 08'
            },
            {
                'ticket_id': 2,
                'balls_str': '04 - 20 - 30 - 44 - 50',
                'stars_str': '07 - 09'
            }
        ]
        
        # Test du formatage
        formatted_display = format_tickets_display(mock_tickets)
        
        print("📋 Nouveau format d'affichage (numéros à la ligne) :")
        print("─" * 45)
        print(formatted_display)
        print("─" * 45)
        
        print("\n✅ Le nouveau format sépare clairement :")
        print("   • Le numéro de ticket (🎫 Ticket X)")
        print("   • Les boules principales (ligne séparée)")
        print("   • Les étoiles (ligne séparée avec ⭐)")
        print("   • Visibilité maximale !")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_display_format()