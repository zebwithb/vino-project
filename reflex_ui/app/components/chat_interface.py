import reflex as rx
from app.states.chat_state import ChatState
from app.components.message_bubble import message_display
from app.components.input_area import input_area


def chat_interface() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.cond(
                len(ChatState.messages) == 0,
                rx.el.div(
                    rx.foreach(
                        ChatState.messages, message_display
                    ),
                    class_name="flex flex-col gap-4 p-4 md:p-6 flex-grow overflow-y-auto",
                ),
            ),
            class_name="flex-grow flex flex-col justify-center items-center overflow-hidden",
        ),
        input_area(),
        class_name="h-screen flex flex-col bg-slate-100 font-['Inter']",
    )