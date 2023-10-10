import csv

# Initialize names of what you need to save
producer = ""
operator = ""
job = ""
notes = ""
locations = []

# Open the input file in read mode
with open('Xytech.txt', 'r') as file:
    xytech_data = file.readlines()

# Parsing data from Xytech file
capture_notes = False  # Flag to capture notes

for line in xytech_data:
    line = line.strip()

    # Save names and such
    if line.startswith("Producer:"):
        producer = line[len("Producer:"):].strip()
    elif line.startswith("Operator:"):
        operator = line[len("Operator:"):].strip()
    elif line.startswith("Job:"):
        job = line[len("Job:"):].strip()
    elif line.startswith("Notes:") or line.startswith("Notes :"):
        # Start capturing notes
        capture_notes = True
        notes = []  # Initialize notes as a list
    elif capture_notes:
        # Capture all lines after "Notes:" (including leading spaces)
        notes.append(line)

# Makes notes a single string
notes = ' '.join(notes).strip()

# Open the Baselight file in read mode
with open('Baselight_export.txt', 'r') as file:
    baselight_data = file.readlines()

# Initialize a variable to store the current location and numbers
current_location = ""
current_numbers = []

# Process Baselight data
for line in baselight_data:
    line = line.strip()
    
    if line.startswith("/baselightfilesystem1"):
        # Store the current location and numbers
        if current_location:
            locations.append([current_location, ' '.join(current_numbers)])
        
        # Set the current location
        current_location = line.replace("/baselightfilesystem1", "/hpsans13/production")
        current_numbers = []
    else:
        # Append numbers to the current_numbers list
        current_numbers.extend(line.split())

# Append the last location and numbers
if current_location:
    locations.append([current_location, ' '.join(current_numbers)])

# Export data to CSV file
with open('output.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)

    # Write line 1 with actual information
    writer.writerow([producer, operator, job, notes])
    # Write empty lines
    writer.writerow([])
    writer.writerow([])

    # Write lines 4 onward with location and numbers in separate cells
    writer.writerows(locations)

print("Data exported to 'output.csv'")
