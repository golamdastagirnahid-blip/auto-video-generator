import os
import requests
from PIL import Image, ImageDraw, ImageFont
from config import Config
from rich.console import Console

console = Console()


class ImageFetcher:

    def __init__(self):
        self.pexels_key  = Config.PEXELS_API_KEY
        self.pixabay_key = Config.PIXABAY_API_KEY
        self.temp_dir    = Config.TEMP_DIR
        os.makedirs(self.temp_dir, exist_ok=True)

    def fetch_image(self, query: str, index: int) -> str:
        console.print(f"  🔍 Finding image for: [cyan]{query}[/cyan]")

        # Try Pexels first
        path = self._from_pexels(query, index)

        # Try Pixabay if Pexels fails
        if not path:
            console.print(f"  ⚠️ Pexels failed, trying Pixabay...")
            path = self._from_pixabay(query, index)

        # Try with simpler single word query
        if not path:
            simple = query.split()[0]
            console.print(f"  ⚠️ Trying simpler search: {simple}")
            path = self._from_pexels(simple, index)

        # Make a placeholder image if everything fails
        if not path:
            console.print(f"  ⚠️ No image found, creating placeholder...")
            path = self._make_placeholder(index, query)

        console.print(f"  ✅ Image ready for scene {index}")
        return path

    def _from_pexels(self, query: str, index: int) -> str:
        try:
            url     = "https://api.pexels.com/v1/search"
            headers = {"Authorization": self.pexels_key}
            params  = {
                "query"       : query,
                "per_page"    : 1,
                "orientation" : "landscape"
            }

            r = requests.get(url, headers=headers, params=params, timeout=10)

            if r.status_code == 200:
                data = r.json()
                if data.get("photos"):
                    img_url = data["photos"][0]["src"]["large2x"]
                    return self._download(img_url, index)
        except Exception as e:
            console.print(f"  ❌ Pexels error: {e}")

        return None

    def _from_pixabay(self, query: str, index: int) -> str:
        try:
            url    = "https://pixabay.com/api/"
            params = {
                "key"         : self.pixabay_key,
                "q"           : query,
                "image_type"  : "photo",
                "orientation" : "horizontal",
                "per_page"    : 3
            }

            r = requests.get(url, params=params, timeout=10)

            if r.status_code == 200:
                data = r.json()
                if data.get("hits"):
                    img_url = data["hits"][0]["largeImageURL"]
                    return self._download(img_url, index)
        except Exception as e:
            console.print(f"  ❌ Pixabay error: {e}")

        return None

    def _download(self, url: str, index: int) -> str:
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                path = os.path.join(self.temp_dir, f"scene_{index:04d}.jpg")
                with open(path, 'wb') as f:
                    f.write(r.content)
                return path
        except Exception as e:
            console.print(f"  ❌ Download error: {e}")
        return None

    def _make_placeholder(self, index: int, text: str) -> str:
        # Create a simple colored image with text
        img  = Image.new('RGB', (Config.VIDEO_WIDTH, Config.VIDEO_HEIGHT), color=(20, 30, 80))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(Config.FONT_PATH, 50)
        except:
            font = ImageFont.load_default()

        display = " ".join(text.split()[:5])
        draw.text((100, Config.VIDEO_HEIGHT // 2), display, fill="white", font=font)

        path = os.path.join(self.temp_dir, f"scene_{index:04d}.jpg")
        img.save(path)
        return path

    def resize_for_video(self, image_path: str) -> str:
        # Make image fit the video size perfectly
        img          = Image.open(image_path).convert("RGB")
        target_ratio = Config.VIDEO_WIDTH / Config.VIDEO_HEIGHT
        img_ratio    = img.width / img.height

        if img_ratio > target_ratio:
            new_w = int(img.height * target_ratio)
            left  = (img.width - new_w) // 2
            img   = img.crop((left, 0, left + new_w, img.height))
        else:
            new_h = int(img.width / target_ratio)
            top   = (img.height - new_h) // 2
            img   = img.crop((0, top, img.width, top + new_h))

        img = img.resize((Config.VIDEO_WIDTH, Config.VIDEO_HEIGHT), Image.LANCZOS)
        img.save(image_path, quality=95)
        return image_path
