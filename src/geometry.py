from shapely.geometry import shape
import trimesh
import json 

def create_building_mesh():

    with open("data/synthetic/building.json", 'r') as f:
        geojson_data = json.load(f)

    footprint = geojson_data["parcel"]["building"]["footprint"]
    height = geojson_data["parcel"]["building"]["height_m"]

    poly = shape(footprint)

    coordinates = list(poly.exterior.coords)[:-1]

    vertices = []
    for x, y in coordinates:
        vertices.append([x, y, 0])
        vertices.append([x, y, height])

    faces = []

    n = len(coordinates)

    # Bottom and top suyrfaces
    for i in range(1, n - 1):
        faces.append([0, 2 * (i + 1), 2 * i])
        faces.append([1, 2 * i + 1, 2 * (i + 1) + 1])

    # Side walls
    for i in range(n):
        next_i = (i + 1) % n

        bottom_current = 2 * i
        top_current = 2 * i + 1

        bottom_next = 2 * next_i
        top_next = 2 * next_i + 1

        faces.append([bottom_current, bottom_next, top_next])
        faces.append([bottom_current, top_next, top_current])

    mesh = trimesh.Trimesh(
        vertices=vertices,
        faces=faces
    )

    return mesh 

building_mesh = create_building_mesh()
print(type(building_mesh))