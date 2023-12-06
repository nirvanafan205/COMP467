import argparse
import csv
from pymongo import MongoClient
from moviepy.editor import VideoFileClip

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['magneto']
collection = db['insertTwo']

# Output CSV file path
csv_output_path = 'output.csv'

# Initialize argument parser
parser = argparse.ArgumentParser(description="Export data from MongoDB to CSV and process a video file.")

# Add arguments to the parser
parser.add_argument("--process", help="Path to video file for processing", type=str)
args = parser.parse_args()

# Check if --process argument is provided
if args.process:
    # Load the video file
    video = VideoFileClip(args.process)
    
    # Get the duration of the video
    video_duration = video.duration
    print(f"Processing video file: {args.process}")
    print(f"Video duration: {video_duration} seconds")

    # Get the frame rate of the video
    frame_rate = video.fps
    print(f"Frame rate: {frame_rate} fps")

    # Here you can add additional video processing logic if needed

# Fetch data from MongoDB
mongo_data = collection.find()

# Extract relevant fields
csv_data = [(entry['Location'], entry['FrameRange']) for entry in mongo_data]

# Write data to CSV file
with open(csv_output_path, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)

    # Write data
    csv_writer.writerows(csv_data)

print(f"Data exported to {csv_output_path}")