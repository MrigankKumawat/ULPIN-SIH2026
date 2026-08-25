def generate_floors(height, number_of_floors):
    floor_height = height/number_of_floors

    floors = []

    for i in range(number_of_floors):
        floor = {
            "floor_number":i + 1,
            "z_min":i * floor_height,
            "z_max":(i + 1) * floor_height
        }

        floors.append(floor)

    return floors

