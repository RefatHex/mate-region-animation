import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk
import pandas as pd
import json
import os

def get_coordinates(image_path, area_name):
    coordinates = []

    def on_click(event):
        """Handles mouse click events to collect coordinates."""
        scale_x = original_width / resized_width
        scale_y = original_height / resized_height
        scaled_x = int(event.x * scale_x)
        scaled_y = int(event.y * scale_y)

        coordinates.append((scaled_x, scaled_y))
        print(f"{area_name} - Scaled Coordinate added: ({scaled_x}, {scaled_y})")
        canvas.create_oval(event.x - 2, event.y - 2, event.x + 2, event.y + 2, fill="red")

    def save_coordinates():
        """Saves the coordinates to a JSON file."""
        with open(f"{area_name}_coordinates.json", "w") as f:
            json.dump(coordinates, f)
        print(f"Coordinates for {area_name} saved.")
        root.destroy()  

    image = Image.open(image_path)
    global original_width, original_height
    original_width, original_height = image.size

    max_size = (800, 600)
    image.thumbnail(max_size)
    global resized_width, resized_height
    resized_width, resized_height = image.size

    root = tk.Tk()
    root.title(f"Click to Mark Coordinates for {area_name}")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)
    photo = ImageTk.PhotoImage(image)
    canvas = tk.Canvas(root, width=resized_width, height=resized_height)
    canvas.pack()
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)
    canvas.bind("<Button-1>", on_click)

    save_button = tk.Button(root, text="Save Coordinates", command=save_coordinates)
    save_button.pack()

    root.mainloop()
    return coordinates

def load_or_get_coordinates(base_map_path, areas):
    regions_coordinates = {}
    for area in areas:
        json_path = f"{area}_coordinates.json"
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                regions_coordinates[area] = [tuple(map(int, coord)) for coord in json.load(f)]
        else:
            print(f"Collecting coordinates for {area}")
            regions_coordinates[area] = get_coordinates(base_map_path, area)
    return regions_coordinates


base_map_path = "Location-of-the-Illinois-River-basin_W640.jpg"
if not os.path.exists(base_map_path):
    raise FileNotFoundError(f"Base map not found at {base_map_path}")

base_map = Image.open(base_map_path)

area_colors = {
    "Area 1 - Mississippi River to Saginaw River": "blue",
    "Area 2 - Saginaw River to Mackinac River": "green",
    "Area 3 - Mackinac River to Vermillion River": "orange",
    "Area 4 - Vermillion River to Lake Michigan": "purple",
    "Area 5 - Lake Michigan": "brown",
}

regions_coordinates = load_or_get_coordinates(base_map_path, area_colors)

csv_path = "river_areas_dataset.csv"
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"CSV file not found at {csv_path}")

df = pd.read_csv(csv_path)

frames = []
for index, row in df.iterrows():
    year = row["Year"]
    current_map = base_map.copy()
    draw = ImageDraw.Draw(current_map)

    for area, status in row.items():
        if area.startswith("Area") and status == "Y":
            if area in regions_coordinates and len(regions_coordinates[area]) > 1:
                color = area_colors.get(area, "red") 
                for i in range(len(regions_coordinates[area]) - 1):
                    draw.line(
                        [regions_coordinates[area][i], regions_coordinates[area][i + 1]],
                        fill=color,
                        width=5,
                    )

    try:
        font = ImageFont.truetype("arialbd.ttf", 40) 
    except IOError:
        font = None  
    draw.text((50, 50), f"Year: {year}", fill="black", font=font)

    frames.append(current_map)

if frames:
    output_path = "river_regions_animation2.gif"
    frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=1000, loop=0)
    print(f"Animation saved as {output_path}")
else:
    print("No frames to save.")
