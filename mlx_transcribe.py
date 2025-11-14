import os
import sys
from pathlib import Path
from pydub import AudioSegment
from lightning_whisper_mlx import LightningWhisperMLX

# ---------------------------------------------------------------------------
# USAGE:
# python mlx_transcribe.py <path to audio file> [<language>] [<model>] [<quantization>] [<speaker names>]
# Example:
#   python mlx_transcribe.py my_recording.mp3 en "distil-medium.en" "None" "Alice and Bob"
# ---------------------------------------------------------------------------

def transcribe_audio(model, file_path, language="en"):
    """Transcribe audio using Lightning Whisper MLX."""
    transcription = model.transcribe(audio_path=file_path, language=language)
    return transcription.get("text", "")

def main():
    if len(sys.argv) < 2:
        print("Usage: python mlx_transcribe.py <path to audio file> [<language>] [<model>] [<quantization>] [<speaker names>]")
        sys.exit(1)

    # Extract arguments
    input_file_path = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) >= 3 else "en"
    model_name = sys.argv[3] if len(sys.argv) >= 4 else "distil-large-v3"
    quantization = sys.argv[4] if len(sys.argv) >= 5 else None  # Options: None, "4bit", "8bit"
    speaker_names = f"The speakers are {sys.argv[5]}." if len(sys.argv) >= 6 else ""

    # Verify input file
    input_path = Path(input_file_path)
    if not input_path.is_file():
        print(f"Error: The file {input_file_path} does not exist.")
        sys.exit(1)

    # Load Lightning Whisper MLX model
    whisper = LightningWhisperMLX(model=model_name, batch_size=12, quant=quantization)

    # Load the audio file
    audio = AudioSegment.from_file(input_file_path)

    # Define chunking parameters
    chunk_length_ms = 10 * 60 * 1000  # 10 minutes
    overlap_ms = 5 * 1000  # 5 seconds

    transcription_file_path = input_path.parent / f"{input_path.stem}_transcript.txt"
    tmp_fname = "$$tmp_audio_for_transcription$$.mp3"

    # Open output file
    with transcription_file_path.open("w", encoding="utf-8") as out_file:
        current_offset, i = 0, 0

        while True:
            portion = audio[current_offset : (current_offset + chunk_length_ms)]
            if len(portion) == 0:
                break

            portion.export(tmp_fname, format="mp3")
            text_chunk = transcribe_audio(whisper, tmp_fname, language=language)

            # Write transcript portion
            line = f"Transcription portion {i + 1}\n{text_chunk}\n\n"
            out_file.write(line)
            print(line, flush=True)

            i += 1
            current_offset += chunk_length_ms - overlap_ms

#         # Append post-processing instructions
#         prompt = f"""---
# You are a helpful assistant. Your task is to correct any spelling discrepancies in 
# the transcribed text above, combine portions, and split with new lines when speaker or topic appear to change. 
# Remove filler words such as okay, right, you know, kind of, like, really, well, and others. 
# Do not remove phrases otherwise, keep the whole meaning. 
# Only add necessary punctuation such as periods, commas, and capitalization, and use only the context provided. 
# {speaker_names}
# The format must be as follows:
# **Speaker 1 Name**: Hello.

# **Speaker 2 Name**: Hello.

# **Speaker 1 Name**: How are you?
# """
#         out_file.write(prompt)

    # Clean up
    os.remove(tmp_fname)
    print(f"Transcription completed. Output file located at: {transcription_file_path}")

if __name__ == "__main__":
    main()
