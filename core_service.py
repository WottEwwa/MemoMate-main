from game_service import GameService
from twilio_client import ConversationStatus, ConversationContext
from user_service import UserService
import user_messages


class CoreService:
    def __init__(self, user_service: UserService, game_service: GameService):
        self._user_service = user_service
        self._game_service = game_service

    def handle_message(self, context: ConversationContext):
        if context.is_authenticating():
            self._user_service.authenticate_user(context, self.handle_message)
        elif context.is_playing():
            self._game_service.play_game(context)
        elif context.message.startswith("!"):
            self.handle_command(context, context.message[1:])
        else:
            context.send_message(user_messages.UNKNOWN)
            print(f"Nachricht erhalten: {context.message}")

    def handle_command(self, context: ConversationContext, command: str):
        match command:
            case "start":
                if not context.is_playing() and not context.is_authenticating():
                    context.transition_status(to=ConversationStatus.UNAUTHENTICATED)
                    self.handle_message(context)
                    print("Lernsession gestartet.")
                elif context.is_playing():
                    context.send_message("Die Lernsession ist bereits aktiv. Schreib '!stop' um sie zu beenden.")
                else:
                    context.send_message("Bitte schließe zuerst die aktuelle Einrichtung ab.")
            case "stop":
                if context.is_playing():
                    context.transition_status(to=ConversationStatus.INACTIVE)
                    context.current_exercise = None
                    context.send_message(user_messages.STOP_MESSAGE)
                    print("Lernsession beendet.")
                else:
                    context.send_message("Es ist leider aktuell keine aktive Lernsession vorhanden.")
            case "lang":
                # Hier fehlt die Logik zur Sprachänderung.
                context.send_message(user_messages.LANGUAGE_PROMPT)
            case "help":
                context.send_message(user_messages.HELP_PROMPT)
                print("Hilfe angezeigt.")
            case _:
                context.send_message(user_messages.UNKNOWN)
                print(f"Unbekannter Befehl: {command}")