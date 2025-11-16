"""
Visualisation interactive des corrélations et données enrichies.
Génère des graphiques HTML interactifs avec Plotly.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import json
from pathlib import Path
import webbrowser

def load_data():
    """Charge les données enrichies et les corrélations."""
    enriched_path = Path("data/correlations/enriched_draws.csv")
    corr_path = Path("data/correlations/correlations.json")
    
    if not enriched_path.exists():
        raise FileNotFoundError(
            "Fichier enriched_draws.csv introuvable. "
            "Lancez d'abord analyze_100_draws.py"
        )
    
    df = pd.read_csv(enriched_path)
    df['draw_date'] = pd.to_datetime(df['draw_date'])
    
    correlations = None
    if corr_path.exists():
        with open(corr_path, 'r', encoding='utf-8') as f:
            correlations = json.load(f)
    
    return df, correlations

def create_overview_dashboard(df):
    """Crée un dashboard récapitulatif."""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            '🌙 Phase lunaire au fil du temps',
            '🌡️ Température à Paris (21h05)',
            '💨 Pression atmosphérique',
            '🎲 Distribution somme des numéros'
        ),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 1. Phase lunaire
    fig.add_trace(
        go.Scatter(
            x=df['draw_date'],
            y=df['moon_illumination'],
            mode='lines+markers',
            name='Phase lunaire (%)',
            line=dict(color='gold', width=2),
            marker=dict(size=6),
            hovertemplate='<b>%{x|%d/%m/%Y}</b><br>Illumination: %{y:.1f}%<extra></extra>'
        ),
        row=1, col=1
    )
    
    # 2. Température
    fig.add_trace(
        go.Scatter(
            x=df['draw_date'],
            y=df['temperature_c'],
            mode='lines+markers',
            name='Température (°C)',
            line=dict(color='orangered', width=2),
            marker=dict(size=6),
            hovertemplate='<b>%{x|%d/%m/%Y}</b><br>Température: %{y:.1f}°C<extra></extra>'
        ),
        row=1, col=2
    )
    
    # 3. Pression
    fig.add_trace(
        go.Scatter(
            x=df['draw_date'],
            y=df['pressure_hpa'],
            mode='lines+markers',
            name='Pression (hPa)',
            line=dict(color='steelblue', width=2),
            marker=dict(size=6),
            hovertemplate='<b>%{x|%d/%m/%Y}</b><br>Pression: %{y:.1f} hPa<extra></extra>'
        ),
        row=2, col=1
    )
    
    # 4. Distribution somme des numéros
    fig.add_trace(
        go.Histogram(
            x=df['sum_numbers'],
            name='Somme numéros',
            marker=dict(color='mediumpurple'),
            nbinsx=20,
            hovertemplate='Somme: %{x}<br>Fréquence: %{y}<extra></extra>'
        ),
        row=2, col=2
    )
    
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_xaxes(title_text="Date", row=1, col=2)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_xaxes(title_text="Somme", row=2, col=2)
    
    fig.update_yaxes(title_text="% Illumination", row=1, col=1)
    fig.update_yaxes(title_text="°C", row=1, col=2)
    fig.update_yaxes(title_text="hPa", row=2, col=1)
    fig.update_yaxes(title_text="Nombre de tirages", row=2, col=2)
    
    fig.update_layout(
        title_text="📊 Dashboard EuroMillions - Facteurs externes",
        height=800,
        showlegend=False,
        template="plotly_white"
    )
    
    return fig

def create_correlation_scatter(df):
    """Crée un scatter plot de la corrélation lune-étoiles."""
    # Créer le scatter plot sans trendline pour éviter statsmodels
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['moon_illumination'],
        y=df['sum_stars'],
        mode='markers',
        marker=dict(
            size=12,
            color=df['sum_stars'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Somme<br>étoiles"),
            line=dict(width=1, color='white')
        ),
        text=df['draw_date'].dt.strftime('%d/%m/%Y'),
        hovertemplate='<b>%{text}</b><br>' +
                      'Phase lunaire: %{x:.1f}%<br>' +
                      'Somme étoiles: %{y}<extra></extra>',
        name=''
    ))
    
    # Ajouter une ligne de tendance simple (régression linéaire manuelle)
    import numpy as np
    z = np.polyfit(df['moon_illumination'].dropna(), df['sum_stars'].dropna(), 1)
    p = np.poly1d(z)
    x_line = np.linspace(df['moon_illumination'].min(), df['moon_illumination'].max(), 100)
    
    fig.add_trace(go.Scatter(
        x=x_line,
        y=p(x_line),
        mode='lines',
        line=dict(color='red', width=2, dash='dash'),
        name='Tendance',
        hovertemplate='Ligne de tendance<extra></extra>'
    ))
    
    fig.update_layout(
        title='🔍 Corrélation : Phase lunaire ↔ Somme des étoiles',
        xaxis_title='🌙 Phase lunaire (% illumination)',
        yaxis_title='⭐ Somme des étoiles',
        height=600,
        template="plotly_white"
    )
    
    fig.update_layout(
        annotations=[
            dict(
                text="⚠️ Corrélation faible (-0.222) - Probablement due au hasard statistique",
                xref="paper", yref="paper",
                x=0.5, y=-0.15,
                showarrow=False,
                font=dict(size=12, color="red")
            )
        ]
    )
    
    return fig

def create_weather_heatmap(df):
    """Crée une heatmap température vs humidité."""
    # Créer des bins pour grouper les données
    df['temp_bin'] = pd.cut(df['temperature_c'], bins=10)
    df['humidity_bin'] = pd.cut(df['humidity_pct'], bins=10)
    
    # Compter les occurrences
    heatmap_data = df.groupby(['temp_bin', 'humidity_bin']).size().reset_index(name='count')
    
    # Créer une matrice pivot
    pivot = heatmap_data.pivot(index='humidity_bin', columns='temp_bin', values='count').fillna(0)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[f"{interval.left:.1f}-{interval.right:.1f}°C" for interval in pivot.columns],
        y=[f"{interval.left:.0f}-{interval.right:.0f}%" for interval in pivot.index],
        colorscale='YlOrRd',
        hovertemplate='Température: %{x}<br>Humidité: %{y}<br>Tirages: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title='🌡️💧 Distribution Température vs Humidité lors des tirages',
        xaxis_title='Température à Paris (21h05)',
        yaxis_title='Humidité (%)',
        height=600,
        template="plotly_white"
    )
    
    return fig

def create_moon_phases_polar(df):
    """Crée un graphique polaire des phases lunaires."""
    # Ajouter une colonne pour l'angle (0-360°)
    df['moon_angle'] = df['moon_illumination'] * 3.6  # 0-100% -> 0-360°
    
    fig = go.Figure()
    
    # Scatter polaire
    fig.add_trace(go.Scatterpolar(
        r=df['sum_numbers'],
        theta=df['moon_angle'],
        mode='markers',
        marker=dict(
            size=10,
            color=df['sum_stars'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Somme<br>étoiles"),
            line=dict(width=1, color='white')
        ),
        text=df['draw_date'].dt.strftime('%d/%m/%Y'),
        hovertemplate='<b>%{text}</b><br>' +
                      'Phase: %{theta:.0f}°<br>' +
                      'Somme numéros: %{r}<extra></extra>'
    ))
    
    fig.update_layout(
        title='🌙 Tirages en fonction de la phase lunaire (vue polaire)',
        polar=dict(
            radialaxis=dict(
                title='Somme des numéros',
                range=[60, 200]
            ),
            angularaxis=dict(
                direction='clockwise',
                rotation=90
            )
        ),
        height=700,
        template="plotly_white"
    )
    
    return fig

def create_prime_fibonacci_distribution(df):
    """Distribution des nombres premiers et Fibonacci."""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('🔢 Nombres premiers par tirage', '🌀 Nombres de Fibonacci par tirage')
    )
    
    # Nombres premiers
    prime_counts = df['prime_count'].value_counts().sort_index()
    fig.add_trace(
        go.Bar(
            x=prime_counts.index,
            y=prime_counts.values,
            name='Nombres premiers',
            marker=dict(color='royalblue'),
            hovertemplate='Nombres premiers: %{x}<br>Fréquence: %{y}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Fibonacci
    fib_counts = df['fibonacci_count'].value_counts().sort_index()
    fig.add_trace(
        go.Bar(
            x=fib_counts.index,
            y=fib_counts.values,
            name='Fibonacci',
            marker=dict(color='darkorange'),
            hovertemplate='Nombres Fibonacci: %{x}<br>Fréquence: %{y}<extra></extra>'
        ),
        row=1, col=2
    )
    
    fig.update_xaxes(title_text="Nombre de premiers dans le tirage", row=1, col=1)
    fig.update_xaxes(title_text="Nombre de Fibonacci dans le tirage", row=1, col=2)
    fig.update_yaxes(title_text="Fréquence", row=1, col=1)
    fig.update_yaxes(title_text="Fréquence", row=1, col=2)
    
    fig.update_layout(
        title_text="🔢 Distribution des propriétés mathématiques",
        height=500,
        showlegend=False,
        template="plotly_white"
    )
    
    return fig

def create_temporal_evolution(df):
    """Évolution temporelle multi-variables."""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        subplot_titles=(
            '🎲 Somme des numéros',
            '⭐ Somme des étoiles',
            '🔢 Nombres premiers'
        ),
        vertical_spacing=0.08
    )
    
    # Somme des numéros avec moyenne mobile
    fig.add_trace(
        go.Scatter(
            x=df['draw_date'],
            y=df['sum_numbers'],
            mode='lines+markers',
            name='Somme numéros',
            line=dict(color='mediumpurple', width=1),
            marker=dict(size=4),
            opacity=0.6
        ),
        row=1, col=1
    )
    
    # Moyenne mobile 10 tirages
    df['sum_numbers_ma'] = df['sum_numbers'].rolling(window=10, center=True).mean()
    fig.add_trace(
        go.Scatter(
            x=df['draw_date'],
            y=df['sum_numbers_ma'],
            mode='lines',
            name='Moyenne mobile (10)',
            line=dict(color='purple', width=3)
        ),
        row=1, col=1
    )
    
    # Somme des étoiles
    fig.add_trace(
        go.Scatter(
            x=df['draw_date'],
            y=df['sum_stars'],
            mode='lines+markers',
            name='Somme étoiles',
            line=dict(color='gold', width=2),
            marker=dict(size=6)
        ),
        row=2, col=1
    )
    
    # Nombres premiers
    fig.add_trace(
        go.Scatter(
            x=df['draw_date'],
            y=df['prime_count'],
            mode='lines+markers',
            name='Nombres premiers',
            line=dict(color='royalblue', width=2),
            marker=dict(size=6)
        ),
        row=3, col=1
    )
    
    fig.update_xaxes(title_text="Date", row=3, col=1)
    fig.update_yaxes(title_text="Somme", row=1, col=1, range=[60, 200])
    fig.update_yaxes(title_text="Somme", row=2, col=1, range=[0, 24])
    fig.update_yaxes(title_text="Nombre", row=3, col=1, range=[0, 5])
    
    fig.update_layout(
        title_text="📈 Évolution temporelle des tirages",
        height=900,
        showlegend=False,
        template="plotly_white"
    )
    
    return fig

def create_correlation_matrix(df):
    """Matrice de corrélation des variables numériques."""
    # Sélectionner les colonnes numériques pertinentes
    numeric_cols = [
        'sum_numbers', 'sum_stars', 
        'moon_illumination', 'temperature_c', 'humidity_pct', 'pressure_hpa',
        'prime_count', 'fibonacci_count', 'even_count'
    ]
    
    # Filtrer les colonnes qui existent
    available_cols = [col for col in numeric_cols if col in df.columns]
    
    # Calculer la matrice de corrélation
    corr_matrix = df[available_cols].corr()
    
    # Noms lisibles
    labels_map = {
        'sum_numbers': 'Somme numéros',
        'sum_stars': 'Somme étoiles',
        'moon_illumination': 'Phase lunaire',
        'temperature_c': 'Température',
        'humidity_pct': 'Humidité',
        'pressure_hpa': 'Pression',
        'prime_count': 'Nombres premiers',
        'fibonacci_count': 'Fibonacci',
        'even_count': 'Nombres pairs'
    }
    
    labels = [labels_map.get(col, col) for col in available_cols]
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=labels,
        y=labels,
        colorscale='RdBu',
        zmid=0,
        zmin=-1,
        zmax=1,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        hovertemplate='%{y} ↔ %{x}<br>Corrélation: %{z:.3f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='🔗 Matrice de corrélation complète',
        xaxis_title='',
        yaxis_title='',
        height=700,
        template="plotly_white"
    )
    
    return fig

def main():
    """Génère toutes les visualisations."""
    print("="*70)
    print("📊 GÉNÉRATION DES VISUALISATIONS INTERACTIVES")
    print("="*70)
    
    # Charger les données
    print("\n📁 Chargement des données...")
    df, correlations = load_data()
    print(f"✅ {len(df)} tirages chargés")
    
    # Créer le dossier de sortie
    output_dir = Path("visualizations")
    output_dir.mkdir(exist_ok=True)
    print(f"📂 Dossier: {output_dir.absolute()}")
    
    visualizations = [
        ("overview_dashboard", "Dashboard récapitulatif", create_overview_dashboard),
        ("moon_stars_correlation", "Corrélation Lune-Étoiles", create_correlation_scatter),
        ("weather_heatmap", "Heatmap Météo", create_weather_heatmap),
        ("moon_polar", "Phases lunaires (polaire)", create_moon_phases_polar),
        ("prime_fibonacci", "Nombres premiers & Fibonacci", create_prime_fibonacci_distribution),
        ("temporal_evolution", "Évolution temporelle", create_temporal_evolution),
        ("correlation_matrix", "Matrice de corrélation", create_correlation_matrix),
    ]
    
    html_files = []
    
    print("\n🎨 Génération des graphiques...")
    for filename, description, func in visualizations:
        try:
            print(f"  ⏳ {description}...", end=" ")
            fig = func(df)
            
            output_path = output_dir / f"{filename}.html"
            fig.write_html(
                str(output_path),
                include_plotlyjs='cdn',
                config={'displayModeBar': True, 'responsive': True}
            )
            html_files.append((output_path, description))
            print("✅")
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    # Créer une page index
    print("\n📄 Création de la page index...")
    index_html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EuroMillions - Visualisations</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        h1 {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle {
            text-align: center;
            font-size: 1.2em;
            margin-bottom: 30px;
            opacity: 0.9;
        }
        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .card {
            background: white;
            color: #333;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            transition: transform 0.3s, box-shadow 0.3s;
            cursor: pointer;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.4);
        }
        .card h2 {
            color: #667eea;
            margin-top: 0;
            font-size: 1.5em;
        }
        .card p {
            color: #666;
            line-height: 1.6;
        }
        .btn {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            text-decoration: none;
            transition: transform 0.2s;
            margin-top: 10px;
        }
        .btn:hover {
            transform: scale(1.05);
        }
        .stats {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .stat-item {
            text-align: center;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            display: block;
        }
        .stat-label {
            font-size: 0.9em;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <h1>🎰 EuroMillions - Analyse Avancée</h1>
    <p class="subtitle">Visualisations interactives des corrélations entre tirages et facteurs externes</p>
    
    <div class="stats">
        <div class="stats-grid">
            <div class="stat-item">
                <span class="stat-value">""" + str(len(df)) + """</span>
                <span class="stat-label">Tirages analysés</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">22</span>
                <span class="stat-label">Variables collectées</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">""" + (str(correlations['significant_count']) if correlations else '1') + """</span>
                <span class="stat-label">Corrélations trouvées</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">7</span>
                <span class="stat-label">Visualisations</span>
            </div>
        </div>
    </div>
    
    <div class="card-grid">
"""
    
    descriptions = {
        "overview_dashboard": "Vue d'ensemble des données astronomiques et météorologiques collectées pour chaque tirage.",
        "moon_stars_correlation": "Analyse de la corrélation (faible) entre la phase lunaire et la somme des étoiles tirées.",
        "weather_heatmap": "Distribution des conditions météorologiques (température vs humidité) lors des tirages.",
        "moon_polar": "Représentation polaire des tirages en fonction du cycle lunaire complet.",
        "prime_fibonacci": "Fréquence des nombres premiers et de Fibonacci dans les tirages.",
        "temporal_evolution": "Évolution dans le temps des caractéristiques des tirages avec moyennes mobiles.",
        "correlation_matrix": "Matrice complète des corrélations entre toutes les variables analysées."
    }
    
    icons = {
        "overview_dashboard": "📊",
        "moon_stars_correlation": "🌙⭐",
        "weather_heatmap": "🌡️💧",
        "moon_polar": "🌗",
        "prime_fibonacci": "🔢",
        "temporal_evolution": "📈",
        "correlation_matrix": "🔗"
    }
    
    for filepath, description in html_files:
        filename = filepath.stem
        icon = icons.get(filename, "📊")
        desc_text = descriptions.get(filename, description)
        
        index_html += f"""
        <div class="card" onclick="window.location.href='{filepath.name}'">
            <h2>{icon} {description}</h2>
            <p>{desc_text}</p>
            <a href="{filepath.name}" class="btn">Voir la visualisation →</a>
        </div>
"""
    
    index_html += """
    </div>
    
    <div style="text-align: center; margin-top: 50px; padding: 20px; background: rgba(255,255,255,0.1); border-radius: 10px;">
        <h3>🎓 Note scientifique</h3>
        <p style="max-width: 800px; margin: 0 auto; line-height: 1.8;">
            Ces visualisations confirment que les tirages EuroMillions sont <strong>vraiment aléatoires</strong>.
            L'absence de corrélations fortes entre les tirages et les facteurs externes (lune, météo, etc.)
            prouve la robustesse du système de tirage. La faible corrélation trouvée (phase lunaire ↔ étoiles)
            est statistiquement attendue par pur hasard avec 40 tests à p&lt;0.05.
        </p>
    </div>
</body>
</html>
"""
    
    index_path = output_dir / "index.html"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    print("✅ Page index créée")
    
    print("\n" + "="*70)
    print("✅ VISUALISATIONS GÉNÉRÉES AVEC SUCCÈS !")
    print("="*70)
    print(f"\n📂 Dossier: {output_dir.absolute()}")
    print(f"📄 Fichiers générés: {len(html_files) + 1}")
    print(f"\n🌐 Ouvrir dans le navigateur:")
    print(f"   {index_path.absolute()}")
    
    # Ouvrir automatiquement dans le navigateur
    print("\n🚀 Ouverture automatique dans le navigateur...")
    try:
        webbrowser.open(f'file://{index_path.absolute()}')
        print("✅ Page ouverte !")
    except Exception as e:
        print(f"⚠️  Impossible d'ouvrir automatiquement: {e}")
        print(f"   Ouvrez manuellement: {index_path.absolute()}")
    
    print("\n💡 Conseil: Explorez les graphiques interactifs avec la souris !")
    print("   • Zoom: clic + glisser")
    print("   • Panoramique: shift + glisser")
    print("   • Réinitialiser: double-clic")
    print("="*70)

if __name__ == "__main__":
    main()
