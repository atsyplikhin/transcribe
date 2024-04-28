import os
import sys
from pathlib import Path
from pydub import AudioSegment
from openai import OpenAI

# Check if the file path is provided
if len(sys.argv) < 2:
    print("Usage: python script.py <path to audio file>")
    sys.exit(1)

speaker_names = f"The speakers are {sys.argv[2]}." if len(sys.argv) >= 3 else ""

# Command line argument for the file path
input_file_path = sys.argv[1]
input_path = Path(input_file_path)

# Initialize OpenAI client
client = OpenAI()

# Read the audio file from the provided path
audio = AudioSegment.from_file(input_file_path)

chunk_length_ms = 10 * 60 * 1000  # 10 minutes
overlap_ms = 5 * 1000  # 5 seconds

i, current_offset = 0, 0
transcription_file_path = input_path.parent / f"{input_path.stem}_transcript.txt"

# Temporary file for transcription
tmp_fname = "$$tmp_audio_for_transcription$$.mp3"

# Open the output file for writing
with transcription_file_path.open("w") as out_file:
    while True:
        portion = audio[current_offset:(current_offset + chunk_length_ms)]
        if len(portion) == 0: break

        portion.export(tmp_fname, format="mp3")

        with open(tmp_fname, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
            line = f"Transcription portion {i + 1}\n{transcription.text}\n\n"
            out_file.write(line)
            print(line)

        # Move to the next chunk
        i += 1
        current_offset += chunk_length_ms - overlap_ms

    prompt = f"""---
You are a helpful assistant. Your task is to correct any spelling discrepancies in 
the transcribed text above, combine portions, split with new lines when speaker or topic appear to changes. 
Remove filler words such as okay, right, you know, kind of, like, really, you know, well, and others. 
Do not remove phrases otherwise, keep the whole meaning. 
Only add necessary punctuation such as periods, commas, and capitalization, and use only the context provided. 
{speaker_names} 
The format must be as follows:
**Speaker 1 Name**: Hello.

**Speaker 2 Name**: Hello.

**Speaker 1 Name**: How are you?"""
    out_file.write(prompt)

# Delete the temporary file
os.remove(tmp_fname)

print(f"Transcription completed. Output file located at: {transcription_file_path}")
