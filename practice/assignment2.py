# Read the file, replace vowels with '7', and print to console
with open("ingest_this.txt", "r") as file:
    content = file.read()
    modified_content = ''.join(['7' if char in 'aeiouAEIOU' else char for char in content])
    print(modified_content)
