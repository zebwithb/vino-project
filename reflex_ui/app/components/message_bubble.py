import reflex as rx
from app.states.chat_state import Message, ChatState
from app.components.typing_indicator import typing_indicator


def ai_message_bubble(
    message_text: str, is_last_ai_message: bool
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(
                "bot", size=20, class_name="text-indigo-600"
            ),
            class_name="flex-shrink-0 p-2 bg-indigo-100 rounded-full border border-indigo-200 shadow-sm",
        ),
        rx.el.div(
            rx.cond(
                (message_text == "")
                & is_last_ai_message
                & ChatState.processing,
                typing_indicator(),
                rx.el.p(
                    message_text,
                    class_name="text-sm sm:text-base text-slate-800",
                ),
            ),
            class_name="bg-slate-100 p-3 rounded-xl shadow-sm",
        ),
        class_name="flex items-start gap-3 w-full max-w-2xl",
    )


def user_message_bubble(message_text: str) -> rx.Component:
    return rx.el.div(
        rx.el.p(
            message_text, class_name="text-sm sm:text-base"
        ),
        class_name="bg-sky-500 text-white p-3 rounded-xl shadow-sm ml-auto max-w-[85%]",
    )


def message_display(
    message: Message, index: int
) -> rx.Component:
    is_last_message = (
        index == ChatState.messages.length() - 1
    )
    return rx.el.div(
        rx.cond(
            message["is_ai"],
            ai_message_bubble(
                message["text"], is_last_message
            ),
            user_message_bubble(message["text"]),
        ),
        class_name="w-full flex",
    )