import json
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import messagebox

# Load the JSON file
file_path = "universedata.json"
with open(file_path, "r") as file:
    data = json.load(file)

# Define colors for celestial bodies
object_colors = {
    "Red": "red",
    "Yellow": "yellow",
    "Orange": "orange",
    "Blue": "blue",
    "Neutron": "cyan",
    "BlackHole": "black"
}

# Define planet colors
planet_colors = {
    "Terra": "green",
    "Ocean": "blue",
    "Barren": "lightgray",
    "Tundra": "cyan",
    "Gas": "purple",
    "Exotic": "pink",
    "Desert": "orange",
    "Forest": "darkgreen",
    "Earthlike": "lime",
    "RobotFactory": "maroon",
    "RobotDepot": "red"
}

# Extract celestial objects
stars = []
black_holes = []
star_map = {}

for coords, details in data.items():
    coord_tuple = tuple(map(int, coords.split(", ")))
    x, y = coord_tuple[:2]

    if details.get("Type") == "Star":
        star_type = details.get("SubType", "White")
        color = object_colors.get(star_type, "gray")
        stars.append((x, y, color, star_type))
        star_map[(x, y)] = (coord_tuple, star_type)

    elif details.get("Type") == "BlackHole":
        black_holes.append((x, y))
        star_map[(x, y)] = (coord_tuple, "BlackHole")

# Plot Star Map
fig, ax = plt.subplots(figsize=(10, 10))

for x, y, color, _ in stars:
    ax.scatter(x, y, color=color, edgecolors="black", s=40, marker="o")

for x, y in black_holes:
    ax.scatter(x, y, color="black", edgecolors="white", s=40, marker="X")

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_title("Map")
ax.grid(True)

def plot_planets(event):
    if event.inaxes is None:
        return
    
    click_x, click_y = event.xdata, event.ydata
    min_dist = float("inf")
    selected_system = None

    for x, y, _, star_type in stars + [(x, y, "black", "BlackHole") for x, y in black_holes]:
        dist = np.sqrt((x - click_x) ** 2 + (y - click_y) ** 2)
        if dist < min_dist:
            min_dist = dist
            selected_system = (x, y, star_type)

    if selected_system and selected_system[:2] in star_map:
        system_coords, star_type = star_map[selected_system[:2]]
        show_planets(system_coords, star_type)

def show_planets(system_coords, star_type):
    planets = []
    planet_positions = {}

    for coords, details in data.items():
        coord_tuple = tuple(map(int, coords.split(", ")))

        if details.get("Type") == "Planet" and coord_tuple[:2] == system_coords[:2]:
            _, _, z, w = coord_tuple
            planet_type = details.get("SubType", "Unknown")
            color = planet_colors.get(planet_type, "gray")
            planets.append((z, w, color, planet_type, details, coord_tuple))
            planet_positions[(z, w)] = (details, coord_tuple)

    fig2, ax2 = plt.subplots(figsize=(8, 8))
    legend_labels = {}

    if star_type == "BlackHole":
        ax2.scatter(0, 0, color="black", s=200, marker="X", edgecolors="white", label="Black Hole")
    else:
        ax2.scatter(0, 0, color=object_colors.get(star_type, "gray"), s=200, marker="o", edgecolors="black", label=f"Star ({star_type})")

    for z, w, color, planet_type, details, coord_tuple in planets:
        ax2.scatter(z, w, color=color, s=100, edgecolors="black")

        if planet_type not in legend_labels:
            legend_labels[planet_type] = plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=color, markersize=10, label=planet_type)

    ax2.legend(handles=list(legend_labels.values()), title="Planet Types")
    ax2.set_title(f"System | {system_coords[:2]}")
    ax2.grid(True)

    def copy_to_clipboard(text):
        """Copies text to clipboard without a popup."""
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        root.destroy()

    def show_details(details, full_coords):
        """Opens a popup showing planet details."""
        info = f"Planet Name: {details.get('Name', 'Unknown Planet')}\n"
        info += f"Coordinates: ({', '.join(map(str, full_coords))}\n)"
        
        info += "\n".join(f"{key}: {value}" for key, value in details.items() if key not in ['Name', 'Materials'])

        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Planet Details:", info)

    def on_click(event):
        """Handles click events on planets and the star/black hole."""
        click_x, click_y = event.xdata, event.ydata
        min_dist = float("inf")
        selected_item = None

        # Click on the star or black hole
        if np.sqrt(click_x ** 2 + click_y ** 2) < 1.5:
            coordinates = ", ".join(map(str, system_coords[:2]))
            copy_to_clipboard(f"{coordinates}, 0, 0, false")
            return

        # Click on a planet
        for (z, w), (details, full_coords) in planet_positions.items():
            dist = np.sqrt((z - click_x) ** 2 + (w - click_y) ** 2)
            if dist < min_dist:
                min_dist = dist
                selected_item = (details, full_coords)

        if selected_item:
            details, full_coords = selected_item
            copy_to_clipboard(f"{", ".join(map(str, full_coords))}, true")
            show_details(details, full_coords)

    # Hover to Show Planet Name + Full Coordinates
    def hover(event):
        if event.inaxes is None:
            return
        
        hover_x, hover_y = event.xdata, event.ydata
        min_dist = float("inf")
        hovered_planet = None

        for (z, w), (details, full_coords) in planet_positions.items():
            dist = np.sqrt((z - hover_x) ** 2 + (w - hover_y) ** 2)
            if dist < min_dist:
                min_dist = dist
                hovered_planet = (z, w, details.get("Name", "Unknown Planet"), full_coords)

        if hovered_planet and min_dist < 1.5:
            ax2.set_title(f"{hovered_planet[2]} | ({', '.join(map(str, hovered_planet[3]))}, true)")
        else:
            ax2.set_title(f"System | {system_coords[:2]}")
        
        fig2.canvas.draw()

    fig2.canvas.mpl_connect("button_press_event", on_click)  # Click to copy & open details
    fig2.canvas.mpl_connect("motion_notify_event", hover)
    plt.show()

fig.canvas.mpl_connect("button_press_event", plot_planets)
plt.show()
