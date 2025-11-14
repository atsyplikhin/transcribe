import os
import sys
from pathlib import Path
from pydub import AudioSegment
from openai import OpenAI

def format_timestamp(seconds):
    """Convert seconds to MM:SS format"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def format_transcript(segments):
    """
    Format transcript segments into a readable conversation format
    
    Args:
        segments: List of segment dictionaries from transcript.to_dict()["segments"]
    
    Returns:
        Formatted transcript as a string
    """
    if not segments:
        return "No transcript segments found."
    
    output_lines = []
    
    current_speaker = None
    current_text = []
    current_start = None
    
    for segment in segments:
        speaker = segment.get('speaker', 'Unknown')
        text = segment.get('text', '').strip()
        start = segment.get('start', 0)
        
        # If speaker changes, output the previous speaker's accumulated text
        if speaker != current_speaker and current_speaker is not None:
            timestamp = format_timestamp(current_start)
            combined_text = ''.join(current_text)
            output_lines.append(f"[{timestamp}] Speaker_{current_speaker}: {combined_text}")
            current_text = []
        
        # Update current speaker and accumulate text
        if speaker != current_speaker:
            current_speaker = speaker
            current_start = start
        
        current_text.append(text)
    
    # Output the last speaker's text
    if current_text:
        timestamp = format_timestamp(current_start)
        combined_text = ''.join(current_text)
        output_lines.append(f"[{timestamp}] Speaker_{current_speaker}: {combined_text}")
    
    return "\n".join(output_lines)

# Check if the required file path is provided
if len(sys.argv) < 2:
    print("Usage: python script.py <path to audio file> [<language>] [<speaker names>]")
    sys.exit(1)

# Extract optional arguments
input_file_path = sys.argv[1]
# language = sys.argv[2] if len(sys.argv) >= 3 else "en"
# speaker_names = f"The speakers are {sys.argv[3]}." if len(sys.argv) >= 4 else ""

# Verify input file path
input_path = Path(input_file_path)
if not input_path.is_file():
    print(f"Error: The file {input_file_path} does not exist.")
    sys.exit(1)

# Initialize OpenAI client
base_url = os.getenv("OPENAI_BASE_URL")
client = OpenAI(base_url=base_url)

transcription_file_path = input_path.parent / f"{input_path.stem}_transcript.txt"

with open(input_file_path, "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        file=audio_file,
        model="gpt-4o-transcribe-diarize",
        chunking_strategy="auto",
        response_format="diarized_json",
    )
    output = format_transcript(transcript.to_dict()["segments"])
    print(output)

with transcription_file_path.open("w") as out_file:
    out_file.write(output)

print(f"Transcription completed. Output file located at: {transcription_file_path}")