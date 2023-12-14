import argparse
import csv
import io
import tempfile
from PIL import Image
import xlsxwriter
from pymongo import MongoClient
from moviepy.editor import VideoFileClip
import os
from frameioclient import FrameioClient
 
  #  Convert  frame number to a timecode 
def frames_to_timecode(frames, frame_rate):
    total_seconds = frames / frame_rate
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    frames = int((total_seconds - int(total_seconds)) * frame_rate)
    return f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}"

# Get middle frame number from a frame range
def get_middle_frame(start_frame, end_frame):
    return start_frame + (end_frame - start_frame) // 2

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['magneto']
collection = db['insertTwo']

# Initialize argument parser
parser = argparse.ArgumentParser(description="Export data from MongoDB to CSV/XLSX and process a video file.")
parser.add_argument("--process", help="Path to video file for processing", type=str)
parser.add_argument("--output", help="Output file format (csv or xlsx)", type=str, default="csv")
args = parser.parse_args()

frame_rate = None

# Check if --process argument is provided
if args.process:
    # Load the video file
    video = VideoFileClip(args.process)
    
    # Get the duration and frame rate of the video
    video_duration = video.duration
    frame_rate = video.fps
    total_frames = int(video_duration * frame_rate)
    print(f"Processing video file: {args.process}")
    print(f"Video duration: {video_duration} seconds")
    print(f"Frame rate: {frame_rate} fps")

# Fetch data from MongoDB
mongo_data = collection.find()

# Create a directory to save thumbnails
thumbnail_dir = 'thumbnails'
os.makedirs(thumbnail_dir, exist_ok=True)

# Extract fields and calculate timecodes
data = []
for entry in mongo_data:
    location = entry['Location']
    frame_range = entry['FrameRange']

    if '-' in frame_range:
        start_frame, end_frame = map(int, frame_range.split('-'))
    elif frame_range.isdigit():
        start_frame = end_frame = int(frame_range)
    else:
        continue  # Skip this entry

    # Check if frame range is within the total frames of the video
    if start_frame <= total_frames and end_frame <= total_frames:
        # Calculate the middle frame for thumbnail
        middle_frame = get_middle_frame(start_frame, end_frame)
        
        # Extract frame as an image
        frame_image = video.get_frame(middle_frame / frame_rate)
        
        # Convert to PIL image and resize
        pil_image = Image.fromarray(frame_image)
        pil_image.thumbnail((96, 74))  

        # Save image as a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg", dir=thumbnail_dir) as temp_file:
            pil_image.save(temp_file, format="JPEG")
            temp_file_path = temp_file.name

        # Convert frames to timecode
        start_timecode = frames_to_timecode(start_frame, frame_rate)
        end_timecode = frames_to_timecode(end_frame, frame_rate)

        # Append to data 
        data.append([location, frame_range, f"{start_timecode} to {end_timecode}", temp_file_path])

# Define headers
headers = ["Location", "Frame Range", "Timecode Range", "Thumbnail"]

# Choose output format and write data
output_path = 'output'
if args.output.lower() == "xlsx":
    output_path += ".xlsx"
    workbook = xlsxwriter.Workbook(output_path)
    worksheet = workbook.add_worksheet()

    # Write the headers
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header)

    # Write the data and add images
    for row_num, row_data in enumerate(data, start=1):
        for col_num, cell_data in enumerate(row_data):
            if col_num < 3:  # Regular data
                worksheet.write(row_num, col_num, cell_data)
            else:  # Image data
                worksheet.insert_image(row_num, col_num, cell_data)

    workbook.close()
else:  # Default to CSV
    output_path += ".csv"
    with open(output_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(headers)
        csv_writer.writerows(data)

print(f"Data exported to {output_path}")

# Initialize the Frame.io client
TOKEN = "fio-u-_suRg2CLQTfBsRNpD9Zv-kC5yy46K7u5SHaRG_eIrXjL0MmQ5ECrmIfq2vEHVuVU"
client = FrameioClient(TOKEN)

# project ID
project_id = "24049025-17ca-4d9a-84e5-b0741141ff99"

# Fetch the project details to get the root_asset_id
project = client.projects.get(project_id)
root_asset_id = project['root_asset_id']

# Loop through the saved thumbnails and upload them to Frame.io
for thumbnail_path in data:
    location, frame_range, timecode_range, thumbnail_path = thumbnail_path
    
    if os.path.isfile(thumbnail_path):
        # use destination_id to upload the image
        asset = client.assets.upload(
            destination_id=root_asset_id,
            filepath=thumbnail_path
        )
        print(f"Uploaded image for Location: {location}")
    else:
        print(f"File not found: {thumbnail_path}")