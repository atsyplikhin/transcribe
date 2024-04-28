# Audio Transcription Script

## Description
- This repository contains a Python script that transcribes long audio files using OpenAI API. 
- It splits the audio into manageable chunks, processes each segment, and compiles the results into a single transcription file. 
- An additional pass with ChatGPT or Claude may be helpful to clean up the text, stitch together the segments, and try to add speaker names. You will need to indicate speaker names and descriptions in the command line, then run the resulting text file through the LLM. 

## Requirements
- OpenAI API Key: Obtain from [OpenAI/api-keys](https://platform.openai.com/api-keys).
- Python 3.8+

## Setup
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
OPENAI_API_KEY="insert_your_key_here" python transcribe.py "[audio file path]" "[optional: speaker names and descriptions - for diarization later]"
```
- You can optionally add speaker names and descriptions to put the outputs through an LLM for diarization attempt as the next step.
- The script will produce a `.txt` file in the directory of the audio file, ready to be pasted into ChatGPT or Claude.

### Transcribe Sample Script
```bash
# Download an example audio clip:
curl -O -J -L "https://www.dropbox.com/scl/fi/6sn0jyeiy4dwmr3g8nzds/Example_Kahneman_Decision_Making.m4a?rlkey=httibe0rmsqro98smuz120nla&dl=0"

#Transcribe audio
OPENAI_API_KEY="insert_your_key_here" python transcribe.py Example_Kahneman_Decision_Making.m4a "DANIEL KAHNEMAN, Behavioral Economist and Nobel Laureate and ALEC ELLISON, Founder, Outvest Capital, former Vice Chairman, Jefferies"
```