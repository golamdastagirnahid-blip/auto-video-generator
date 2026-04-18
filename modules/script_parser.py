import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from dataclasses import dataclass, field
from typing import List

# Download required data automatically
nltk.download('punkt',                        quiet=True)
nltk.download('punkt_tab',                    quiet=True)
nltk.download('stopwords',                    quiet=True)
nltk.download('averaged_perceptron_tagger',   quiet=True)
nltk.download('averaged_perceptron_tagger_eng', quiet=True)


@dataclass
class Scene:
    index:        int
    text:         str
    keywords:     List[str] = field(default_factory=list)
    search_query: str       = ""
    duration:     float     = 0.0
    image_path:   str       = ""
    audio_path:   str       = ""


class ScriptParser:

    def __init__(self):
        self.stop_words = set(stopwords.words('english'))

    def parse(self, script_text: str) -> List[Scene]:
        # Break script into sentences
        sentences = sent_tokenize(script_text)
        scenes    = []

        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue

            keywords     = self._get_keywords(sentence)
            search_query = " ".join(keywords[:4]) if keywords else sentence[:30]

            scene = Scene(
                index        = i,
                text         = sentence,
                keywords     = keywords,
                search_query = search_query
            )
            scenes.append(scene)

        return scenes

    def _get_keywords(self, sentence: str) -> List[str]:
        words = word_tokenize(sentence.lower())

        # Remove common words like "the", "is", "a" etc
        keywords = [
            w for w in words
            if w.isalnum()
            and w not in self.stop_words
            and len(w) > 2
        ]

        return keywords[:6]
