import csv
import argparse
from pymongo import MongoClient
from datetime import datetime

# Initialize argument parser
parser = argparse.ArgumentParser(description="Process Baselight/Flames and Xytech files.")

# Add arguments to the parser
parser.add_argument("--files", help="Path to Baselight/Flames Text files", nargs='+', required=True)
parser.add_argument("--xytech", help="Path to Xytech file input", type=str, required=True)
parser.add_argument("--verbose", action="store_true", help="Enable console output")
parser.add_argument("--output", choices=["csv", "DB"], default="csv", help="Output format (csv or DB)")

# Parse the command-line arguments
args = parser.parse_args()

# mapping
mapping_dict = {
        # BBonds Baselight 
    "/images1/Avatar/reel1/partA/1920x1080": "/ddnsata3/production/Avatar/reel1/partA/1920x1080",
    "/images1/Avatar/reel1/partB/1920x1080": "/ddnsata5/production/Avatar/reel1/partB/1920x1080",
    "/images1/Avatar/pickups/shot_1ab/1920x1080": "/ddnsata6/production/Avatar/pickups/shot_1ab/1920x1080",

        # lopez Baselight 
    "/images1/Avatar/reel3/partA/1920x1080": "/ddnsata4/production/Avatar/reel3/partA/1920x1080",
    "/images1/Avatar/pickups/shot_3ab/1920x1080": "/ddnsata1/production/Avatar/pickups/shot_3ab/1920x1080",
    "/images1/Avatar/reel3/VFX/Hydraulx": "/ddnsata7/production/starwars/reel3/VFX/Hydraulx",
    "/images1/Avatar/reel3/partB/1920x1080": "/ddnsata9/production/Avatar/reel3/partB/1920x1080",

        #JJacobs baselight
    "/images1/Avatar/reel1/partA/1920x1080": "/ddnsata5/production/Avatar/reel1/partA/1920x1080",
    "/images1/Avatar/reel1/VFX/Hydraulx": "/ddnsata7/production/Avatar/reel1/VFX/Hydraulx",
    "/images1/Avatar/pickups/shot_1ab/1920x1080": "/ddnsata4/production/Avatar/pickups/shot_1ab/1920x1080",
    "/images1/Avatar/reel1/VFX/Framestore": "/ddnsata3/production/Avatar/reel1/VFX/Framestore",
    "/images1/Avatar/reel1/partB/1920x1080": "/ddnsata2/production/Avatar/reel1/partB/1920x1080",
    "/images1/Avatar/reel1/VFX/AnimalLogic": "/ddnsata9/production/Avatar/reel1/VFX/AnimalLogic",

        #TDanza baselight
    "/images1/Avatar/reel2/partA/1920x1080": "/ddnsata4/production/Avatar/reel2/partA/1920x1080",
    "/images1/Avatar/pickups/shot_2ab/1920x1080": "/ddnsata3/production/Avatar/pickups/shot_2ab/1920x1080",
    "/images1/Avatar/reel2/VFX/AnimalLogic": "/ddnsata9/production/Avatar/reel2/VFX/AnimalLogic",
    "/images1/Avatar/reel2/VFX/Hydraulx": "/ddnsata8/production/Avatar/reel2/VFX/Hydraulx",
    "/images1/Avatar/reel2/partB/1920x1080": "/ddnsata2/production/Avatar/reel2/partB/1920x1080",
    "/images1/Avatar/reel2/VFX/Framestore": "/ddnsata1/production/Avatar/reel2/VFX/Framestore",

        #THolland baselight
    "/images1/Avatar/reel5/partA/1920x1080": "/ddnsata2/production/Avatar/reel5/partA/1920x1080",
    "/images1/Avatar/reel5/VFX/Hydraulx": "/ddnsata9/production/Avatar/reel5/VFX/Hydraulx",
    "/images1/Avatar/reel5/VFX/Framestore": "/ddnsata5/production/Avatar/reel5/VFX/Framestore",
    "/images1/Avatar/pickups/shot_5ab/1920x1080": "/ddnsata11/production/Avatar/pickups/shot_5ab/1920x1080",
    "/images1/Avatar/reel5/VFX/AnimalLogic 3410": "/ddnsata1/production/Avatar/reel5/VFX/AnimalLogic",
    "/images1/Avatar/reel5/partB/1920x1080": "/ddnsata6/production/Avatar/reel5/partB/1920x1080",

        #BBonds Flame
    "/net/flame-archive Avatar/reel5/partB/1920x1080": "/ddnsata2/production/Avatar/reel5/partA/1920x1080",
    "/net/flame-archive Avatar/pickups/shot_5ab/1920x1080": "/ddnsata11/production/Avatar/pickups/shot_5ab/1920x1080",

        # DFlowers Flame
    "/net/flame-archive Avatar/reel1/VFX/Hydraulx": "/ddnsata7/production/Avatar/reel1/VFX/Hydraulx",
    "/net/flame-archive Avatar/reel1/VFX/AnimalLogic": "/ddnsata9/production/Avatar/reel1/VFX/AnimalLogic",

        #  MFelix Flame
    "/net/flame-archive Avatar/reel1/VFX/Framestore": "/ddnsata3/production/Avatar/reel1/VFX/Framestore",

        # DFlowers Flame 26
    "/net/flame-archive Avatar/reel1/partA/1920x1080": "/ddnsata3/production/Avatar/reel1/partA/1920x1080",
    "/net/flame-archive Avatar/reel1/partB/1920x1080": "/ddnsata5/production/Avatar/reel1/partB/1920x1080",
}

# Initialize MongoDB client and collection
client = MongoClient('mongodb://localhost:27017/')
db = client['magneto']
collection = db['insertTwo']
collection_namor = db['Namor']

# Insert data into db
def insert_into_mongo(collection, username, date, locations):
    for location, (start, end) in locations:
        frame_range = f"{start}-{end}" if start != end else f"{start}"

        data = {
            "User": username,
            "Date": date,
            "Location": location,
            "FrameRange": frame_range
        }

        # Inserting data into MongoDB
        collection.insert_one(data)

# insert data into the Namor collection
def insert_into_namor(collection, user, machine, file_user, file_date, submitted_date):
    data = {
        "User": user,
        "Machine": machine,
        "NameOfFileUser": file_user,
        "DateOfFile": file_date,
        "SubmittedDate": submitted_date
    }

    # Inserting data into the Namor collection
    collection.insert_one(data)

# Process Baselight files
def process_baselight_files(files):
    # Initialize locations list
    locations = []

    for file in files:
        currLocation = ""
        currNums = []

        with open(file, 'r') as file:
            baselight_data = file.readlines()

        # Loop through Baselight data
        for line in baselight_data:
            line = line.strip()

            if line.startswith("/images1/Avatar/"):
                if currLocation and currNums:
                    locations.extend([[currLocation, s_e] for s_e in range(currNums)])

                path, *number_strings = line.split()
                currLocation = find_mapping(path, mapping_dict)
                currNums = [int(n) for n in number_strings if n.isnumeric()]

            else:
                currNums.extend([int(n) for n in line.split() if n.isnumeric()])

        if currLocation and currNums:
            locations.extend([[currLocation, s_e] for s_e in range(currNums)])

    return locations

# Process Flame files
def process_flame_files(files):
    # Initialize locations list
    locations = []

    for file in files:
        currLocation = ""
        currNums = []

        with open(file, 'r') as file:
            flame_data = file.readlines()

        # Loop through Flame data (similar to Baselight processing)
        for line in flame_data:
            line = line.strip()

            if line.startswith("/net/flame-archive Avatar/"):
                if currLocation and currNums:
                    locations.extend([[currLocation, s_e] for s_e in range(currNums)])

                path, *number_strings = line.split()
                currLocation = find_mapping(path, mapping_dict)
                currNums = [int(n) for n in number_strings if n.isnumeric()]

            else:
                currNums.extend([int(n) for n in line.split() if n.isnumeric()])

        if currLocation and currNums:
            locations.extend([[currLocation, s_e] for s_e in range(currNums)])

    return locations

# Return new path based on mapping
def find_mapping(path, mappings):
    parts = path.split("/")
    if len(parts) >= 2:
        checking = "/".join(parts[-2:])
        for keyPath, pathMap in mappings.items():
            if checking in keyPath:
                return pathMap + "/" + "/".join(parts[2:])
    return path

# Returns a list of frame ranges from a list of frame numbers
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

def extract_user_and_date(file_name):
    parts = file_name.split('_')
    if len(parts) >= 3:
        user = parts[1]
        date = parts[2].split('.')[0]  # Remove file extension if present
        return user, date
    return None, None

# Read xytech data file and parse information
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

# Read data from xytech, parse it, and get information
with open(args.xytech, 'r') as file:
    xytech_data = file.readlines()
parsed_xytech = parse_xytech(xytech_data)

date = parsed_xytech.get("Date", "Unknown Date")

# Process Baselight files
baselight_locations = process_baselight_files(args.files)

# Process Flame files
flame_locations = process_flame_files(args.files)

# Process Baselight files
for baselight_file in args.files:
    if "Baselight_" in baselight_file:
        user, date = extract_user_and_date(baselight_file)
        if user and date:
            baselight_locations = process_baselight_files([baselight_file])
            insert_into_mongo(collection, user, date, baselight_locations)

# Process Flame files
for flame_file in args.files:
    if "Flame_" in flame_file:
        user, date = extract_user_and_date(flame_file)
        if user and date:
            flame_locations = process_flame_files([flame_file])
            insert_into_mongo(collection, user, date, flame_locations)

# Get the current date in the specified format
submitted_date = datetime.now().strftime("%m-%d-%Y")

# Insert data into the Namor collection for Baselight files
for baselight_file in args.files:
    if "Baselight_" in baselight_file:
        user, date = extract_user_and_date(baselight_file)
        if user and date:
            insert_into_namor(collection_namor, "Matthew", "Baselight", user, date, submitted_date)

# Insert data into the Namor collection for Flame files
for flame_file in args.files:
    if "Flame_" in flame_file:
        user, date = extract_user_and_date(flame_file)
        if user and date:
            insert_into_namor(collection_namor, "Matthew", "Flame", user, date, submitted_date)

if args.verbose:
    print("Data inserted into MongoDB")

    # Query the Namor collection for distinct Autodesk Flame users
distinct_users = collection_namor.distinct("NameOfFileUser", {"Machine": "Flame"})

# Print the list of distinct Autodesk Flame users
print("Autodesk Flame Users:")
for user in distinct_users:
    print(user)