from geometry import create_building_mesh


def main():
    # Generate the 3D building
    building_mesh = create_building_mesh()

    # Display basic information
    print("=== 3D Building Result ===")
    print("Vertices:", len(building_mesh.vertices))
    print("Faces:", len(building_mesh.faces))
    print("Volume:", building_mesh.volume)
    print("Watertight:", building_mesh.is_watertight)

    building_mesh.export("data/synthetic/building.glb")
    print("3D model exported.")


if __name__ == "__main__":
    main()