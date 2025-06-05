import requests
from requests.exceptions import RequestException
from constants import LearningLevel, LearningLanguage


class DBClient:
    def __init__(self, base_url):
        self._base_url = f"http://{base_url}"

    def create_user(
            self,
            sid: str,
            level: LearningLevel,
            to_lang: LearningLanguage,
            from_lang: LearningLanguage = LearningLanguage.DE
    ) -> None:
        try:
            url = f"{self._base_url}/users/create"
            payload = {
                "user_id": sid,
                "user_name": "",
                "level_id": level.__repr__().lower(),
                "from_code2": from_lang.code(),
                "to_code2": to_lang.code(),
            }
            response = requests.post(url, json=payload)
            response.raise_for_status()
        except RequestException as e:
            #print(response.json())
            print(f"Error creating user: {e}")
            raise e

    def get_user(self, sid) -> dict:
        try:
            url = f"{self._base_url}/users/{sid}"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            return None
        except RequestException as e:
            print(f"Error getting user {sid}: {e}")
            raise e

    def create_word(self, from_word: str, to_word: str, lang: LearningLanguage,
                    level: LearningLevel) -> None:
        try:
            url = f"{self._base_url}/words/create/"
            payload = {
                "level_id": level.__repr__().lower(),
                "de": from_word,
                "en": None,
                "es": None,
                "ua": None,
                "ru": None,
            }
            payload[lang.code().lower()] = to_word
            response = requests.post(url, json=payload)
            response.raise_for_status()
        except RequestException as e:
            #print(response.json())
            print(f"Error creating word: {e}")
            raise e

    #def update_word(self, from_word: str, new_word: str, level: LearningLevel) -> None:
    #    try:
    #        url = f"{self._base_url}/words/update/{from_word}"
    #        response = requests.patch(url, json=new_word)
    #        response.raise_for_status()
    #    except RequestException as e:
    #        print(f"Error updating word '{from_word}': {e}")
    #        raise e

    def has_word(self, lang: LearningLanguage, level: LearningLevel) -> bool:
        try:
           url = f"{self._base_url}/words/translation/{lang.code().lower()}/{level.__repr__().lower()}"
           response = requests.get(url)
           response.raise_for_status()
           return response.json().get("has_translation")
        except RequestException as e:
            if response.status_code == 404:
                return False
            print(f"Error checking translation for {lang.code()}': {e}")
            raise e

    def get_words(self, lang: LearningLanguage, level: LearningLevel) -> list[dict]:
        try:
            url = f"{self._base_url}/words/random/{lang.code().lower()}"
            response = requests.get(url)
            response.raise_for_status()
            return [response.json()]
        except RequestException as e:
            print(response.json())
            print(f"Error getting random word in '{lang.code()}': {e}")
            raise e

    def increase_progress(self, sid: str, word_id: str) -> None:
        try:
            url = f"{self._base_url}/words/update_correct_count/{sid}/{word_id}"
            response = requests.post(url)
            response.raise_for_status()
        except RequestException as e:
            print(f"Error increasing progress for user '{sid}' and word '{word_id}': {e}")
            raise e
