"""
🎬 AUTO VIDEO GENERATOR
Give it a script, it makes a professional video!
100% FREE - No paid tools needed
"""

import os
import sys
import shutil
import argparse
from rich.console import Console
from rich.panel import Panel

from config import Config
from modules.script_parser import ScriptParser
from modules.image_fetcher import ImageFetcher
from modules.audio_generator import AudioGenerator
from modules.video_composer import VideoComposer

console = Console()


def show_welcome():
    console.print(Panel.fit(
        "[bold cyan]🎬 AUTO VIDEO GENERATOR[/bold cyan]\n"
        "[green]Script → Professional Video[/green]\n"
        "[yellow]100% FREE | Images | Voice | Captions[/yellow]",
        border_style="cyan"
    ))


def clean_temp():
    # Clean old temporary files
    if os.path.exists(Config.TEMP_DIR):
        shutil.rmtree(Config.TEMP_DIR)
    os.makedirs(Config.TEMP_DIR,   exist_ok=True)
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)


def generate_video(
    script_text: str,
    voice:       str = "male_us",
    output:      str = "my_video.mp4"
):
    show_welcome()
    clean_temp()

    # Setup all modules
    parser    = ScriptParser()
    fetcher   = ImageFetcher()
    audio_gen = AudioGenerator(voice=Config.VOICES.get(voice, Config.VOICE))
    composer  = VideoComposer()

    # ─────────────────────────────────────────
    # STEP 1 — Read and parse the script
    # ─────────────────────────────────────────
    console.print("\n[bold yellow]📝 STEP 1: Reading your script...[/bold yellow]\n")
    scenes = parser.parse(script_text)
    console.print(f"✅ Found [bold]{len(scenes)}[/bold] scenes in your script\n")

    for scene in scenes:
        console.print(f"  Scene {scene.index + 1}: [cyan]{scene.text[:70]}[/cyan]")
        console.print(f"  Keywords: [green]{', '.join(scene.keywords)}[/green]\n")

    # ─────────────────────────────────────────
    # STEP 2 — Generate voice for each scene
    # ─────────────────────────────────────────
    console.print("[bold yellow]🎤 STEP 2: Generating voice narration...[/bold yellow]\n")

    all_timestamps = []
    time_offset    = 0.0

    for scene in scenes:
        result           = audio_gen.generate_scene_audio(scene.text, scene.index)
        scene.audio_path = result["path"]
        scene.duration   = result["duration"]

        # Collect word timestamps with time offset
        timestamps = audio_gen.get_word_timestamps(result["subtitles"])
        for ts in timestamps:
            ts["start"] += time_offset
            ts["end"]   += time_offset
        all_timestamps.extend(timestamps)

        time_offset += scene.duration

    total_time = sum(s.duration for s in scenes)
    console.print(f"\n✅ Total video duration will be: [bold]{total_time:.1f} seconds[/bold]\n")

    # ─────────────────────────────────────────
    # STEP 3 — Download images for each scene
    # ─────────────────────────────────────────
    console.print("[bold yellow]🖼️ STEP 3: Downloading images...[/bold yellow]\n")

    for scene in scenes:
        image_path       = fetcher.fetch_image(scene.search_query, scene.index)
        scene.image_path = image_path

    console.print("\n✅ All images downloaded!\n")

    # ─────────────────────────────────────────
    # STEP 4 — Compose the final video
    # ─────────────────────────────────────────
    console.print("[bold yellow]🎬 STEP 4: Creating your video...[/bold yellow]\n")

    output_path = composer.compose(
        scenes          = scenes,
        word_timestamps = all_timestamps,
        output_filename = output
    )

    # ─────────────────────────────────────────
    # DONE!
    # ─────────────────────────────────────────
    console.print(Panel(
        f"🎉 [bold green]YOUR VIDEO IS READY![/bold green]\n\n"
        f"📁 File    : [cyan]{output_path}[/cyan]\n"
        f"⏱️  Duration: [yellow]{total_time:.0f} seconds[/yellow]\n"
        f"🎞️  Scenes  : [yellow]{len(scenes)}[/yellow]\n\n"
        f"[green]Open the output folder to find your video![/green]",
        border_style="green"
    ))

    return output_path


if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(description="Auto Video Generator")

    arg_parser.add_argument(
        "--script", "-s",
        type = str,
        help = "Path to your script text file"
    )
    arg_parser.add_argument(
        "--text", "-t",
        type = str,
        help = "Type your script directly here"
    )
    arg_parser.add_argument(
        "--voice", "-v",
        type    = str,
        default = "male_us",
        choices = [
            "male_us",
            "female_us",
            "male_uk",
            "female_uk",
            "male_indian",
            "female_indian"
        ]
    )
    arg_parser.add_argument(
        "--output", "-o",
        type    = str,
        default = "my_video.mp4",
        help    = "Name of the output video file"
    )

    args = arg_parser.parse_args()

    # Get the script text from file or direct input
    if args.script:
        with open(args.script, 'r', encoding='utf-8') as f:
            script = f.read()

    elif args.text:
        script = args.text

    else:
        # Ask user to type script if nothing provided
        console.print("\n[bold cyan]📝 Type or paste your script below.[/bold cyan]")
        console.print("[yellow]Press Enter twice when you are done.[/yellow]\n")
        lines       = []
        empty_count = 0

        while empty_count < 1:
            line = input()
            if line == "":
                empty_count += 1
            else:
                empty_count = 0
                lines.append(line)

        script = "\n".join(lines)

    if not script.strip():
        console.print("[red]❌ No script provided! Please give a script.[/red]")
        sys.exit(1)

    generate_video(
        script_text = script,
        voice       = args.voice,
        output      = args.output
    )
