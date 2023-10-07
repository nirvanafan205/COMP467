import csv

# Initialize names of what you need to save
producer = ""
operator = ""
job = ""
notes = ""

# Open the file in read mode
with open('Xytech.txt', 'r') as file:
    data = file.readlines()

# Parsing data line by line
capture_notes = False  # Flag to capture notes
for line in data:
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

# Join the lines of the "Notes" section into a single string
notes = ' '.join(notes).strip()

# Create a dictionary to store data
data_dict = {
        "Producer": producer,
        "Operator": operator,
        "Job": job,
        "Notes": notes,
        }

# Export data to CSV file
with open('output.csv', 'w', newline='') as csv_file:
    fieldnames = ["Producer", "Operator", "Job", "Notes"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    # Write header
    writer.writeheader()

    # Write data
    writer.writerow(data_dict)

print("Data exported to 'output.csv'")
