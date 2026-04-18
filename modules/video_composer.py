import os
import numpy as np
from moviepy.editor import (
    ImageClip,
    VideoClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips
)
from PIL import Image
from typing import List
from config import Config
from modules.script_parser import Scene
from modules.caption_generator import CaptionGenerator
from modules.image_fetcher import ImageFetcher
from rich.console import Console

console = Console()


class VideoComposer:

    def __init__(self):
        self.caption_gen = CaptionGenerator()
        self.fetcher     = ImageFetcher()
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)

    def compose(
        self,
        scenes:          List[Scene],
        word_timestamps: List[dict],
        output_filename: str = "final_video.mp4"
    ) -> str:

        console.print("\n🎬 [bold green]Building your video...[/bold green]\n")

        all_clips  = []
        directions = ["in", "out", "left", "right"]

        for i, scene in enumerate(scenes):
            console.print(f"  🎞️ Building scene {i+1} of {len(scenes)}")
            console.print(f"  📝 [cyan]{scene.text[:60]}[/cyan]")

            # Resize image to fit video
            self.fetcher.resize_for_video(scene.image_path)

            # Calculate time offset for this scene
            scene_offset = self._get_offset(i, scenes)

            # Get word timestamps for this scene only
            scene_timestamps = [
                t for t in word_timestamps
                if scene_offset <= t["start"] < scene_offset + scene.duration + 0.5
            ]

            # Create image with slow zoom effect
            direction  = directions[i % 4]
            img_clip   = self._ken_burns(scene.image_path, scene.duration, direction)

            # Create caption overlay
            caption_clip = self._make_caption_clip(scene, scene_timestamps, scene_offset)

            # Combine image and caption together
            if caption_clip:
                scene_video = CompositeVideoClip([
                    img_clip,
                    caption_clip
                ]).set_duration(scene.duration)
            else:
                scene_video = img_clip.set_duration(scene.duration)

            # Add voice audio to scene
            if scene.audio_path and os.path.exists(scene.audio_path):
                audio = AudioFileClip(scene.audio_path)
                if audio.duration > scene.duration:
                    audio = audio.subclip(0, scene.duration)
                scene_video = scene_video.set_audio(audio)

            all_clips.append(scene_video)
            console.print(f"  ✅ Scene {i+1} done\n")

        # Join all scenes into one video
        console.print("  🔗 Joining all scenes together...")
        final = concatenate_videoclips(all_clips, method="compose")

        # Save the final video
        output_path = os.path.join(Config.OUTPUT_DIR, output_filename)
        console.print(f"  💾 Saving video to: [cyan]{output_path}[/cyan]")
        console.print("  ⏳ Please wait, this may take a few minutes...\n")

        final.write_videofile(
            output_path,
            fps         = Config.FPS,
            codec       = "libx264",
            audio_codec = "aac",
            logger      = None
        )

        return output_path

    def _get_offset(self, scene_index: int, scenes: List[Scene]) -> float:
        # Calculate start time of this scene in the full video
        offset = 0
        for i in range(scene_index):
            offset += scenes[i].duration
        return offset

    def _ken_burns(self, image_path: str, duration: float, direction: str):
        # Create slow zoom and pan effect on image
        img     = Image.open(image_path).convert("RGB")
        extra   = 200
        img_big = img.resize(
            (Config.VIDEO_WIDTH + extra, Config.VIDEO_HEIGHT + extra),
            Image.LANCZOS
        )
        img_array = np.array(img_big)

        def make_frame(t):
            progress = t / max(duration, 0.1)

            if direction == "in":
                crop_x = int(progress * extra // 2)
                crop_y = int(progress * extra // 2)
            elif direction == "out":
                crop_x = int((1 - progress) * extra // 2)
                crop_y = int((1 - progress) * extra // 2)
            elif direction == "left":
                crop_x = int(progress * extra)
                crop_y = extra // 2
            else:
                crop_x = int((1 - progress) * extra)
                crop_y = extra // 2

            crop_x = max(0, min(crop_x, extra))
            crop_y = max(0, min(crop_y, extra))

            cropped = img_array[
                crop_y : crop_y + Config.VIDEO_HEIGHT,
                crop_x : crop_x + Config.VIDEO_WIDTH
            ]

            if (
                cropped.shape[0] != Config.VIDEO_HEIGHT or
                cropped.shape[1] != Config.VIDEO_WIDTH
            ):
                pil = Image.fromarray(cropped)
                pil = pil.resize((Config.VIDEO_WIDTH, Config.VIDEO_HEIGHT))
                return np.array(pil)

            return cropped

        return VideoClip(make_frame, duration=duration).set_fps(Config.FPS)

    def _make_caption_clip(
        self,
        scene:          Scene,
        timestamps:     list,
        scene_offset:   float
    ) -> VideoClip:

        def make_frame(t):
            absolute_t   = t + scene_offset
            current_word = None

            for ts in timestamps:
                if ts["start"] <= absolute_t <= ts["end"]:
                    current_word = ts["word"]
                    break

            frame = self.caption_gen.make_caption_frame(
                text         = scene.text,
                current_word = current_word
            )
            return frame

        clip = VideoClip(make_frame, duration=scene.duration, ismask=False)
        clip = clip.set_fps(15)
        return clip
