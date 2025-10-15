import requests
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# NASA API Key (kostenlos registrierbar unter https://api.nasa.gov/)
NASA_API_KEY = "yvKFIZFvNJtX7KkHd8OTAbDv8OphAYhg5Vmbgm8i"

def getAsteroidData(start_date, end_date):
    """Holt Asteroidendaten von der NASA API"""
    url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={NASA_API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen der Daten: {e}")
        return None

def extractInfo(data):
    """Extrahiert relevante Informationen aus den NASA-Daten"""
    asteroids = []
    
    for date, neos in data["near_earth_objects"].items():
        for neo in neos:
            # Hauptinformationen
            name = neo["name"]
            diameter_min = neo["estimated_diameter"]["meters"]["estimated_diameter_min"]
            diameter_max = neo["estimated_diameter"]["meters"]["estimated_diameter_max"]
            hazardous = neo["is_potentially_hazardous_asteroid"]
            
            # Close Approach Data - nimm den ersten Eintrag
            close_approach_data = neo["close_approach_data"][0]
            velocity_kmh = float(close_approach_data["relative_velocity"]["kilometers_per_hour"])
            distance_km = float(close_approach_data["miss_distance"]["kilometers"])
            
            asteroids.append({
                "name": name,
                "distance_km": distance_km,
                "diameter": (diameter_min + diameter_max) / 2,  # Durchschnittlicher Durchmesser
                "velocity": velocity_kmh,
                "date": date,
                "hazardous": hazardous,
                "diameter_min": diameter_min,
                "diameter_max": diameter_max
            })
    
    return asteroids

def randomSpherePoint(r):
    """Generiert zufällige Koordinaten auf einer Kugel mit Radius r"""
    theta = np.random.uniform(0, 2*np.pi)   # Winkel in der xy-Ebene
    phi = np.random.uniform(0, np.pi)       # Winkel von der z-Achse
    x = r * np.sin(phi) * np.cos(theta)
    y = r * np.sin(phi) * np.sin(theta)
    z = r * np.cos(phi)
    return x, y, z

def visualize3D(asteroids_data):
    """Erstellt die 3D-Visualisierung der Asteroiden"""
    if not asteroids_data:
        print("Keine Asteroidendaten verfügbar")
        return
    
    df = pd.DataFrame(asteroids_data)
    
    # Koordinaten für die Asteroiden generieren
    coords = [randomSpherePoint(d) for d in df["distance_km"]]
    df["x"], df["y"], df["z"] = zip(*coords)
    
    # Farbe basierend auf Gefährlichkeit
    colors = ["red" if hazardous else "orange" for hazardous in df["hazardous"]]
    
    # Größe basierend auf Durchmesser (skaliert für bessere Darstellung)
    sizes = [min(max(d/10, 3), 15) for d in df["diameter"]]
    
    # Erde im Ursprung
    earth = go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode="markers",
        marker=dict(size=12, color="blue", opacity=0.8),
        name="Earth",
        hovertext="Earth",
        hoverinfo="text"
    )
    
    # Asteroiden
    asteroids = go.Scatter3d(
        x=df["x"], y=df["y"], z=df["z"],
        mode="markers",
        marker=dict(
            size=sizes,
            color=colors,
            opacity=0.7,
            line=dict(width=2, color="darkgray")
        ),
        name="Asteroids",
        hovertext=[
            f"Name: {row['name']}<br>"
            f"Distanz: {row['distance_km']:,.0f} km<br>"
            f"Durchmesser: {row['diameter_min']:.1f} - {row['diameter_max']:.1f} m<br>"
            f"Geschwindigkeit: {row['velocity']:,.0f} km/h<br>"
            f"Datum: {row['date']}<br>"
            f"Gefährlich: {'Ja' if row['hazardous'] else 'Nein'}"
            for _, row in df.iterrows()
        ],
        hoverinfo="text"
    )
    
    # Layout
    layout = go.Layout(
    title=f"Near-Earth Asteroids ({len(asteroids_data)} Objekte)",
    scene=dict(
        xaxis_title="X (km)",
        yaxis_title="Y (km)",
        zaxis_title="Z (km)",
        zaxis_title_font_color="white",
        xaxis=dict(backgroundcolor="black", gridcolor="gray", zerolinecolor="gray", color="white"),
        yaxis=dict(backgroundcolor="black", gridcolor="gray", zerolinecolor="gray", color="white"),
        zaxis=dict(backgroundcolor="black", gridcolor="gray", zerolinecolor="gray", color="white"),
        camera=dict(
            eye=dict(x=1.5, y=1.5, z=1.5)
        )
    ),
    paper_bgcolor="black",   # Gesamter Hintergrund
    plot_bgcolor="black",    # Plot-Bereich
    font=dict(color="white"),  # Alle Texte weiß
    showlegend=True
)

    
    fig = go.Figure(data=[earth, asteroids], layout=layout)
    fig.show()

def main():
    """Hauptfunktion für die Benutzerinteraktion"""
    print("=== NASA Near-Earth Asteroid Visualizer ===")
    
    # Datumseingabe
    start_date = input("Startdatum (YYYY-MM-DD, Enter für heute): ").strip()
    end_date = input("Enddatum (YYYY-MM-DD, Enter für +7 Tage): ").strip()
    
    # Standardwerte falls leer
    if not start_date:
        start_date = datetime.now().strftime("%Y-%m-%d")
    if not end_date:
        end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    print(f"\nLade Daten für {start_date} bis {end_date}...")
    
    # Daten von NASA API abrufen
    data = getAsteroidData(start_date, end_date)
    
    if data is None:
        print("Konnte keine Daten laden. Bitte API-Key und Datenformat überprüfen.")
        return
    
    # Asteroideninformationen extrahieren
    asteroids = extractInfo(data)
    
    if not asteroids:
        print("Keine Asteroiden im angegebenen Zeitraum gefunden.")
        return
    
    print(f"\nGefunden: {len(asteroids)} Asteroiden")
    print(f"Davon potentiell gefährlich: {sum(1 for a in asteroids if a['hazardous'])}")
    
    # 3D-Visualisierung erstellen
    print("\nErstelle 3D-Visualisierung...")
    visualize3D(asteroids)

if __name__ == "__main__":
    main()