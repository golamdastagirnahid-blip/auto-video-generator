import os
import asyncio
import edge_tts
from config import Config
from rich.console import Console

console = Console()


class AudioGenerator:

    def __init__(self, voice: str = None):
        self.voice    = voice or Config.VOICE
        self.temp_dir = Config.TEMP_DIR
        os.makedirs(self.temp_dir, exist_ok=True)

    def generate_scene_audio(self, text: str, index: int) -> dict:
        console.print(f"  🎤 Generating voice for scene {index}...")
        console.print(f"  📝 Text: [cyan]{text[:50]}[/cyan]")

        output_path = os.path.join(self.temp_dir, f"audio_{index:04d}.mp3")

        # Generate the audio file and get subtitles
        subtitles = asyncio.run(self._speak(text, output_path))

        # Get duration using moviepy instead of pydub
        from moviepy.editor import AudioFileClip
        audio    = AudioFileClip(output_path)
        duration = audio.duration
        audio.close()

        console.print(f"  ✅ Voice ready - Duration: [green]{duration:.1f} seconds[/green]")

        return {
            "path"      : output_path,
            "duration"  : duration,
            "subtitles" : subtitles
        }

    async def _speak(self, text: str, output_path: str) -> list:
        # Use Microsoft Edge TTS to generate voice
        communicate = edge_tts.Communicate(
            text   = text,
            voice  = self.voice,
            rate   = Config.RATE,
            volume = Config.VOLUME
        )

        subtitles = []

        with open(output_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    subtitles.append({
                        "text"     : chunk["text"],
                        "offset"   : chunk["offset"],
                        "duration" : chunk["duration"]
                    })

        return subtitles

    def get_word_timestamps(self, subtitles: list) -> list:
        # Convert timing to seconds
        result = []
        for s in subtitles:
            start = s["offset"]   / 10_000_000
            dur   = s["duration"] / 10_000_000
            result.append({
                "word"  : s["text"],
                "start" : start,
                "end"   : start + dur
            })
        return result
