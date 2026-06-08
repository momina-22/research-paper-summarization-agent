#step 2 -- TExt Cleaning
import re

def preprocess_text(text: str) -> str:
    text = re.sub(r'\n{3,}', '\n\n', text)       # remove excess newlines
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)   # remove non-ASCII
    text = re.sub(r'\s+', ' ', text)              # normalize spaces
    text = re.sub(r'\[\d+\]', '', text)           # remove citation numbers
    return text.strip()