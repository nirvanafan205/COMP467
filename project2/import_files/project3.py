import argparse
import csv
from pymongo import MongoClient
from moviepy.editor import VideoFileClip

def frames_to_timecode(frames, frame_rate):
    """Convert a frame number to a timecode string based on the frame rate."""
    total_seconds = frames / frame_rate
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    frames = int((total_seconds - int(total_seconds)) * frame_rate)
    return f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}"

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

frame_rate = None
total_frames = None

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
    print(f"Total frames: {total_frames}")

# Fetch data from MongoDB
mongo_data = collection.find()

# Extract relevant fields and calculate timecodes
csv_data = []
for entry in mongo_data:
    location = entry['Location']
    frame_range = entry['FrameRange']

    if '-' in frame_range:
        start_frame, end_frame = map(int, frame_range.split('-'))
    elif frame_range.isdigit():
        start_frame = end_frame = int(frame_range)
    else:
        print(f"Invalid frame range format for location {location}: {frame_range}")
        continue  # Skip this entry

    # Check if the frame range is within the total frames of the video
    if start_frame <= total_frames and end_frame <= total_frames:
        # Convert frames to timecode
        start_timecode = frames_to_timecode(start_frame, frame_rate)
        end_timecode = frames_to_timecode(end_frame, frame_rate)

        # Append to csv_data
        csv_data.append((location, frame_range, f"{start_timecode} to {end_timecode}"))
    else:
        print(f"Frame range {frame_range} for location {location} is outside the video length")

# Write data to CSV file
with open(csv_output_path, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)

    # Write data
    csv_writer.writerows(csv_data)

print(f"Data exported to {csv_output_path}")