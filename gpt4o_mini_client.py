import openai
import ast
from dotenv import load_dotenv
import os

from constants import LearningLanguage, LearningLevel


class GPT4oMiniClient:
    """
    constructor to create an object from this class
    """

    def __init__(self):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file.")
        openai.api_key = api_key

        # Use the new OpenAI client
        self.client = openai.OpenAI(api_key=api_key)

    def chat(self, language_native: LearningLanguage, language_to_learn: LearningLanguage,
             language_level: LearningLevel = LearningLevel.EASY, number_of_words=50):
        """
        module to create a list of 50 words to learn in a certain language
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content":
                    "Please return me a dictionary with int as primary key for each word of a "
                    f"list of {number_of_words}. Assume the person is speaking"
                    f" {language_native}, and "
                    f"wants to learn {language_to_learn} and has the following language "
                    f"level: {language_level}."
                    " Please return the list in his native language without translation. Please "
                    "only return the dictionary starting your response with { and ending with }."
                    "PLEASE!."}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

    def string_to_dict(self, dict_string: str) -> dict:
        """
        method to transform the response string to a dictionary
        :return:
        """
        try:
            # Convert the string to a Python dictionary
            python_dict = ast.literal_eval(dict_string)
            return python_dict
        except Exception as e:
            print(f"❌ Error converting string to dict: {e}")
            return None


# Example usage
if __name__ == "__main__":
    client = GPT4oMiniClient()
    for i in range(100):
        response = client.chat("German", "English", "beginner", 5)
        print(client.string_to_dict(response))
        print(response)