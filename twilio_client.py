import time
from collections.abc import Callable
from enum import Enum
from datetime import datetime, timezone
from twilio.rest import Client
from twilio.rest.conversations.v1.service.conversation import ConversationInstance

from constants import LearningLanguage, LearningLevel


class ConversationStatus(Enum):
    UNKNOWN = 0
    UNAUTHENTICATED = 1
    AUTHENTICATED = 2
    SELECT_LANG = 3
    SELECT_LEVEL = 4
    INACTIVE = 5


class ConversationContext:
    def __init__(self, conversation: ConversationInstance):
        self.sid: str = conversation.sid
        self.conversation: ConversationInstance = conversation
        self.status = ConversationStatus.UNKNOWN
        self.learning_lang: LearningLanguage | None = None
        self.learning_level: LearningLevel | None = None
        self.message: str | None = None
        self.current_exercise: dict | None = None

    def send_message(self, text: str):
        self.conversation.messages.create(author=TwilioClient.SYS_USERNAME, body=text)

    def transition_status(self, *, to: ConversationStatus):
        self.status = to

    def is_authenticating(self):
        authenticating_states = [
            ConversationStatus.UNAUTHENTICATED,
            ConversationStatus.SELECT_LANG,
            ConversationStatus.SELECT_LEVEL
        ]

        return self.status in authenticating_states

    def is_playing(self):
        playing_states = [ConversationStatus.AUTHENTICATED]
        return self.status in playing_states


class TwilioClient:
    SYS_USERNAME = "ms-hackathons"
    POLL_INTERVAL = 3

    def __init__(self, *, account_sid: str, api_key: str, api_secret: str,
                 conversation_service_id: str):
        self._conversation_service_id: str = conversation_service_id
        self._client: Client = Client(api_key, api_secret, account_sid)
        self._message_handler: Callable[[ConversationContext], None] | None = None
        self._command_handler: Callable[[ConversationContext, str], None] | None = None
        self._interrupt: bool = False
        self._conversation_contexts: dict[str, ConversationContext] = {}

    def start_polling(self):
        if not self._message_handler or not self._command_handler:
            raise AttributeError(
                "Message handler & command handler must be defined before start polling"
            )

        print(f"Started polling new messages every {TwilioClient.POLL_INTERVAL} seconds...")
        last_poll = datetime.now(tz=timezone.utc).replace(microsecond=0) # TODO: Time server

        while not self._interrupt:
            for conversation in self.__get_conversations():
                if conversation.sid not in self._conversation_contexts:
                    self.__create_conversation_context(conversation)

                messages = conversation.messages.list()
                user_messages = [message for message in messages if
                                 message.author != TwilioClient.SYS_USERNAME]

                for message in user_messages:
                    if message.date_created >= last_poll:
                        message_text = message.body

                        if not message_text:
                            continue

                        conversation_context = self._conversation_contexts[conversation.sid]
                        conversation_context.message = message_text

                        if message_text.startswith("!"):
                            self._command_handler(conversation_context, message_text[1:])
                        else:
                            self._message_handler(conversation_context)

            last_poll = datetime.now(tz=timezone.utc).replace(microsecond=0) # TODO: Time server
            time.sleep(TwilioClient.POLL_INTERVAL)

        print(f"Stopped polling")

    def stop_polling(self):
        # TODO: make polling async to make this work
        # TODO: maybe update conversation states
        self._interrupt = True

    def on_message(self, message_handler: Callable[[ConversationContext], None]):
        self._message_handler = message_handler

    def on_command(self, command_handler: Callable[[ConversationContext, str], None]):
        self._command_handler = command_handler

    def __create_conversation_context(self, conversation: ConversationInstance):
        sid = conversation.sid
        self._conversation_contexts[sid] = ConversationContext(conversation)

    def __get_conversations(self):
        return self.__get_service().conversations.list()

    def __get_service(self):
        return self._client.conversations.v1.services(self._conversation_service_id)
