import os # interacts w/ os
import time # time related functions and sleep

folderPath = "week3" # string to find folder

# function
def checkNewfile():
    while True: # start of infin loop
        files = os.listdir(folderPath) # gets all files and directories
        if files: # checks list is not empty
            for fileName in files:
                filePath = os.path.join(folderPath, fileName) # access files properties
                if os.path.isfile(filePath): # checks current item
                    fileType = fileName.split('.')[-1] # gets extension
                    file_created_time = time.ctime(os.path.getctime(filePath)) # time 
                    # messages
                    print("File found:")
                    print(f" Name: {fileName}")
                    print(f" Type: {fileType}")
                    print(f" Created Time: {file_created_time}")
                    return
        time.sleep(1)

if __name__ == "__main__":
    if not os.path.exists(folderPath):
        os.mkdir(folderPath)
    print(f"Monitoring folder '{folderPath}' for new files...")
    checkNewfile()
