import os
import sys
from pathlib import Path

from pydub import AudioSegment
import whisper

# ---------------------------------------------------------------------------
# USAGE:
# python local_whisper_transcribe.py <path to audio file> [<language>] [<speaker names>]
# Example:
#   python local_whisper_transcribe.py my_recording.mp3 en "Alice and Bob"
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python local_whisper_transcribe.py <path to audio file> [<language>] [<speaker names>]")
        sys.exit(1)

    # Extract arguments
    input_file_path = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) >= 3 else "en"
    speaker_names = f"The speakers are {sys.argv[3]}." if len(sys.argv) >= 4 else ""

    # Verify the input file exists
    input_path = Path(input_file_path)
    if not input_path.is_file():
        print(f"Error: The file {input_file_path} does not exist.")
        sys.exit(1)

    # Load the audio using pydub
    audio = AudioSegment.from_file(input_file_path)

    # Load Whisper model locally with MPS (Metal) if you have an Apple Silicon GPU
    # Options for device: "cpu", "cuda", or "mps" (on Apple Silicon)
    model = whisper.load_model("large", device="cpu")  # or "small", "medium", etc.

    chunk_length_ms = 10 * 60 * 1000  # 10 minutes
    overlap_ms = 5 * 1000  # 5 seconds

    i, current_offset = 0, 0
    transcription_file_path = input_path.parent / f"{input_path.stem}_transcript.txt"

    # Temporary audio segment we export in chunks (keep on disk to feed to Whisper)
    tmp_fname = "$$tmp_audio_for_transcription$$.mp3"

    # Open the output file for writing
    with transcription_file_path.open("w", encoding="utf-8") as out_file:
        while True:
            # Extract the chunk
            portion = audio[current_offset : (current_offset + chunk_length_ms)]
            if len(portion) == 0:
                break

            # Export chunk to a temporary file
            portion.export(tmp_fname, format="mp3")

            # Use Whisper to transcribe locally
            # language parameter can be set if you know the language (e.g., "en")
            result = model.transcribe(tmp_fname, language=language)
            text_chunk = result["text"]

            line = f"Transcription portion {i + 1}\n{text_chunk}\n\n"
            out_file.write(line)
            print(line, flush=True)

            i += 1
            current_offset += chunk_length_ms - overlap_ms

        # Append the post-processing prompt
        prompt = f"""---
You are a helpful assistant. Your task is to correct any spelling discrepancies in 
the transcribed text above, combine portions, and split with new lines when speaker or topic appear to change. 
Remove filler words such as okay, right, you know, kind of, like, really, you know, well, and others. 
Do not remove phrases otherwise, keep the whole meaning. 
Only add necessary punctuation such as periods, commas, and capitalization, and use only the context provided. 
{speaker_names}
The format must be as follows:
**Speaker 1 Name**: Hello.

**Speaker 2 Name**: Hello.

**Speaker 1 Name**: How are you?
"""
        out_file.write(prompt)

    # Remove the temporary file
    os.remove(tmp_fname)

    print(f"Transcription completed. Output file located at: {transcription_file_path}")

if __name__ == "__main__":
    main()
