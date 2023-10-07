# Initialize names of what you need to save
producer = ""
operator = ""
job = ""
location = []
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
    elif line.startswith("/"):
        location.append(line)
    elif line.startswith("Notes:"):
        capture_notes = True  # Start capturing notes
        notes = []  # Initialize notes as a list
    elif capture_notes:
        notes.append(line)  # Capture all lines after "Notes:" until the end

# Printing
print("Producer:", producer)
print("Operator:", operator)
print("Job:", job)
print("Location:", location)
if notes:
    print("Notes:")
    for note_line in notes:
        print(note_line)
