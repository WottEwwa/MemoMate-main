import random
from db_client import DBClient
from twilio_client import ConversationContext


class GameService:
    def __init__(self, db: DBClient):
        self._db = db

    def play_game(self, context: ConversationContext):
        sid = context.sid
        current_word = context.current_exercise

        if current_word:
            wid = current_word.get("word_id")
            to_word = current_word.get("translation")

            if self.check_answer(context.message, to_word):
                self._db.increase_progress(sid, wid)
                context.send_message("Correct")
            else:
                context.send_message(f"Incorrect. The correct answer is {to_word}")

        new_word = self.get_random_word(context)
        context.current_exercise = new_word
        context.send_message(f"How to say {new_word.get('de')} in {context.learning_lang}")

    def check_answer(self, user_answer: str, correct_answer: str) -> bool:
        user_answer = user_answer.strip().lower()
        correct_answer = correct_answer.strip().lower()

        if user_answer == correct_answer:
            return True
        else:
            return False

    def get_random_word(self, context: ConversationContext) -> dict:
        words = self._db.get_words(context.learning_lang, context.learning_level)
        return random.choice(words)
