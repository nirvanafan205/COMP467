import csv

# mapping
mapping_dict = {
    "reel1/partA/1920x1080": "/hpsans13/production",
    "reel1/VFX/Hydraulx": "/hpsans12/production",
    "reel1/VFX/Framestore": "/hpsans13/production",
    "reel1/VFX/AnimalLogic": "/hpsans14/production",
    "reel1/partB/1920x1080": "/hpsans13/production",
    "pickups/shot_1ab/1920x1080": "/hpsans15/production",
    "pickups/shot_2b/1920x1080": "/hpsans11/production",
    "reel1/partC/1920x1080": "/hpsans17/production",
}

def find_mapping(path, mappings):
    path_parts = path.split("/")
    if len(path_parts) >= 2:
        check_path = "/".join(path_parts[-2:])
        for key_path, mapped_path in mappings.items():
            if check_path in key_path:
                return mapped_path + "/" + "/".join(path_parts[2:])
    return path

def range(numbers):
    ranges = []
    start = end = numbers[0]

    for n in numbers[1:]:
        if n == end + 1:
            end = n
        else:
            ranges.append((start, end))
            start = end = n
    ranges.append((start, end))
    return [(s, e) for s, e in ranges]

def parse_xytech(xytech_data):
    capture_notes = False
    parsed_data = {"Notes": []}

    for line in xytech_data:
        line = line.strip()
        if line.startswith("Producer:"):
            parsed_data["Producer"] = line[len("Producer:"):].strip()

        elif line.startswith("Operator:"):
            parsed_data["Operator"] = line[len("Operator:"):].strip()

        elif line.startswith("Job:"):
            parsed_data["Job"] = line[len("Job:"):].strip()

        elif line.startswith("Notes:") or line.startswith("Notes :"):
            capture_notes = True

        elif capture_notes:
            parsed_data["Notes"].append(line)
    parsed_data["Notes"] = ' '.join(parsed_data["Notes"]).strip()

    return parsed_data

with open('Xytech.txt', 'r') as file:
    xytech_data = file.readlines()
parsed_xytech = parse_xytech(xytech_data)

locations = []
with open('Baselight_export.txt', 'r') as file:
    baselight_data = file.readlines()

current_location = ""
current_numbers = []

for line in baselight_data:
    line = line.strip()

    if line.startswith("/baselightfilesystem1"):

        if current_location and current_numbers:
            locations.extend([[current_location, s_e] for s_e in range(current_numbers)])
        
        path, *number_strings = line.split()
        current_location = find_mapping(path, mapping_dict)  # use mapping
        current_numbers = [int(n) for n in number_strings if n.isnumeric()]

    else:
        current_numbers.extend([int(n) for n in line.split() if n.isnumeric()])

if current_location and current_numbers:
    locations.extend([[current_location, s_e] for s_e in range(current_numbers)])

with open('output.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow([parsed_xytech["Producer"], parsed_xytech["Operator"], parsed_xytech["Job"], parsed_xytech["Notes"]])
    writer.writerow([])
    writer.writerow([])

    for location, (start, end) in locations:
        frame_range = f"{start}-{end}" if start != end else f"{start}"
        writer.writerow([f"{location} {frame_range}"])

print("Data exported to 'output.csv'")
