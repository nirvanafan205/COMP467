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

# return new path based on pathing
def find_mapping(path, mappings):
    parts = path.split("/")
    if len(parts) >= 2:
        checking = "/".join(parts[-2:])
        for keyPath, pathMap in mappings.items():
            if checking in keyPath:
                return pathMap + "/" + "/".join(parts[2:])
    return path

# returns range
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

# read xytech data file
# get producer, operator, job and notes info
def parse_xytech(xytech_data):
    notes = False
    parseData = {"Notes": []}

    for line in xytech_data:
        line = line.strip()
        if line.startswith("Producer:"):
            parseData["Producer"] = line[len("Producer:"):].strip()

        elif line.startswith("Operator:"):
            parseData["Operator"] = line[len("Operator:"):].strip()

        elif line.startswith("Job:"):
            parseData["Job"] = line[len("Job:"):].strip()

        elif line.startswith("Notes:") or line.startswith("Notes :"):
            notes = True

        elif notes:
            parseData["Notes"].append(line)
    parseData["Notes"] = ' '.join(parseData["Notes"]).strip()

    return parseData

# read data from xytech
# parse data
# get info
with open('Xytech.txt', 'r') as file:
    xytech_data = file.readlines()
parsed_xytech = parse_xytech(xytech_data)

# store paths and ranges from baselight
locations = []
with open('Baselight_export.txt', 'r') as file:
    baselight_data = file.readlines()

# track current location
currLocation = ""

# hold current list of frame numbers
currNums = []

# loop baselight data
for line in baselight_data:
    line = line.strip() # remove leading and trailing whitespaces

    # check if it starts with specific string 
    if line.startswith("/baselightfilesystem1"):

        # find range and store it in location
        if currLocation and currNums:
            locations.extend([[currLocation, s_e] for s_e in range(currNums)])
        
        # spllit line, map, and convert nums
        path, *number_strings = line.split()
        currLocation = find_mapping(path, mapping_dict)  # use mapping
        currNums = [int(n) for n in number_strings if n.isnumeric()]

    # contain additional frame numbers
    else:
        currNums.extend([int(n) for n in line.split() if n.isnumeric()])

if currLocation and currNums:
    locations.extend([[currLocation, s_e] for s_e in range(currNums)])

    # opens output.csv for writing 
with open('output.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow([parsed_xytech["Producer"], parsed_xytech["Operator"], parsed_xytech["Job"], parsed_xytech["Notes"]])
    # blanks
    writer.writerow([])
    writer.writerow([])

    # for locations and respective ranges
    for location, (start, end) in locations:
        frame_range = f"{start}-{end}" if start != end else f"{start}"
        writer.writerow([f"{location} {frame_range}"])

    # message to show it work
print("Data exported to 'output.csv'")