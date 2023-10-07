# initialized names of what I need to save
producer = ""
operator = ""
job = ""
location = []
notes = ""

# Open the files in read mode
with open('Xytech.txt', 'r') as file:
    data= file.read()

# parsing data
for line in data:
    line = line.strip()

        # save names and such 
    if line.startswith("Producer:"):
        producer = line[len("Producer:"):].strip()

    elif line.startswith("Operator:"):
        operator = line[len("Operator:"):].strip()

    elif line.startswith("Job:"):
        job = line[len("Job:"):].strip()

    elif line.startswith("/"):
        location.append(line)

    elif line.startswith("Notes:"):
        notes = line[len("Notes:"):].strip()

# printing 
print("Producer:", producer)
print("Operator:", operator)
print("Job:", job)
print("Location:", location)
print("Notes:", notes)
