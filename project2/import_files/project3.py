import argparse
import csv
import xlsxwriter
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

# Extract relevant fields and calculate timecodes
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

    # Check if the frame range is within the total frames of the video
    if start_frame <= total_frames and end_frame <= total_frames:
        start_timecode = frames_to_timecode(start_frame, frame_rate)
        end_timecode = frames_to_timecode(end_frame, frame_rate)
        data.append([location, frame_range, f"{start_timecode} to {end_timecode}"])

# Define headers
headers = ["Location", "Frame Range", "Timecode Range"]

# Choose output format and write data
output_path = 'output'
if args.output.lower() == "xlsx":
    output_path += ".xlsx"
    workbook = xlsxwriter.Workbook(output_path)
    worksheet = workbook.add_worksheet()

    # Write the headers
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header)

    # Write the data
    for row_num, row_data in enumerate(data, start=1):
        for col_num, cell_data in enumerate(row_data):
            worksheet.write(row_num, col_num, cell_data)

    workbook.close()
else:  # Default to CSV
    output_path += ".csv"
    with open(output_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(headers)
        csv_writer.writerows(data)

print(f"Data exported to {output_path}")