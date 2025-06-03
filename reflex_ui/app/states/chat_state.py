import reflex as rx
from typing import List, TypedDict
import asyncio
from openai import OpenAI
import os


class Message(TypedDict):
    text: str
    is_ai: bool


class ChatState(rx.State):
    messages: List[Message] = []
    processing: bool = False
    input_message: str = ""

    @rx.event
    def clear_messages(self):
        self.messages = []
        self.processing = False
        self.input_message = ""

    @rx.event
    def send_message_from_input(self):
        if (
            self.processing
            or not self.input_message.strip()
        ):
            return
        message_text = self.input_message.strip()
        self.messages.append(
            {"text": message_text, "is_ai": False}
        )
        self.messages.append({"text": "", "is_ai": True})
        self.processing = True
        self.input_message = ""
        return ChatState.generate_response

    @rx.event
    def send_preset_message(self, preset_text: str):
        if self.processing:
            return
        self.messages.append(
            {"text": preset_text, "is_ai": False}
        )
        self.messages.append({"text": "", "is_ai": True})
        self.processing = True
        return ChatState.generate_response

## TODO Check if this is needed with GEMINI, change?
    @rx.event(background=True)
    async def generate_response(self):
        if not os.getenv("OPENAI_API_KEY"):
            async with self:
                self.messages[-1][
                    "text"
                ] = "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
                self.processing = False
            return
        try:
            client = OpenAI()
            prepared_messages = [
                {
                    "role": "system",
                    "content": "You are a friendly and helpful AI assistant.",
                }
            ]
            for msg in self.messages[:-1]:
                role = (
                    "assistant" if msg["is_ai"] else "user"
                )
                prepared_messages.append(
                    {"role": role, "content": msg["text"]}
                )
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=prepared_messages,
                stream=True,
            )
            current_ai_response = ""
            for chunk in stream:
                if not self.processing:
                    break
                if (
                    chunk.choices[0].delta
                    and chunk.choices[0].delta.content
                ):
                    current_ai_response += chunk.choices[
                        0
                    ].delta.content
                    async with self:
                        if self.messages:
                            self.messages[-1][
                                "text"
                            ] = current_ai_response
        except Exception as e:
            async with self:
                self.messages[-1][
                    "text"
                ] = f"An error occurred: {str(e)}"
        finally:
            async with self:
                self.processing = False