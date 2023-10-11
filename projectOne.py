import csv

def find_ranges(numbers):
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

# Parsing data from Xytech file
def parse_xytech(xytech_data):
    capture_notes = False
    parsed_data = {"Notes": []}

    for line in xytech_data:
        line = line.strip()

        # Save names and such
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

# Reading Xytech data
with open('Xytech.txt', 'r') as file:
    xytech_data = file.readlines()

parsed_xytech = parse_xytech(xytech_data)

# Initialize locations
locations = []

# Reading Baselight data
with open('Baselight_export.txt', 'r') as file:
    baselight_data = file.readlines()

current_location = ""
current_numbers = []

# Process Baselight data
for line in baselight_data:
    line = line.strip()
    
    if line.startswith("/baselightfilesystem1"):
        if current_location and current_numbers:
            locations.extend([[current_location, s_e] for s_e in find_ranges(current_numbers)])
        
        path, *number_strings = line.split()
        current_location = path.replace("/baselightfilesystem1", "/hpsans13/production")
        current_numbers = [int(n) for n in number_strings if n.isnumeric()]
    else:
        current_numbers.extend([int(n) for n in line.split() if n.isnumeric()])

if current_location and current_numbers:
    locations.extend([[current_location, s_e] for s_e in find_ranges(current_numbers)])

# Export data to CSV file
with open('output.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)

    # Write line 1 with actual information
    writer.writerow([parsed_xytech["Producer"], parsed_xytech["Operator"], parsed_xytech["Job"], parsed_xytech["Notes"]])
    # Write empty lines
    writer.writerow([])
    writer.writerow([])

    # Write lines 4 onward with location and numbers
    for location, (start, end) in locations:
        frame_range = f"{start}-{end}" if start != end else f"{start}"
        writer.writerow([f"{location} {frame_range}"])

print("Data exported to 'output.csv'")
