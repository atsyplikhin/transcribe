# Audio Transcription Script

## Description
- This repository contains a Python script that transcribes long audio files using OpenAI API. 
- It splits the audio into manageable chunks, processes each segment, and compiles the results into a single transcription file. 
- An additional pass with ChatGPT or Claude may be helpful to clean up the text, stitch together the segments, and try to add speaker names. You will need to indicate speaker names and descriptions in the command line, then run the resulting text file through the LLM. 

## Requirements
- OpenAI API Key: Obtain from [OpenAI/api-keys](https://platform.openai.com/api-keys).
- Python 3.8+
- For transcribing non-wav files – like mp3 – you'll need ffmpeg or libav. Installation instructions here: [Getting ffmpeg set up](https://github.com/jiaaro/pydub/blob/master/README.markdown#getting-ffmpeg-set-up).

## Setup
Install ffmpeg if you need to transcribe non-wav files: [Getting ffmpeg set up](https://github.com/jiaaro/pydub/blob/master/README.markdown#getting-ffmpeg-set-up).
```bash
# Clone the repository
git clone https://github.com/atsyplikhin/transcribe.git
cd transcribe

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip setuptools
pip install -r requirements.txt
```

## Usage
- Transcribe an audio file (see example below): 
```bash
OPENAI_API_KEY="insert_your_key_here" python transcribe.py "[audio file path]" "[optional: language, for example fr]" "[optional: speaker names and descriptions - for diarization later]"
```
- You can optionally select a language, e.g. "en" or "fr".
- You can optionally add speaker names and descriptions to put the outputs through an LLM for diarization attempt as the next step.
- The script will produce a `.txt` file in the directory of the audio file, ready to be pasted into ChatGPT or Claude.

Note: to avoid using OPENAI_API_KEY every time you run the script, you can export it:
```bash
export OPENAI_API_KEY="insert_your_key_here"

# Now you can run transcribe.py without OPENAI_API_KEY in the command line:
python transcribe.py "[audio file path]" "[optional: language, for example fr]" "[optional: speaker names and descriptions - for diarization later]"
```


### Example: Transcribe Sample Audio File
```bash
# Download an example audio clip:
curl -O -J -L "https://www.dropbox.com/scl/fi/l7m6vavgbx143dbx4tqls/Example_To_Transcribe.m4a?rlkey=v4nd007gai7l7t6snqlnm65i2&dl=0"

#Transcribe audio
OPENAI_API_KEY="insert_your_key_here" python transcribe.py "Example_To_Transcribe.m4a" "en" "Tom Kelley (interviewer) and Ms. Smith (interviewee)"
```

Audio source is [here](https://youtu.be/yBtMwyQFXwA?si=7tZtPokSDR7JkBGu&t=177).


### Sample commands to set up from scratch on MacOS X 15.2 with Python 3.12
```bash
git clone https://github.com/atsyplikhin/transcribe.git
cd transcribe
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
# Install requirements
pip install -r requirements.txt
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install ffmpeg
echo >> /Users/aletsy01/.zprofile
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> /Users/aletsy01/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
# Install ffmpeg
brew install ffmpeg
# Run on an example
curl -O -J -L "https://www.dropbox.com/scl/fi/l7m6vavgbx143dbx4tqls/Example_To_Transcribe.m4a?rlkey=v4nd007gai7l7t6snqlnm65i2&dl=0"
OPENAI_API_KEY="insert_your_key_here" python transcribe.py "Example_To_Transcribe.m4a" "en" "Tom Kelley (interviewer) and Ms. Smith (interviewee)"
```

# Audio Compression Script: compress_voice_audio.py

Example commands (your folder)

Use your folder path exactly as given:

Standard voice compression (recommended):

python3 compress_voice_audio.py "/Users/aletsy01/Local Documents/Recordings/"


Overwrite filenames instead of writing _compressed.m4a:

python3 compress_voice_audio.py "/Users/aletsy01/Local Documents/Recordings/" --overwrite


Tighter compression for speech (smaller files, a bit less fidelity):

python3 compress_voice_audio.py "/Users/aletsy01/Local Documents/Recordings/" --bitrate 24k --samplerate 16000


Dry run (see what will happen, no files written):

python3 compress_voice_audio.py "/Users/aletsy01/Local Documents/Recordings/" --dry-run