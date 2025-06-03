import reflex as rx
from app.states.chat_state import ChatState


def input_area() -> rx.Component:
    return rx.el.div(
        rx.el.form(
            rx.el.div(
                rx.el.textarea(
                    default_value=ChatState.input_message,
                    placeholder="Type your message...",
                    on_change=ChatState.set_input_message,
                    class_name="flex-grow p-3 bg-white border border-slate-300 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-sky-400 min-h-[48px] max-h-40 text-slate-800 placeholder-slate-400",
                ),
                rx.el.button(
                    rx.cond(
                        ChatState.processing,
                        rx.icon(
                            "loader-circle",
                            class_name="animate-spin",
                            size=20,
                        ),
                        rx.icon("send-horizontal", size=20),
                    ),
                    type="submit",
                    disabled=ChatState.processing
                    | (
                        ChatState.input_message.strip()
                        == ""
                    ),
                    class_name="p-3 bg-sky-500 text-white rounded-xl hover:bg-sky-600 focus:outline-none focus:ring-2 focus:ring-sky-400 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors",
                ),
                class_name="flex items-end gap-2",
            ),
            on_submit=ChatState.send_message_from_input,
            reset_on_submit=False,
            class_name="w-full",
        ),
        rx.cond(
            ChatState.messages.length() > 0,
            rx.el.button(
                rx.icon(
                    "trash-2", size=16, class_name="mr-1.5"
                ),
                "Clear Chat",
                on_click=ChatState.clear_messages,
                class_name="mt-2 text-xs text-slate-500 hover:text-red-500 flex items-center transition-colors",
                variant="ghost",
            ),
        ),
        class_name="sticky bottom-0 left-0 right-0 p-4 bg-slate-50/80 backdrop-blur-md border-t border-slate-200 flex flex-col items-center",
    )