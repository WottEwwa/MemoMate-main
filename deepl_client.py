import requests
from dotenv import load_dotenv
import os

from constants import LearningLanguage


class DeepLClient:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("DEEPL_API_KEY")
        if not api_key:
            raise ValueError("DEEPL_API_KEY not found in .env file.")
        self.api_key = api_key
        self.api_url = "https://api-free.deepl.com/v2/translate"

    def translate_text(self, text: str, *, target_lang: LearningLanguage,
                       source_lang: LearningLanguage = LearningLanguage.DE) -> str:
        """Translate a single string"""
        response = requests.post(
            self.api_url,
            data={
                "auth_key": self.api_key,
                "text": text,
                "source_lang": source_lang.code(),
                "target_lang": target_lang.code()
            }
        )
        response.raise_for_status()
        return response.json()["translations"][0]["text"]

    def translate_dict(self, data: dict, *, target_lang: LearningLanguage,
                       source_lang: LearningLanguage = LearningLanguage.DE) -> dict:
        """Translate all values in a dictionary while preserving keys"""
        translated = {}
        for key, value in data.items():
            translated[key] = self.translate_text(
                value, target_lang=target_lang, source_lang=source_lang
            )
        return translated


def main():
    # Sample dictionary (German → English)
    word_dict = {1: 'Haus', 2: 'Auto', 3: 'Baum', 4: 'Katze', 5: 'Hund', 6: 'Buch', 7: 'Stuhl',
                 8: 'Tisch', 9: 'Wasser', 10: 'Licht'}

    # Create the DeepL client
    client = DeepLClient()

    # Translate the dictionary
    translated_dict = client.translate_dict(word_dict)

    # Print the translated result
    print(translated_dict)


if __name__ == "__main__":
    main()
