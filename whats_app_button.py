from typing import List, Optional, Union

class WhatsAppButton:
    """
    Represents a single button in a WhatsApp message.

    Attributes:
        button_number: The unique identifier for the button (1-3).  Twilio requires these to be numbered.
        content: The text displayed on the button.
        reply: The text that is sent back to your application when the user clicks this button.
    """
    def __init__(self, button_number: int, content: str, reply: str):
        if not 1 <= button_number <= 3:
            raise ValueError("button_number must be between 1 and 3")
        self.button_number = button_number
        self.content = content
        self.reply = reply

    def to_dict(self) -> dict:
        """
        Returns the button data in a dictionary format suitable for Twilio's API.
        """
        return {
            f"button": {
                "title": self.content,
                "payload": self.reply
            }
        }


class WhatsAppMessage:
    """
    Represents a complete WhatsApp message with optional header, body, and buttons.
    """
    def __init__(self,
                 to: str,
                 from_whatsapp: str,  # Changed to from_whatsapp
                 body: str,
                 header: Optional[str] = None,
                 buttons: Optional[List[WhatsAppButton]] = None,
                 media_url: Optional[str] = None):
        """
        Initializes a WhatsApp message object.

        Args:
            to: The WhatsApp number of the recipient (including "whatsapp:" prefix).
            from_whatsapp: The WhatsApp number of your Twilio sender (including "whatsapp:" prefix).
            body: The main text content of the message.
            header: Optional header text (displayed above the body).
            buttons: Optional list of WhatsAppButton objects (max 3).
            media_url: Optional URL of media to send (image, video, audio).
        """
        self.to = to
        self.from_whatsapp = from_whatsapp # Changed
        self.body = body
        self.header = header
        self.buttons = buttons
        self.media_url = media_url

        if buttons and len(buttons) > 3:
            raise ValueError("Maximum 3 buttons are allowed in a WhatsApp message")

        if buttons:
            button_numbers = [button.button_number for button in buttons]
            if len(set(button_numbers)) != len(button_numbers):
                raise ValueError("Button numbers must be unique")
            if any(not 1 <= bnum <= 3 for bnum in button_numbers):
                raise ValueError("Button numbers must be between 1 and 3.")



    def to_dict(self) -> dict:
        """
        Returns the entire message payload as a dictionary, ready to be sent to Twilio.
        """
        payload = {
            "from": self.from_whatsapp, # Changed
            "to": self.to,
            "body": self.body,
        }

        if self.header:
            payload["header"] = {"type": "text", "text": self.header}

        if self.buttons:
            payload["action"] = {
                "buttons": [button.to_dict()["button"] for button in self.buttons]
            }

        if self.media_url:
            payload["media_url"] = [self.media_url] # Twilio expects a list for media_url

        return payload

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the WhatsApp message.  Useful for debugging.
        """
        parts = [
            f"To: {self.to}",
            f"From (WhatsApp): {self.from_whatsapp}", # Changed
            f"Body: {self.body}",
        ]
        if self.header:
            parts.append(f"Header: {self.header}")
        if self.buttons:
            button_strings = [f"  {b.button_number}: {b.content} ({b.reply})" for b in self.buttons]
            parts.append(f"Buttons:\n" + "\n".join(button_strings))
        if self.media_url:
            parts.append(f"Media URL: {self.media_url}")
        return "\n".join(parts)



def send_whatsapp_message(message: Union[WhatsAppMessage, dict], twilio_client) -> None:
    """
    Sends a WhatsApp message using the Twilio API.

    Args:
        message:  A WhatsAppMessage object OR a dictionary representing the message payload.
        twilio_client:  Your Twilio client object.  You must have already initialized this.
    """
    if isinstance(message, WhatsAppMessage):
        payload = message.to_dict()
    else:
        payload = message  # Assume it's already a correctly formatted dict

    try:
        twilio_client.messages.create(**payload)  # Use the unpacked payload
        print("WhatsApp message sent successfully!")
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        raise  # Re-raise the exception to be handled by the caller, if needed
        #  Important:  Don't just return None on an error.  This can hide problems.
        #  Consider logging the error, and then either:
        #   1.  Raise the exception (as done here), so the caller knows it failed.
        #   2.  Return an error object (e.g., a tuple like (False, "Error message")).



if __name__ == "__main__":
    # Your Twilio Account SID and Auth Token
    account_sid = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # Replace with your SID
    auth_token = "your_auth_token"  # Replace with your auth token
    from twilio.rest import Client
    client = Client(account_sid, auth_token)

    # Your Twilio WhatsApp number (the number you send *from*, including "whatsapp:")
    from_whatsapp_number = "whatsapp:+12345678901"  # Replace with your Twilio WhatsApp number

    # Recipient's WhatsApp number (the number you send *to*, including "whatsapp:")
    to_whatsapp_number = "whatsapp:+491234567890"  # Replace with recipient's WhatsApp number

    # Create some buttons
    button1 = WhatsAppButton(button_number=1, content="Show Order", reply="order123")
    button2 = WhatsAppButton(button_number=2, content="My Profile", reply="profile456")
    button3 = WhatsAppButton(button_number=3, content="Contact Support", reply="support789")

    # Create a WhatsApp message with buttons
    message_with_buttons = WhatsAppMessage(
        to=to_whatsapp_number,
        from_whatsapp=from_whatsapp_number,
        body="Choose an option:",
        header="Welcome to My Shop",
        buttons=[button1, button2, button3],
        media_url="https://www.example.com/image.jpg"  # Optional media URL
    )

    print("Message with buttons:")
    print(message_with_buttons)

    # Send the message with buttons
    send_whatsapp_message(message_with_buttons, client)

    # Create a simple text message (without buttons)
    simple_message = WhatsAppMessage(
        to=to_whatsapp_number,
        from_whatsapp=from_whatsapp_number,
        body="Hello! This is a test message."
    )
    print("\nSimple text message:")
    print(simple_message)
    send_whatsapp_message(simple_message, client)

    # Example of sending a pre-constructed dictionary (for demonstration)
    dict_message = {
        "from": from_whatsapp_number,
        "to": to_whatsapp_number,
        "body": "This message is sent from a dictionary.",
    }
    send_whatsapp_message(dict_message, client)
