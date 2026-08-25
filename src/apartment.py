from shapely.geometry import shape, box
from floor import generate_floors
import trimesh
import json

APARTMENT_COLORS = [
    [255, 80, 80, 255],     # Red
    [80, 150, 255, 255],    # Blue
    [80, 200, 120, 255],    # Green
    [255, 190, 70, 255]     # Yellow
]

def create_apartments():

    # Load building data
    with open("data/synthetic/building.json", "r") as f:
        geojson_data = json.load(f)

    footprint = geojson_data["parcel"]["building"]["footprint"]

    building = shape(footprint)

    # Building bounds
    min_x, min_y, max_x, max_y = building.bounds

    mid_x = (min_x + max_x) / 2
    mid_y = (min_y + max_y) / 2

    # Four candidate apartment regions
    regions = [
        box(min_x, min_y, mid_x, mid_y),
        box(mid_x, min_y, max_x, mid_y),
        box(min_x, mid_y, mid_x, max_y),
        box(mid_x, mid_y, max_x, max_y)
    ]

    apartments = []

    height = geojson_data['parcel']['building']['height_m']
    number_of_floors = geojson_data['parcel']['building']['floors']

    floor_generating = generate_floors(
        height=height,
        number_of_floors=number_of_floors
    )

    for floor in floor_generating:
        z_min = floor['z_min']
        z_max = floor['z_max']

        for i, region in enumerate(regions):

            apartment = building.intersection(region)

            if apartment.is_empty or apartment.area <= 0:
                continue

            coordinates = list(apartment.exterior.coords)[:-1]

            vertices = []

            # Bottom + top vertices
            for x, y in coordinates:
                vertices.append([x, y, z_min])
                vertices.append([x, y, z_max])

            faces = []

            n = len(coordinates)

            # Bottom surface
            for j in range(1, n - 1):
                faces.append([0, 2 * (j + 1), 2 * j])

            # Top surface
            for j in range(1, n - 1):
                faces.append([1, 2 * j + 1, 2 * (j + 1) + 1])

            # Side walls
            for j in range(n):

                next_j = (j + 1) % n

                bottom_current = 2 * j
                top_current = 2 * j + 1

                bottom_next = 2 * next_j
                top_next = 2 * next_j + 1

                faces.append([
                    bottom_current,
                    bottom_next,
                    top_next
                ])

                faces.append([
                    bottom_current,
                    top_next,
                    top_current
                ])

            mesh = trimesh.Trimesh(
                vertices=vertices,
                faces=faces,
                process=True
            )

            mesh.fix_normals()

            color = APARTMENT_COLORS[i]
            mesh.visual.face_colors = color

            unit_id = f"B001-F{floor['floor_number']:02d}-U{i + 1:02d}"
            print("\n", unit_id)
            print("Area:", apartment.area)
            print("Height:", z_max - z_min)
            print("Volume:", mesh.volume)
            print("Watertight:", mesh.is_watertight)

            apartments.append({
                "id": unit_id,
                "footprint": apartment,
                "mesh": mesh,
                "metadata": {
                    "property_id": unit_id,
                    "building_id": "B001",
                    "floor": floor["floor_number"],
                    "unit": i + 1,
                    "area": apartment.area,
                    "height": z_max - z_min,
                    "volume": mesh.volume,
                    "watertight": mesh.is_watertight,
                    "geometry_valid": apartment.is_valid
                }
            })

    return apartments


if __name__ == "__main__":
    apartments = create_apartments()

    # Combined scene — kept for the existing GLTF debug viewer workflow.
    scene = trimesh.Scene()

    for apartment in apartments:
        scene.add_geometry(
            apartment["mesh"],
            geom_name=apartment["id"]
        )

    scene.export("data/synthetic/apartments.glb")

    # Individual per-apartment GLBs + a metadata mapping, for the CesiumJS
    # viewer: each unit is loaded as its own pickable/highlightable Cesium
    # entity, and its property_id is used to look up metadata.json below.
    # This is additive — it doesn't change the combined export above.
    import os

    units_dir = "data/synthetic/apartments"
    os.makedirs(units_dir, exist_ok=True)

    metadata = {}

    for apartment in apartments:
        apartment["mesh"].export(f"{units_dir}/{apartment['id']}.glb")
        metadata[apartment["id"]] = apartment["metadata"]

    with open("data/synthetic/apartments_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print("\nTotal apartments:", len(apartments))
    print("GLB exported: data/synthetic/apartments.glb")
    print(f"Individual GLBs exported: {units_dir}/<unit_id>.glb")
    print("Metadata exported: data/synthetic/apartments_metadata.json")