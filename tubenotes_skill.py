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
            with tempfile.TemporaryDirectory() as tmpdir:
                audio_path = os.path.join(tmpdir, "audio.mp3")
                download_cmd = [
                    "yt-dlp", "-x", "--audio-format", "mp3",
                    "-o", audio_path, url
                ]
                subprocess.run(download_cmd, capture_output=True)

                # Transcribe with Whisper CLI - generating JSON for timestamps
                whisper_cmd = [
                    "/opt/homebrew/bin/whisper", audio_path,
                    "--model", "base", "--output_dir", tmpdir, "--output_format", "json"
                ]
                subprocess.run(whisper_cmd, capture_output=True)

                transcript_json_path = os.path.join(tmpdir, "audio.json")
                transcript_with_timestamps = ""
                if os.path.exists(transcript_json_path):
                    with open(transcript_json_path, 'r') as f:
                        data = json.load(f)
                        for segment in data.get('segments', []):
                            start = int(segment['start'])
                            # Format seconds to M:SS or H:MM:SS
                            ts = ""
                            if start >= 3600:
                                ts = f"{start//3600}:{(start%3600)//60:02d}:{start%60:02d}"
                            else:
                                ts = f"{start//60}:{start%60:02d}"
                            transcript_with_timestamps += f"[{ts}] {segment['text']}\n"

            return {
                "title": title,
                "channel": uploader,
                "duration": duration,
                "url": url,
                "transcript": transcript_with_timestamps
            }
        except Exception as e:
            return {"error": str(e)}

    def generate_summary(self, video_info: Dict) -> str:
        # Use the transcript for summarization if available
        context = video_info.get('transcript', '')
        if not context:
            context = f"Title: {video_info['title']}"
        
        # Explicit instruction to include timestamps and the source link
        prompt = (
            f"Summarize this YouTube video: {video_info['url']}\n\n"
            f"Based on the following transcript (which includes timestamps in [M:SS] format), "
            "provide a punchy bulleted summary. \n"
            "CRITICAL: For each major point, include the timestamp from the transcript as a link in this format: "
            "[M:SS](URL&t=S) where URL is the video link and S is the total seconds. \n"
            "Include the original video link at the bottom.\n\n"
            f"Transcript:\n{context}"
        )
        
        try:
            cmd = ["/opt/homebrew/bin/gemini", prompt]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout.strip() if result.returncode == 0 else "Failed to generate AI summary."
        except:
            return "Gemini CLI not available."

    def save_to_apple_notes(self, summary: str, title: str) -> bool:
        """Save summary to Apple Notes using the bin/notes CLI."""
        try:
            notes_script = os.path.expanduser("~/clawd/bin/notes")
            if not os.path.exists(notes_script):
                return False

            # Use 'create' command: create <name> <body> [folder]
            # Convert simple markdown to HTML for Notes
            html_body = summary.replace("\n", "<br>").replace("**", "<b>").replace("`", "<code>")
            subprocess.run([notes_script, "create", title, html_body, DEFAULT_FOLDER], capture_output=True)
            return True
        except Exception as e:
            return False

    def handle_callback(self, callback_data: str, summary: str, title: str) -> str:
        """Handle button clicks."""
        if callback_data.startswith("save:"):
            if self.save_to_apple_notes(summary, title):
                return f"✅ Saved to Apple Notes (Folder: {DEFAULT_FOLDER})."
            else:
                return "❌ Failed to save to Apple Notes. Check bin/notes script."
        return "Action cancelled."

if __name__ == "__main__":
    import sys
    skill = TubeNotesSkill()
    # Basic CLI wrapper for testing
    if len(sys.argv) > 1:
        url = sys.argv[1]
        info = skill.get_video_info(url)
        summary = skill.generate_summary(info)
        print(summary)
