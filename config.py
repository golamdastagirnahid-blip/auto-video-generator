import os

class Config:

    # ─────────────────────────────
    # YOUR FREE API KEYS
    # We will add real keys later
    # ─────────────────────────────
    PEXELS_API_KEY  = "YOUR_PEXELS_KEY_HERE"
    PIXABAY_API_KEY = "YOUR_PIXABAY_KEY_HERE"

    # ─────────────────────────────
    # VIDEO SETTINGS
    # ─────────────────────────────
    VIDEO_WIDTH  = 1920   # Full HD width
    VIDEO_HEIGHT = 1080   # Full HD height
    FPS          = 30     # Frames per second

    # ─────────────────────────────
    # VOICE SETTINGS
    # ─────────────────────────────
    VOICE  = "en-US-ChristopherNeural"
    RATE   = "+0%"
    VOLUME = "+0%"

    # ─────────────────────────────
    # CAPTION SETTINGS
    # ─────────────────────────────
    FONT_PATH    = "assets/fonts/Montserrat-Bold.ttf"
    FONT_SIZE    = 60
    STROKE_WIDTH = 3

    # ─────────────────────────────
    # FOLDERS
    # ─────────────────────────────
    TEMP_DIR   = "temp"
    OUTPUT_DIR = "output"

    # ─────────────────────────────
    # ALL AVAILABLE VOICES
    # ─────────────────────────────
    VOICES = {
        "male_us"      : "en-US-ChristopherNeural",
        "female_us"    : "en-US-JennyNeural",
        "male_uk"      : "en-GB-RyanNeural",
        "female_uk"    : "en-GB-SoniaNeural",
        "male_indian"  : "en-IN-PrabhatNeural",
        "female_indian": "en-IN-NeerjaNeural",
    }
