# TubeNotes

TubeNotes is a first-class OpenClaw skill designed to summarize YouTube videos into concise, actionable bullet points. It integrates seamlessly into your workflow, allowing you to preview summaries in chat and save them directly to your favorite note-taking application.

## Features

- **Seamless Integration:** Just paste a YouTube URL into your OpenClaw chat to trigger a summary.
- **AI-Powered Summarization:** Uses advanced LLMs (like Gemini) to extract key takeaways and instructions.
- **Action-Oriented Content:** Focuses on actionable items and punchy bullet points rather than just a general overview.
- **Timestamp Links:** Every summary includes timestamped links that take you directly to the relevant part of the video.
- **Interactive Workflow:**
    - **Preview:** Review the generated summary within the chat before saving.
    - **Save to Notes:** One-click saving to your destination of choice.
    - **Edit Summary:** Refine the output before it hits your permanent notes.
- **Flexible Destinations:** Primarily optimized for **Apple Notes** (saving to a "YT Summaries" folder), with configurable support for **SiYuan** and **Joplin**.

## Setup

### Prerequisites

- Python 3.10+
- [OpenClaw](https://github.com/min-hsao/openclaw) installed and configured.
- `yt-dlp` installed on your system (for transcript extraction).

### Installation

1. Clone the repository into your OpenClaw skills directory:
   ```bash
   git clone https://github.com/min-hsao/tubenotes.git
   cd tubenotes
   ```

2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Register the skill in your OpenClaw configuration:
   Add `tubenotes_skill.py` to your `active_skills` list in your OpenClaw settings.

## Configuration

TubeNotes can be customized via environment variables or a configuration file within the `tubenotes/` directory.

### LLM Provider
Configure your preferred AI model for summarization:
- `TUBENOTES_PROVIDER`: (default: `gemini`)
- `GOOGLE_API_KEY`: Required if using Gemini.
- `OPENAI_API_KEY`: Required if using OpenAI.

### Note-Taking Destinations
- `TUBENOTES_DESTINATION`: `apple_notes` (default), `siyuan`, or `joplin`.
- `APPLE_NOTES_FOLDER`: The name of the folder to save summaries (default: `YT Summaries`).

#### SiYuan / Joplin (Optional)
If using SiYuan or Joplin, provide the following:
- `DESTINATION_API_TOKEN`: Your API access token.
- `DESTINATION_ENDPOINT`: The server URL for your note-taking app.

### Summarization Style
- `SUMMARY_DETAIL`: `minimal` (default), `standard`, or `detailed`.
