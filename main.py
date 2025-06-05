import os
from dotenv import load_dotenv

from db_client import DBClient
from deepl_client import DeepLClient
from gpt4o_mini_client import GPT4oMiniClient
from user_service import UserService
from game_service import GameService
from core_service import CoreService
from twilio_client import TwilioClient

load_dotenv()


def main():
    fast_url = os.getenv("FAST_URL")
    fast_port = os.getenv("FAST_PORT")
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    api_sid = os.getenv("TWILIO_API_KEY")
    api_secret = os.getenv("TWILIO_API_SECRET")
    conversation_service_id = os.getenv("TWILIO_CONVERSATION_SERVICE_SID")

    gpt4o = GPT4oMiniClient()
    deepl = DeepLClient()
    db_client = DBClient(f"{fast_url}:{fast_port}")
    user_service = UserService(gpt4o, deepl, db_client)
    game_service = GameService(db_client)
    core_service = CoreService(user_service, game_service)

    twilio_client = TwilioClient(
        account_sid=account_sid,
        api_key=api_sid,
        api_secret=api_secret,
        conversation_service_id=conversation_service_id
    )

    twilio_client.on_message(core_service.handle_message)
    twilio_client.on_command(core_service.handle_command)
    twilio_client.start_polling()


if __name__ == '__main__':
    main()
