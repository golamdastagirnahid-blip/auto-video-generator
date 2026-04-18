import numpy as np
from PIL import Image, ImageDraw, ImageFont
from config import Config
from rich.console import Console

console = Console()


class CaptionGenerator:

    def __init__(self):
        # Try to load custom font
        try:
            self.font = ImageFont.truetype(Config.FONT_PATH, Config.FONT_SIZE)
            console.print("✅ Custom font loaded successfully")
        except:
            self.font = ImageFont.load_default()
            console.print("⚠️ Using default font")

    def make_caption_frame(
        self,
        text:         str,
        current_word: str = None
    ) -> np.ndarray:

        # Create transparent image same size as video
        img  = Image.new('RGBA', (Config.VIDEO_WIDTH, Config.VIDEO_HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Wrap long text into multiple lines
        lines = self._wrap(text, draw, Config.VIDEO_WIDTH - 200)

        # Calculate height of one line
        test_bbox = draw.textbbox((0, 0), "A", font=self.font)
        line_h    = test_bbox[3] - test_bbox[1]
        gap       = 15

        total_h = len(lines) * (line_h + gap)

        # Place captions near bottom of screen
        start_y = Config.VIDEO_HEIGHT - total_h - 120

        for li, line in enumerate(lines):
            line_bbox = draw.textbbox((0, 0), line, font=self.font)
            line_w    = line_bbox[2] - line_bbox[0]
            x         = (Config.VIDEO_WIDTH - line_w) // 2
            y         = start_y + li * (line_h + gap)

            # Draw dark background box behind text
            pad = 18
            box = [
                x - pad,
                y - pad // 2,
                x + line_w + pad,
                y + line_h + pad // 2
            ]
            self._rounded_box(draw, box, fill=(0, 0, 0, 170))

            # Draw each word one by one
            word_x = x
            for word in line.split():
                wb     = draw.textbbox((0, 0), word + " ", font=self.font)
                word_w = wb[2] - wb[0]

                # Check if this word is currently being spoken
                is_highlighted = (
                    current_word is not None and
                    word.lower().strip(".,!?;:") ==
                    current_word.lower().strip(".,!?;:")
                )

                if is_highlighted:
                    # Draw yellow highlight box behind word
                    hbox = [
                        word_x - 4,
                        y - 2,
                        word_x + word_w - 4,
                        y + line_h + 2
                    ]
                    self._rounded_box(draw, hbox, fill=(255, 220, 0, 230))

                    # Draw word in black color on yellow
                    draw.text(
                        (word_x, y),
                        word + " ",
                        fill  = (0, 0, 0, 255),
                        font  = self.font
                    )

                else:
                    # Draw white word with black outline
                    sw = 2
                    for dx in range(-sw, sw + 1):
                        for dy in range(-sw, sw + 1):
                            draw.text(
                                (word_x + dx, y + dy),
                                word + " ",
                                fill = (0, 0, 0, 255),
                                font = self.font
                            )
                    draw.text(
                        (word_x, y),
                        word + " ",
                        fill = (255, 255, 255, 255),
                        font = self.font
                    )

                word_x += word_w

        return np.array(img)

    def _wrap(self, text: str, draw, max_w: int) -> list:
        # Break text into lines that fit the screen
        words   = text.split()
        lines   = []
        current = []

        for word in words:
            current.append(word)
            line_text = " ".join(current)
            bbox      = draw.textbbox((0, 0), line_text, font=self.font)

            if bbox[2] - bbox[0] > max_w:
                if len(current) > 1:
                    current.pop()
                    lines.append(" ".join(current))
                    current = [word]
                else:
                    lines.append(line_text)
                    current = []

        if current:
            lines.append(" ".join(current))

        return lines

    def _rounded_box(self, draw, coords, fill, radius=12):
        # Draw a box with rounded corners
        x1, y1, x2, y2 = coords
        r               = radius

        draw.rectangle([x1 + r, y1,      x2 - r, y2     ], fill=fill)
        draw.rectangle([x1,     y1 + r,  x2,     y2 - r ], fill=fill)
        draw.pieslice( [x1,     y1,      x1+2*r, y1+2*r ], 180, 270, fill=fill)
        draw.pieslice( [x2-2*r, y1,      x2,     y1+2*r ], 270, 360, fill=fill)
        draw.pieslice( [x1,     y2-2*r,  x1+2*r, y2     ], 90,  180, fill=fill)
        draw.pieslice( [x2-2*r, y2-2*r,  x2,     y2     ], 0,   90,  fill=fill)
