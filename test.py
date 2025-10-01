import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Example asteroid data with just distance
data = [
    {"name": "Asteroid A", "distance_km": 1500000, "diameter": 120, "velocity": 23000, "date": "2025-10-01"},
    {"name": "Asteroid B", "distance_km": 500000, "diameter": 340, "velocity": 18000, "date": "2025-10-02"},
    {"name": "Asteroid C", "distance_km": 2300000, "diameter": 50, "velocity": 27000, "date": "2025-10-03"}
]

df = pd.DataFrame(data)

# Convert distance into random spherical coordinates
def random_point_on_sphere(r):
    theta = np.random.uniform(0, 2*np.pi)   # angle in xy-plane
    phi = np.random.uniform(0, np.pi)       # angle from z-axis
    x = r * np.sin(phi) * np.cos(theta)
    y = r * np.sin(phi) * np.sin(theta)
    z = r * np.cos(phi)
    return x, y, z

coords = [random_point_on_sphere(d) for d in df["distance_km"]]
df["x"], df["y"], df["z"] = zip(*coords)

# Earth at origin
earth = go.Scatter3d(
    x=[0], y=[0], z=[0],
    mode="markers",
    marker=dict(size=8, color="blue"),
    name="Earth",
    hovertext="Earth"
)

# Asteroids
asteroids = go.Scatter3d(
    x=df["x"], y=df["y"], z=df["z"],
    mode="markers",
    marker=dict(size=5, color="red"),
    name="Asteroids",
    hovertext=[
        f"Name: {row['name']}<br>"
        f"Distance: {row['distance_km']:,} km<br>"
        f"Diameter: {row['diameter']} m<br>"
        f"Velocity: {row['velocity']} km/h<br>"
        f"Date: {row['date']}"
        for _, row in df.iterrows()
    ],
    hoverinfo="text"
)

layout = go.Layout(
    title="Near-Earth Asteroids (approx. positions)",
    scene=dict(
        xaxis_title="X (km)",
        yaxis_title="Y (km)",
        zaxis_title="Z (km)"
    )
)

fig = go.Figure(data=[earth, asteroids], layout=layout)
fig.show()
