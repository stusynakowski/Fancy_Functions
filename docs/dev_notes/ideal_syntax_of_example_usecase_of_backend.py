import sys
import os
import time
from typing import Any, List, Callable
from functools import wraps

# ==========================================
# 0. Mock Framework Implementation (For Demo)
# ==========================================

class Cell:
    def __init__(self, value: Any, name: str = None):
        self._value = value
        self.name = name or "Cell"
    
    @property
    def value(self):
        return self._value
    
    def set(self, value):
        print(f"   [Update] {self.name} changed value.")
        self._value = value
    
    def __repr__(self):
        return f"Cell({self._value})"

# Decorator Mocks that simulate the behavior
def fancy(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Unwrap cells
        raw_args = [a.value if isinstance(a, Cell) else a for a in args]
        raw_kwargs = {k: v.value if isinstance(v, Cell) else v for k, v in kwargs.items()}
        print(f" -> Running '{func.__name__}'...")
        res = func(*raw_args, **raw_kwargs)
        return Cell(res)
    return wrapper

def expand(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 1 -> N
        raw_args = [a.value if isinstance(a, Cell) else a for a in args]
        print(f" -> [Expand] '{func.__name__}' generating list...")
        results = func(*raw_args, **kwargs)
        return [Cell(r) for r in results]
    return wrapper

def vectorize(func):
    @wraps(func)
    def wrapper(cells, *args, **kwargs):
        # N -> N
        # Handle single cell or list of cells
        if isinstance(cells, Cell): cells = [cells]
        
        print(f" -> [Vectorize] '{func.__name__}' on {len(cells)} items...")
        results = []
        for c in cells:
            val = c.value
            res = func(val, *args, **kwargs)
            results.append(Cell(res))
        return results
    return wrapper

def reshape(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # N -> M
        # Unwrap logic for multiple lists
        unwrapped_args = []
        for arg in args:
            if isinstance(arg, list):
                unwrapped_args.append([c.value for c in arg])
            else:
                unwrapped_args.append(arg)
        
        print(f" -> [Reshape] '{func.__name__}' rearranging data...")
        # Function returns raw list of dicts/values
        raw_results = func(*unwrapped_args, **kwargs)
        return [Cell(r) for r in raw_results]
    return wrapper

def summarize(func):
    @wraps(func)
    def wrapper(cells, *args, **kwargs):
        # N -> 1
        print(f" -> [Summarize] '{func.__name__}' aggregating {len(cells)} items...")
        raw_values = [c.value for c in cells]
        res = func(raw_values, *args, **kwargs)
        return Cell(res)
    return wrapper

# ==========================================
# 1. Define The Logic (The "Fancy" Functions)
# ==========================================

# STEP 1: Extract Videos (1 -> N)
# Input: Single Cell (Channel URL)
# Output: List of Cells (Video URLs)
# Decorator: @expand because we generate multiple items from one source.
@expand
def fetch_channel_videos(channel_url: str) -> list[str]:
    # Mock impl: youtube_dl to get all video URLs
    print(f"Fetching videos for {channel_url}...")
    return [
        "https://youtu.be/video1", 
        "https://youtu.be/video2", 
        "https://youtu.be/video3"
    ]

# STEP 2 & 3: Metadata & Transcribe (N -> N)
# Input: List of Cells (Videos)
# Output: List of Cells (Metadata/Transcript)
# Decorator: @vectorize to apply this 1-to-1 logic over the list of videos.
@vectorize
def extract_metadata(video_url: str) -> dict:
    return {"title": "Title " + video_url, "duration": 120}

@vectorize
def transcribe_video(video_url: str) -> str:
    # Mock impl: Whisper or API call
    return f"Transcript for {video_url}..."

# STEP 4 & 5: Parse & Pivot to Conversations (N -> M)
# Input: List of Cells (Transcripts)
# Output: List of Cells (Conversation Utterances)
# Decorator: @reshape because we are transforming the structure (3 Transcripts -> 50 Conversations).
# We treat the list of transcripts as a dataset to be pivoted.
@reshape
def segment_conversations(transcripts: list[str], metadatas: list[dict]) -> list[dict]:
    all_segments = []
    for text, meta in zip(transcripts, metadatas):
        # Mock impl: Use LLM to split transcript into speaker chunks
        # This acts like a "FlatMap" operation
        segments = [
            {"person": "Host", "text": "Question?", "video": meta['title']},
            {"person": "Guest", "text": "Answer.", "video": meta['title']}
        ]
        all_segments.extend(segments)
    return all_segments

# STEP 6 & 7: Parse Categories & Iterative Analysis (M -> M)
# Input: List of Cells (Conversations)
# Output: List of Cells (Analyzed Data)
# Decorator: @vectorize to analyze each conversation independently.
@vectorize
def analyze_sentiment(conversation: dict) -> dict:
    # Mock impl: LLM Sementic analysis
    conversation['sentiment'] = 0.8  # Positive
    conversation['category'] = "Tech"
    return conversation

# STEP 8: Aggregate Analysis (M -> 1)
# Input: List of Cells (Analyzed Conversations)
# Output: Single Cell (Report)
# Decorator: @summarize to collapse the list into one result.
@summarize
def generate_channel_report(analyses: list[dict]) -> dict:
    # Aggregate stats
    avg_sentiment = sum(a['sentiment'] for a in analyses) / len(analyses)
    return {
        "total_conversations": len(analyses),
        "average_sentiment": avg_sentiment,
        "plot_image": "<bytes>" 
    }

# ==========================================
# 2. The Workflow Script (The "User" Code)
# ==========================================

# A. Definition Phase (Building the Graph)
# ----------------------------------------

# 0. The Input (Reactive Root)
channel_cell = Cell("https://youtube.com/@example_channel")

# 1. Get Videos (Generates a dynamic list of cells)
video_cells = fetch_channel_videos(channel_cell)
# `video_cells` is a List[Cell]

# 2. Get Metadata & Transcripts (Parallel Columns)
metadata_cells = extract_metadata(video_cells)
transcript_cells = transcribe_video(video_cells)

# 4 & 5. Pivot to Discussion Points (Reshapes N videos to M points)
# Note: We pass both columns to join them in the reshaping
conversation_cells = segment_conversations(transcript_cells, metadata_cells)
# `conversation_cells` is a new List[Cell] (likely larger than video_cells)

# 6 & 7. Row-level Analysis
analysis_cells = analyze_sentiment(conversation_cells)

# 8. Final Report (Reduces to single result)
final_report_cell = generate_channel_report(analysis_cells)


# B. Execution Phase (Reactive Behavior)
# --------------------------------------

# Accessing the value triggers the computation chain (Pull-based)
print("Generating Report...")
print(final_report_cell.value) 
# -> Output: {'total_conversations': 6, 'average_sentiment': 0.8, ...}

# C. Reactivity Example
# --------------------------------------

# If we change the input...
print("\n--- Updating Channel ---")
channel_cell.set("https://youtube.com/@another_channel")

# ...the exact minimal path updates.
# 1. fetch_channel_videos runs (new URL)
# 2. map/transcribe runs (new videos found)
# 3. segment_conversations runs (new transcripts)
# 4. analyze_sentiment runs
# 5. generate_channel_report runs

print(final_report_cell.value)