#!/usr/bin/env python3
"""
TubeNotes - OpenClaw skill for summarizing YouTube videos.
"""

import os
import re
import json
import subprocess
import tempfile
from typing import Optional, Dict, List
from datetime import datetime

# Configuration
DEFAULT_FOLDER = "YT Summaries"
LLM_PROVIDER = os.getenv("TUBENOTES_PROVIDER", "gemini")

class TubeNotesSkill:
    def __init__(self):
        # Support standard watch URLs and Shorts
        self.youtube_pattern = re.compile(
            r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)([\w-]+)'
        )
    
    def detect_youtube_url(self, text: str) -> Optional[str]:
        match = self.youtube_pattern.search(text)
        return match.group(0) if match else None
    
    def get_video_info(self, url: str) -> Dict:
        try:
            # 1. Get video metadata via yt-dlp
            cmd = [
                "yt-dlp",
                "--skip-download",
                "--print", "%(title)s|%(uploader)s|%(duration)s",
                url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(result.stderr)
            
            parts = result.stdout.strip().split('|')
            title = parts[0]
            uploader = parts[1]
            duration = parts[2]

            # 2. Download audio and transcribe with local Whisper
            # Use a temporary directory for the audio/transcript
            with tempfile.TemporaryDirectory() as tmpdir:
                audio_path = os.path.join(tmpdir, "audio.mp3")
                download_cmd = [
                    "yt-dlp", "-x", "--audio-format", "mp3",
                    "-o", audio_path, url
                ]
                subprocess.run(download_cmd, capture_output=True)

                # Transcribe with Whisper CLI
                whisper_cmd = [
                    "/opt/homebrew/bin/whisper", audio_path,
                    "--model", "base", "--output_dir", tmpdir, "--output_format", "txt"
                ]
                subprocess.run(whisper_cmd, capture_output=True)

                transcript_path = os.path.join(tmpdir, "audio.txt")
                transcript = ""
                if os.path.exists(transcript_path):
                    with open(transcript_path, 'r') as f:
                        transcript = f.read()

            return {
                "title": title,
                "channel": uploader,
                "duration": duration,
                "url": url,
                "transcript": transcript
            }
        except Exception as e:
            return {"error": str(e)}

    def generate_summary(self, video_info: Dict) -> str:
        # Use the transcript for summarization if available
        context = video_info.get('transcript', '')
        if not context:
            # Fallback to title/description if transcript failed
            context = f"Title: {video_info['title']}"
        
        prompt = f"Summarize this YouTube video based on the following transcript. Keep it to punchy bullet points. Transcript: {context}"
        
        try:
            cmd = ["/opt/homebrew/bin/gemini", prompt]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout.strip() if result.returncode == 0 else "Failed to generate AI summary."
        except:
            return "Gemini CLI not available."

    def save_to_apple_notes(self, summary: str, title: str) -> bool:
        """Save summary to Apple Notes using the bin/notes CLI."""
        try:
            # Use the notes script from ~/clawd/bin as per USER.md
            notes_script = os.path.expanduser("~/clawd/bin/notes")
            
            if not os.path.exists(notes_script):
                print(f"Notes script not found at {notes_script}")
                return False

            # The notes script usage: notes add --title "Title" --body "Body"
            # Assuming it handles folder 'YT Summaries' or we just add it to the default
            subprocess.run([notes_script, "add", "--title", title, "--body", summary], capture_output=True)
            return True
        except Exception as e:
            print(f"Error saving to Apple Notes: {e}")
            return False

    def handle_callback(self, callback_data: str, summary: str, title: str) -> str:
        """Handle button clicks."""
        if callback_data.startswith("save:"):
            if self.save_to_apple_notes(summary, title):
                return "✅ Saved to Apple Notes (Folder: YT Summaries)."
            else:
                return "❌ Failed to save to Apple Notes. Check bin/notes script."
        return "Action cancelled."

if __name__ == "__main__":
    import sys
    skill = TubeNotesSkill()
    print(json.dumps(skill.handle_message(sys.argv[1]), indent=2))
