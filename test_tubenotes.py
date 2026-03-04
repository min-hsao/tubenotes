#!/usr/bin/env python3
"""Test the TubeNotes skill."""
import sys
sys.path.insert(0, '.')

from tubenotes_skill import TubeNotesSkill

skill = TubeNotesSkill()

# Test URL detection
test_texts = [
    "Check out this video: https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "No URL here",
    "Short URL: https://youtu.be/dQw4w9WgXcQ",
    "Another one: www.youtube.com/watch?v=test123"
]

for text in test_texts:
    url = skill.detect_youtube_url(text)
    print(f"Text: {text[:50]}...")
    print(f"  Detected URL: {url}")
    print()

# Test summary generation (mock)
print("Testing summary generation...")
mock_info = {
    "title": "Test Video Title",
    "channel": "Test Channel",
    "duration": 600,
    "url": "https://youtube.com/watch?v=test",
    "transcript": "Test transcript",
    "description": "Test description"
}

summary = skill.generate_summary(mock_info)
print(f"Generated summary length: {len(summary)} chars")
print("First 200 chars:", summary[:200])
