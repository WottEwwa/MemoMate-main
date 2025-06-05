from collections.abc import Callable

from constants import LearningLevel, LearningLanguage
from db_client import DBClient
from deepl_client import DeepLClient
from gpt4o_mini_client import GPT4oMiniClient
from twilio_client import ConversationStatus, ConversationContext


class UserService:
    def __init__(self, llm: GPT4oMiniClient, deepl: DeepLClient, db: DBClient):
        self._llm = llm
        self._deepl = deepl
        self._db = db

    def create_user(self, sid: str, level: LearningLevel, to_lang: LearningLanguage,
                    from_lang: LearningLanguage = LearningLanguage.DE):
        self._db.create_user(sid, level, to_lang, from_lang)
        print(f"Creating user {sid}")
        print("LEVEL", level)
        print("TO LANG", to_lang)

    def generate_words(self, level: LearningLevel, to_lang: LearningLanguage):
        if not self._db.has_word(to_lang, level):
            answer = self._llm.chat(LearningLanguage.DE, to_lang, level, 10)
            words = self._llm.string_to_dict(answer)
            print(words)
            translated_words = self._deepl.translate_dict(words, target_lang=to_lang)
            print(translated_words)

            for i in words:
                from_word = words.get(i)
                to_word = translated_words.get(i)
                self._db.create_word(from_word, to_word, to_lang, level)

    def authenticate_user(self, context: ConversationContext,
                          handle_message: Callable[[ConversationContext], None]):
        user = self._db.get_user(context.sid)

        if user:
            context.learning_lang = LearningLanguage.from_str(user.get("to_code2"))
            context.learning_level = LearningLevel.from_str(user.get("level_id").upper())
            context.transition_status(to=ConversationStatus.AUTHENTICATED)
            handle_message(context)
        else:
            match context.status:
                case ConversationStatus.UNAUTHENTICATED:
                    context.transition_status(to=ConversationStatus.SELECT_LANG)
                    context.send_message("Sprache wählen")
                case ConversationStatus.SELECT_LANG:
                    self.select_language(context)
                case ConversationStatus.SELECT_LEVEL:
                    self.select_level(context)
                    self.create_user(context.sid, context.learning_level, context.learning_lang)
                    self.generate_words(context.learning_level, context.learning_lang)
                    handle_message(context)

    def select_language(self, context: ConversationContext):
        try:
            context.learning_lang = LearningLanguage.from_str(context.message)
            context.transition_status(to=ConversationStatus.SELECT_LEVEL)
            context.send_message("Level wählen")
        except KeyError:
            context.send_message("Sprache wählen")

    def select_level(self, context: ConversationContext):
        try:
            context.learning_level = LearningLevel.from_str(context.message)
            context.transition_status(to=ConversationStatus.AUTHENTICATED)
        except KeyError:
            context.send_message("Level wählen")
