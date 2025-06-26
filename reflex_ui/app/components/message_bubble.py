import reflex as rx
from app.states.chat_state import Message, ChatState
from app.components.typing_indicator import typing_indicator


def ai_message_display(message_text: str, is_last_ai_message: bool) -> rx.Component:
    return rx.el.div(
        rx.cond(
            (message_text == "")
            & is_last_ai_message
            & ChatState.processing,
            typing_indicator(),
            rx.el.p(
                rx.markdown(message_text),
                class_name="text-sm sm:text-base text-slate-800",
            ),
        ),
        class_name="w-full max-w-2xl",
    )


def user_message_bubble(message_text: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(
                message_text, 
                class_name="text-sm sm:text-base text-slate-800 text-right",
            ),
            class_name="p-3 rounded-xl shadow-sm",
            style={"background_color": "#f0f0f0", "min_width": "150px", "max_width": "80%"},
        ),
        class_name="flex items-start gap-3 w-full max-w-2xl justify-end",
        style={"min_width": "20%"},
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
            ai_message_display(
                message["text"], is_last_message
            ),
            user_message_bubble(message["text"]),
        ),
        class_name=rx.cond(
            message["is_ai"],
            "w-full flex justify-start mb-4",
            "w-full flex justify-end mb-4",
        ),
    )